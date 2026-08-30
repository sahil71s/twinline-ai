from __future__ import annotations
import numpy as np
import pandas as pd
from .spc import add_spc_features
from .confidence import confidence_score


def score_defect_risk(observations: pd.DataFrame) -> pd.DataFrame:
    out = add_spc_features(observations)
    evidence = pd.DataFrame(index=out.index)
    checks = []
    for col in ["cycle_time_s_z", "queue_length_z", "vibration_rms_z", "temperature_c_z", "torque_nm_z"]:
        if col in out: checks.append(out[col].abs().fillna(0).gt(2.5))
    evidence_count = sum(checks) if checks else pd.Series(0, index=out.index)
    signal_component = out["upstream_defect_signal"].fillna(0).clip(0, .35) / .35
    evidence_component = (evidence_count / 3).clip(0, 1)
    quality_component = (1 - out["part_quality_score"].fillna(1)).clip(0, .12) / .12
    out["predicted_defect_risk"] = (0.05 + 0.40 * signal_component + 0.30 * evidence_component + 0.15 * quality_component + 0.10 * out["spc_anomaly"]).clip(0, .99)
    out["defect_alert"] = (out["predicted_defect_risk"] >= 0.45).astype(int)
    out["evidence_count"] = evidence_count.astype(int)
    out["inference_mode"] = np.where(out.sensor_tier.eq("rich"), "DIRECT", np.where(out.sensor_tier.eq("partial"), "PARTIAL", "INFERRED"))
    out["confidence_tier"] = [
        confidence_score(r.sensor_coverage_pct, 0.9, 0.15 if r.evidence_count >= 2 else 0.45, min(1, r.evidence_count/3), int(r.evidence_count))["tier"]
        for r in out.itertuples()
    ]
    return out
