from __future__ import annotations
import numpy as np
import pandas as pd

SIGNALS = ["cycle_time_s", "queue_length", "vibration_rms", "temperature_c", "torque_nm"]

def add_spc_features(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    out = df.sort_values(["station_id", "completion_min", "vehicle_id"]).copy()
    for col in SIGNALS:
        if col not in out: continue
        g = out.groupby("station_id", sort=False)[col]
        mean = g.transform(lambda s: s.shift(1).rolling(window, min_periods=8).mean())
        std = g.transform(lambda s: s.shift(1).rolling(window, min_periods=8).std())
        out[f"{col}_z"] = (out[col] - mean) / (std + 1e-6)
    zcols = [f"{c}_z" for c in SIGNALS if f"{c}_z" in out]
    out["spc_alarm_count"] = out[zcols].abs().gt(3).sum(axis=1)
    out["spc_anomaly"] = out["spc_alarm_count"].gt(0).astype(int)
    out["cycle_time_ewma"] = out.groupby("station_id")["cycle_time_s"].transform(lambda s: s.ewm(span=20, min_periods=8, adjust=False).mean())
    out["queue_ewma"] = out.groupby("station_id")["queue_length"].transform(lambda s: s.ewm(span=20, min_periods=8, adjust=False).mean())
    return out


def bottleneck_risk(df: pd.DataFrame, horizon_min: float = 15.0) -> pd.DataFrame:
    out = add_spc_features(df)
    out["queue_growth"] = out.groupby("station_id")["queue_length"].transform(lambda s: s.diff(8) / 8.0)
    out["cycle_growth"] = out.groupby("station_id")["cycle_time_s"].transform(lambda s: s.diff(8) / 8.0)
    out["utilization_proxy"] = (out["cycle_time_s"] / 60.0).clip(0, 1.5)
    raw = 0.40 * out["queue_growth"].fillna(0) + 0.35 * out["cycle_growth"].fillna(0) + 0.25 * (out["utilization_proxy"] - 0.80)
    out["bottleneck_risk"] = 1 / (1 + np.exp(-6 * raw))
    out["bottleneck_horizon_min"] = horizon_min
    out["bottleneck_alert"] = (out["bottleneck_risk"] >= 0.65).astype(int)
    return out
