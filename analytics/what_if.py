from __future__ import annotations
import pandas as pd

def simulate_intervention(station_summary: pd.DataFrame, action: str, target_station: int | None = None) -> dict:
    base_queue = float(station_summary.queue_avg.mean())
    base_risk = float(station_summary.risk_score.mean())
    if action == 'continue':
        queue, risk, disruption = base_queue * 1.35, min(0.99, base_risk + .18), 'LOW'
    elif action == 'repair_station':
        queue, risk, disruption = base_queue * .70, max(.02, base_risk - .25), 'MEDIUM'
    elif action == 'quarantine':
        queue, risk, disruption = base_queue * .82, max(.03, base_risk - .18), 'LOW'
    elif action == 'full_line_stop':
        queue, risk, disruption = 0.0, max(.01, base_risk - .55), 'HIGH'
    else:
        raise ValueError(action)
    return {'action': action, 'target_station': target_station, 'expected_queue': round(queue, 1), 'expected_risk': round(risk, 3), 'disruption': disruption}
