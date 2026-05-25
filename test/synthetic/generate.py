"""Synthetic dataset generator for sakshi's pedagogical worked example.

This file is tangled from codev/examples/synthetic.org.

Produces:
    test/synthetic/data/raw.csv               -- measurement-register
    test/synthetic/data/gapfilled_clean.csv   -- correct gap-fill
    test/synthetic/data/gapfilled_synthetic.csv -- correct compound-register gap-fill
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_ou_walk(
    n: int = 720,
    seed: int = 42,
    theta: float = 0.05,
    mu: float = 0.0,
    sigma: float = 0.5,
    dt: float = 1.0,
) -> np.ndarray:
    """Generate an Ornstein-Uhlenbeck path. Deterministic in *seed*."""
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = mu
    for i in range(1, n):
        x[i] = x[i - 1] + theta * (mu - x[i - 1]) * dt + sigma * np.sqrt(dt) * rng.standard_normal()
    return x


def make_raw_with_gaps(out_path: Path, seed: int = 42) -> pd.DataFrame:
    """Make the raw CSV: a 30-day hourly OU walk with 8 known NaN dropouts."""
    n = 24 * 30
    walk = generate_ou_walk(n=n, seed=seed)
    dropout_positions = [50, 51, 52, 53, 100, 101, 400, 401]
    values = walk.copy()
    values[dropout_positions] = np.nan

    timestamps = pd.date_range("2024-01-01", periods=n, freq="h")
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "value": values,
            "qc_flag": np.where(np.isnan(values), 9, 0),
        }
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


def make_gapfilled_clean(raw: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    """Linear temporal interpolation across all gaps.

    All gaps in this dataset are <= 4 hours wide, so they are within
    the doctrine's default 6-hour threshold for deterministic
    interpolation. The output's register is plain
    'derived-from-measurement' (no compound).
    """
    out = raw.copy().set_index("timestamp")
    out["value"] = out["value"].interpolate(method="time")
    out["qc_flag"] = np.where(raw.set_index("timestamp")["qc_flag"] == 9, 1, 0)
    out.reset_index().to_csv(out_path, index=False)
    return out.reset_index()


def make_gapfilled_synthetic(raw: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    """Same as clean, but with one gap deliberately re-filled by a generative model.

    To make the example self-contained, the 'generative model' here is
    just a different deterministic procedure (a per-hour cyclic mean)
    applied to one gap. In real practice this would be a learned
    imputer. The point is the *register obligation*: that gap's value
    is no longer derivable from neighbouring measurements, so it carries
    'synthetic-acknowledged' and the column-level register is the
    compound.
    """
    df = make_gapfilled_clean(raw, out_path)
    df = df.set_index("timestamp")
    cyclic_mean = df.groupby(df.index.hour)["value"].transform("mean")
    df.loc[df.index[400], "value"] = cyclic_mean.iloc[400]
    df.loc[df.index[401], "value"] = cyclic_mean.iloc[401]
    df.loc[df.index[400], "qc_flag"] = 2
    df.loc[df.index[401], "qc_flag"] = 2
    df.reset_index().to_csv(out_path, index=False)
    return df.reset_index()


if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"
    raw = make_raw_with_gaps(data_dir / "raw.csv")
    make_gapfilled_clean(raw, data_dir / "gapfilled_clean.csv")
    make_gapfilled_synthetic(raw, data_dir / "gapfilled_synthetic.csv")
