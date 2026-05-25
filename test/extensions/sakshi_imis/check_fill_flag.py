"""sakshi_imis — IMIS-specific extension checks.

Adds: per-row fill_flag convention.

Usage:
    pytest --sakshi-imis-check-fill-flag

This is a worked example of how to add a domain extension. In a real
project, this file would live in its own package (sakshi_imis), not
inside sakshi's test/ tree.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from sakshi import FailureClass, FirewallFailure, load_manifest


def check_imis_fill_flag(manifest_path: Path) -> None:
    """For any IMIS gap-fill manifest, the output must have a fill_flag column.

    Recognised as an IMIS gap-fill by:
    - step name containing 'imis' and 'gapfill', OR
    - any output with a derivation containing 'interpolation'
    """
    manifest = load_manifest(manifest_path)

    is_imis_gapfill = (
        "imis" in manifest.step.lower()
        and "gapfill" in manifest.step.lower()
    )
    has_interpolation_derivation = any(
        (out.derivation or "").find("interpolation") >= 0
        for out in manifest.outputs
    )
    if not (is_imis_gapfill or has_interpolation_derivation):
        return  # Not an IMIS gap-fill; nothing to check.

    base = manifest_path.parent
    for out in manifest.outputs:
        path = base / out.id
        if not path.exists() or path.suffix not in (".csv", ".parquet"):
            continue
        df = (
            pd.read_csv(path) if path.suffix == ".csv" else pd.read_parquet(path)
        )
        if "fill_flag" not in df.columns:
            raise FirewallFailure(
                FailureClass.MISSED,
                f"output {out.id!r} is an IMIS gap-fill product but has no "
                f"'fill_flag' column.",
                manifest_step=manifest.step,
                hint="Add a 'fill_flag' column (0=original, 1=interpolated, 2=imputed).",
            )
        flag_values = set(df["fill_flag"].unique())
        invalid = flag_values - {0, 1, 2}
        if invalid:
            raise FirewallFailure(
                FailureClass.BLOCKING,
                f"output {out.id!r} has fill_flag values outside the IMIS "
                f"vocabulary {{0, 1, 2}}: {invalid}",
                manifest_step=manifest.step,
                hint="Map fill_flag values to the IMIS vocabulary.",
            )
