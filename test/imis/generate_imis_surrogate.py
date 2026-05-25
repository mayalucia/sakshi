"""Generate a small synthetic surrogate for IMIS air-temperature data.

This file is tangled from codev/examples/imis.org.

Shape and column conventions follow the SLF IMIS API documentation:
    https://www.slf.ch/en/avalanche-bulletin-and-snow-situation/measured-values.html

Columns:
    station_id      -- 'WFJ' or 'FLU' (Weissfluhjoch, Davos Flueela)
    timestamp_utc   -- ISO-8601 UTC timestamp (hourly)
    air_temp_c      -- air temperature in degrees Celsius (NaN for missing)
    qc_flag         -- IMIS QC flag (0=ok, 1=flagged, 9=missing)

Produces:
    test/imis/data/imis_wfj_flu_2024-02.csv  -- raw, with known gaps
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def synth_station(
    station_id: str,
    n_hours: int,
    base_temp: float,
    daily_amp: float,
    noise_sigma: float,
    gap_indices: list[int],
    seed: int,
) -> pd.DataFrame:
    """Generate a synthetic hourly time series for one station."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2024-02-15 00:00", periods=n_hours, freq="h", tz="UTC")
    hours = np.arange(n_hours)
    diurnal = daily_amp * np.sin(2 * np.pi * hours / 24)
    drift = -0.5 * np.cos(2 * np.pi * hours / (24 * 7))
    noise = rng.normal(0, noise_sigma, n_hours)
    temps = base_temp + diurnal + drift + noise
    temps[gap_indices] = np.nan
    qc = np.where(np.isnan(temps), 9, 0)
    return pd.DataFrame(
        {
            "station_id": station_id,
            "timestamp_utc": timestamps.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "air_temp_c": np.round(temps, 2),
            "qc_flag": qc,
        }
    )


def make_surrogate(out_path: Path) -> pd.DataFrame:
    """Make the two-station surrogate covering 48 hours in mid-Feb 2024."""
    n_hours = 48
    wfj_gaps = [4, 5, 6, 20, 21]
    flu_gaps = [12, 13, 14, 15, 16, 17, 18, 19, 30]
    wfj = synth_station(
        station_id="WFJ",
        n_hours=n_hours,
        base_temp=-8.5,
        daily_amp=4.0,
        noise_sigma=0.4,
        gap_indices=wfj_gaps,
        seed=2024,
    )
    flu = synth_station(
        station_id="FLU",
        n_hours=n_hours,
        base_temp=-6.0,
        daily_amp=5.5,
        noise_sigma=0.5,
        gap_indices=flu_gaps,
        seed=2025,
    )
    df = pd.concat([wfj, flu], ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    make_surrogate(Path(__file__).parent / "data" / "imis_wfj_flu_2024-02.csv")
