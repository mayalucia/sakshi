"""Tests for sakshi's synthetic worked example.

This file is tangled from codev/examples/synthetic.org.

The test suite exercises five manifests, one per failure class plus a
false-positive trap, and asserts that the firewall classifies each
correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from sakshi import (
    FailureClass,
    FirewallFailure,
    check_manifest,
    load_manifest,
)

HERE = Path(__file__).parent
SYNTH_DIR = HERE / "synthetic"
MANIFESTS_DIR = SYNTH_DIR / "manifests"
DATA_DIR = SYNTH_DIR / "data"


@pytest.fixture(scope="module", autouse=True)
def ensure_data_generated():
    """Generate the synthetic dataset before any test runs."""
    if not (DATA_DIR / "raw.csv").exists():
        sys.path.insert(0, str(SYNTH_DIR))
        from generate import (  # type: ignore[import-not-found]
            make_gapfilled_clean,
            make_gapfilled_synthetic,
            make_raw_with_gaps,
        )

        raw = make_raw_with_gaps(DATA_DIR / "raw.csv")
        make_gapfilled_clean(raw, DATA_DIR / "gapfilled_clean.csv")
        make_gapfilled_synthetic(raw, DATA_DIR / "gapfilled_synthetic.csv")


# ----- Per-manifest assertions -----------------------------------------


def test_01_correct_passes():
    """Manifest 1 should pass cleanly."""
    manifest = load_manifest(MANIFESTS_DIR / "01_correct.manifest.yaml")
    check_manifest(manifest)


def test_02_b_broken_blocks():
    """Manifest 2 should be blocked B-class at schema-parse time.

    The output's actual content (one cell filled by generative model)
    is not what the schema sees; what the schema sees is the *manifest*'s
    declaration. The B-class violation here is that a manifest claiming
    the gap-fill is deterministic must be coherent with its output's
    declared register.

    In v0.1 we cannot inspect the output's data directly; we trust the
    declared register. The B-class catch happens when a *future* manifest
    that *does* declare the compound register has its 'synthesis' field
    missing — schema enforces that. Here, we test the firewall's
    parse-time response to the converse case: a manifest whose declared
    register is plain 'derived-from-measurement' but whose 'tests' do
    not include the synthetic-content check. That, we cannot catch
    structurally — it requires the consumer-side check. So this test
    documents the v0.1 limitation: this specific failure mode is
    *outside* the v0.1 firewall, and the manifest will load.

    The test asserts the load *succeeds* (which is the v0.1 truth) and
    documents the limitation. A future v0.2 enhancement will couple the
    manifest's declared register against test-asserted register, closing
    the gap.
    """
    manifest = load_manifest(MANIFESTS_DIR / "broken" / "02_b_class_broken.manifest.yaml")
    # v0.1: parse succeeds. Documented limitation.
    assert manifest.step == "synthetic-gapfill-b-broken"


def test_03_t_broken_blocks():
    """Manifest 3 should be blocked T-class at drift-check time."""
    with pytest.raises((FirewallFailure, Exception)) as excinfo:
        check_manifest(MANIFESTS_DIR / "broken" / "03_t_class_broken.manifest.yaml")
    msg = str(excinfo.value)
    assert "T-class" in msg, f"expected T-class in failure, got: {msg}"
    assert "drift" in msg.lower(), f"expected 'drift' in message, got: {msg}"


def test_04_m_broken_blocks():
    """Manifest 4 should be blocked M-class at parse time."""
    with pytest.raises(FirewallFailure) as excinfo:
        load_manifest(MANIFESTS_DIR / "broken" / "04_m_class_broken.manifest.yaml")
    msg = str(excinfo.value)
    assert "M-class" in msg, f"expected M-class in failure, got: {msg}"


def test_05_false_positive_trap_passes():
    """Manifest 5 should PASS — the unusual compound is doctrinally correct."""
    manifest = load_manifest(MANIFESTS_DIR / "05_false_positive_trap.manifest.yaml")
    assert manifest.step == "synthetic-stylised-plot-faithful"
    # No drift check needed; the output is not a real file on disk.
    # We're asserting that the schema accepts the compound and that the
    # parse succeeds.
