from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from analytics.defect_detection import score_defect_risk

def run_backtest(data_dir='data/generated', output_dir='outputs'):
    data_dir, output_dir = Path(data_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    obs = pd.read_csv(data_dir/'production_observations.csv')
    inspections = pd.read_csv(data_dir/'quality_inspections.csv')
    scored = score_defect_risk(obs)
    # Rule-based engine has no fitted model, so evaluate on a complete synthetic
    # scenario while preserving the temporal order of the evidence before inspection.
    outcomes = inspections.groupby('vehicle_id').defect_flag.max().rename('actual_defect')
    vehicle_scores = scored.groupby('vehicle_id').predicted_defect_risk.max().to_frame('predicted_risk').join(outcomes, how='left').fillna({'actual_defect':0}).reset_index()
    threshold = .45
    pred = (vehicle_scores.predicted_risk >= threshold).astype(int)
    y = vehicle_scores.actual_defect.astype(int)
    metrics = {
        'protocol': 'scenario-level synthetic backtest; no future labels are exposed to the scoring rule',
        'defect': {
            'threshold': threshold,
            'precision': float(precision_score(y,pred,zero_division=0)),
            'recall': float(recall_score(y,pred,zero_division=0)),
            'f1': float(f1_score(y,pred,zero_division=0)),
            'false_positive_rate': float(((pred==1)&(y==0)).sum()/max((y==0).sum(),1)),
            'true_positives': int(((pred==1)&(y==1)).sum()),
            'false_positives': int(((pred==1)&(y==0)).sum()),
        },
    }
    failed = inspections[inspections.defect_flag.eq(1)].sort_values('timestamp_min')
    leads=[]
    for r in failed.itertuples(index=False):
        prior = scored[(scored.vehicle_id==r.vehicle_id) & (scored.completion_min < r.timestamp_min)]
        alerts = prior[prior.predicted_defect_risk >= threshold]
        if not alerts.empty: leads.append(float(r.timestamp_min - alerts.completion_min.min()))
    metrics['lead_time_min'] = {'mean': float(pd.Series(leads).mean()) if leads else 0.0, 'median': float(pd.Series(leads).median()) if leads else 0.0, 'alerts_with_lead_time': len(leads)}
    (output_dir/'backtest_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return metrics
