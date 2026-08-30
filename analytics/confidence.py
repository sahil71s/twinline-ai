from __future__ import annotations
import numpy as np

def confidence_score(sensor_coverage: float, recency: float, volatility: float, model_agreement: float, evidence_count: int) -> dict:
    """Transparent confidence: coverage × recency × stability × agreement, gated by evidence."""
    coverage = float(np.clip(sensor_coverage, 0, 1))
    recency = float(np.clip(recency, 0, 1))
    stability = float(np.clip(1 - volatility, 0, 1))
    agreement = float(np.clip(model_agreement, 0, 1))
    raw = 100 * (0.30 * coverage + 0.20 * recency + 0.20 * stability + 0.30 * agreement)
    if evidence_count < 2:
        return {"score": round(min(raw, 39), 1), "tier": "INSUFFICIENT", "reason": "Fewer than two corroborating signals."}
    if coverage < 0.5:
        raw = min(raw, 64)
        tier = "LOW"
    elif raw >= 75:
        tier = "HIGH"
    elif raw >= 50:
        tier = "MEDIUM"
    else:
        tier = "LOW"
    return {"score": round(raw, 1), "tier": tier, "reason": "Confidence reduced when direct evidence is incomplete or inferred."}
