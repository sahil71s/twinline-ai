from __future__ import annotations
import numpy as np
import pandas as pd


def infer_sensor_poor_station_risk(scored: pd.DataFrame, stations: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    station_order = stations.sort_values('station_id').station_id.tolist()
    neighbors = {sid: station_order[max(0, i-1):min(len(station_order), i+2)] for i, sid in enumerate(station_order)}
    out['inference_mode'] = np.where(out.sensor_tier.eq('manual'), 'INFERRED', out.inference_mode)
    # For manual stations, borrow upstream/downstream risk from the same vehicle and neighboring station observations.
    risk_by_vehicle_station = out.set_index(['vehicle_id','station_id'])['predicted_defect_risk']
    inferred = []
    for r in out.itertuples():
        if r.sensor_tier != 'manual':
            inferred.append(r.predicted_defect_risk); continue
        vals = []
        for sid in neighbors[r.station_id]:
            if sid == r.station_id: continue
            try: vals.append(float(risk_by_vehicle_station.loc[(r.vehicle_id, sid)]))
            except KeyError: pass
        inferred.append(float(np.mean(vals)) if vals else float(r.predicted_defect_risk))
    out['inferred_defect_risk'] = inferred
    out.loc[out.sensor_tier.eq('manual'), 'predicted_defect_risk'] = out.loc[out.sensor_tier.eq('manual'), 'inferred_defect_risk']
    out.loc[out.sensor_tier.eq('manual'), 'confidence_tier'] = np.where(out.loc[out.sensor_tier.eq('manual'), 'evidence_count'] >= 2, 'LOW', 'INSUFFICIENT')
    return out
