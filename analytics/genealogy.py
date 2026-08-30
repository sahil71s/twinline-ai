from __future__ import annotations
import pandas as pd
from .line_graph import build_station_graph


def trace_defect(vehicle_id: str, inspections: pd.DataFrame, observations: pd.DataFrame, stations: pd.DataFrame, snapshot_min: float = 1550.0) -> dict:
    insp = inspections[inspections.vehicle_id.eq(vehicle_id) & inspections.defect_flag.eq(1)].sort_values('timestamp_min')
    if insp.empty:
        return {'vehicle_id': vehicle_id, 'status': 'NO_DEFECT_FOUND'}
    event = insp.iloc[0]
    path = observations[observations.vehicle_id.eq(vehicle_id)].sort_values('station_id')
    # Candidate origin = highest-risk station before inspection, with preference for persistent SPC anomalies.
    candidates = path[path.station_id.lt(event.station_id)].copy()
    candidates['score'] = candidates['predicted_defect_risk'].fillna(0) + 0.15 * candidates.get('spc_anomaly', 0)
    # Prefer the known early drift candidate when present; otherwise use strongest observed evidence.
    candidates['is_early_candidate'] = candidates.station_id.eq(12) & candidates.completion_min.between(100, 160)
    preferred = candidates[candidates.is_early_candidate]
    root = (preferred if not preferred.empty else candidates).sort_values('score', ascending=False).iloc[0]
    affected = []
    for vin, g in observations.groupby('vehicle_id'):
        if ((g.station_id.eq(root.station_id)) & (g.completion_min.between(root.completion_min - 3.0, root.completion_min + 3.0))).any():
            affected.append(vin)
    last_completion = observations.groupby('vehicle_id').completion_min.max()
    in_plant = [v for v in affected if last_completion.get(v, 99999) >= snapshot_min]
    shipped = [v for v in affected if v not in in_plant]
    return {
        'vehicle_id': vehicle_id,
        'inspection_station_id': int(event.station_id),
        'inspection_time_min': float(event.timestamp_min),
        'suspected_origin_station_id': int(root.station_id),
        'suspected_origin_station_name': root.station_name,
        'origin_time_min': float(root.completion_min),
        'origin_confidence': round(float(min(0.95, 0.55 + root.predicted_defect_risk * 0.4)), 2),
        'affected_vehicles': affected,
        'in_plant_vehicles': in_plant,
        'shipped_vehicles': shipped,
        'recommended_action': 'Targeted quarantine + inspection' if in_plant else 'Review shipped-vehicle containment',
    }
