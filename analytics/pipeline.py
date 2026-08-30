from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .defect_detection import score_defect_risk
from .inference import infer_sensor_poor_station_risk
from .spc import bottleneck_risk


def run_analytics(data_dir='data/generated', output_dir='outputs'):
    data_dir, output_dir = Path(data_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    stations = pd.read_csv(data_dir/'station_catalog.csv')
    obs = pd.read_csv(data_dir/'production_observations.csv')
    inspections = pd.read_csv(data_dir/'quality_inspections.csv')
    scored = score_defect_risk(obs)
    scored = infer_sensor_poor_station_risk(scored, stations)
    bott = bottleneck_risk(scored)
    for c in ['bottleneck_risk','bottleneck_alert']:
        scored[c] = bott[c].values
    scored.to_csv(output_dir/'scored_observations.csv', index=False)
    summary = scored.groupby(['station_id','station_name','stage','sensor_tier'], as_index=False).agg(
        risk_score=('predicted_defect_risk','mean'), queue_avg=('queue_length','mean'), cycle_avg=('cycle_time_s','mean'),
        bottleneck_rate=('bottleneck_alert','mean'), spc_alert_rate=('spc_anomaly','mean'), direct_sensor_share=('sensor_coverage_pct','mean')
    )
    summary['data_confidence'] = summary.apply(lambda r: 'HIGH' if r.direct_sensor_share >= .9 else ('MEDIUM' if r.direct_sensor_share >= .5 else 'LOW'), axis=1)
    summary.to_csv(output_dir/'station_risk_summary.csv', index=False)
    metrics = {'rows_scored': int(len(scored)), 'stations': int(len(stations)), 'vehicles': int(scored.vehicle_id.nunique()),
               'sensor_tiers': stations.sensor_tier.value_counts().to_dict(),
               'high_risk_stations': summary.nlargest(5,'risk_score').station_id.astype(int).tolist(),
               'inspection_defects': int(inspections.defect_flag.sum())}
    (output_dir/'analytics_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return metrics
