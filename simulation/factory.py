from __future__ import annotations
import numpy as np
import pandas as pd
from .config import STAGES, SENSOR_TIERS


def build_station_catalog(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    station_no = 1
    tier_order = ["rich"] * 28 + ["partial"] * 8 + ["manual"] * 4
    for stage, count in STAGES:
        for _ in range(count):
            rows.append({
                "station_id": station_no,
                "station_name": f"ST-{station_no:02d}",
                "stage": stage,
                "base_cycle_time_s": round(float(np.clip(rng.normal(50, 4.5), 40, 62)), 2),
                "station_criticality": round(float(rng.uniform(0.75, 1.30)), 3),
                "sensor_tier": tier_order[station_no - 1],
                "sensor_coverage_pct": {"rich": 1.0, "partial": 0.55, "manual": 0.0}[tier_order[station_no - 1]],
            })
            station_no += 1
    return pd.DataFrame(rows)
