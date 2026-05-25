"""Tests for sakshi's IMIS worked example.

This file is tangled from codev/examples/imis.org.

The test suite walks a three-step IMIS workflow (raw import → gap-fill
→ daily aggregate) and asserts the firewall behaviour at each step.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sakshi import (
    FirewallFailure,
    check_manifest,
    load_manifest,
)

HERE = Path(__file__).parent
IMIS_DIR = HERE / "imis"
MANIFESTS_DIR = IMIS_DIR / "manifests"
DATA_DIR = IMIS_DIR / "data"


@pytest.fixture(scope="module", autouse=True)
def ensure_surrogate():
    if not (DATA_DIR / "imis_wfj_flu_2024-02.csv").exists():
        sys.path.insert(0, str(IMIS_DIR))
        from generate_imis_surrogate import make_surrogate  # type: ignore[import-not-found]

        make_surrogate(DATA_DIR / "imis_wfj_flu_2024-02.csv")


# ----- Manifest-only checks --------------------------------------------


def test_01_raw_import_manifest_loads():
    """Raw-import manifest is doctrinally clean and loads."""
    manifest = load_manifest(MANIFESTS_DIR / "01_imis_raw_import.manifest.yaml")
    assert manifest.step == "imis-raw-import-wfj-flu-2024-02"
    check_manifest(manifest)


def test_02_gapfill_manifest_loads_with_compound_register():
    """Gap-fill manifest demonstrates the compound register accepted."""
    manifest = load_manifest(MANIFESTS_DIR / "02_imis_gapfill.manifest.yaml")
    out = manifest.outputs[0]
    regs = out.register if isinstance(out.register, list) else [out.register]
    reg_values = [r.value for r in regs]
    assert "derived-from-measurement" in reg_values
    assert "synthetic-acknowledged" in reg_values
    assert out.derivation is not None
    assert out.synthesis is not None


def test_03_daily_aggregate_manifest_inherits_compound():
    """Daily-aggregate manifest preserves the compound through aggregation."""
    manifest = load_manifest(MANIFESTS_DIR / "03_imis_daily_aggregate.manifest.yaml")
    out = manifest.outputs[0]
    regs = out.register if isinstance(out.register, list) else [out.register]
    reg_values = [r.value for r in regs]
    assert "synthetic-acknowledged" in reg_values, (
        "Aggregation must preserve synthesis ancestry — collapsing here would"
        " be a silent demotion."
    )


# ----- Pipeline-content checks (informational, not firewall) -----------
# These tests describe what the pipeline *would do* if implemented;
# they assert properties of the manifests, not of executed code. v0.2
# will couple the manifests' tests entries to executed pipeline runs
# via dmt-eval's test-plugin domain machinery; for v0.1, manifest
# self-consistency is sufficient.


def test_raw_csv_has_expected_shape():
    """The surrogate CSV has the right columns and row count."""
    df = pd.read_csv(DATA_DIR / "imis_wfj_flu_2024-02.csv")
    assert list(df.columns) == ["station_id", "timestamp_utc", "air_temp_c", "qc_flag"]
    assert (df["station_id"] == "WFJ").sum() == 48
    assert (df["station_id"] == "FLU").sum() == 48
    # FLU has a 6-hour gap (indices 12-17 in the FLU partition).
    flu = df[df["station_id"] == "FLU"].reset_index(drop=True)
    assert flu.loc[12:17, "air_temp_c"].isna().all()


def test_qc_flag_vocabulary_matches_imis():
    """The QC flag vocabulary matches the IMIS standard (0, 1, 9)."""
    df = pd.read_csv(DATA_DIR / "imis_wfj_flu_2024-02.csv")
    flags = set(df["qc_flag"].unique())
    assert flags.issubset({0, 1, 9}), (
        f"qc_flag vocabulary deviates from IMIS standard: {flags}"
    )
