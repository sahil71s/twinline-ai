from __future__ import annotations

def scorecard(metrics: dict) -> list[dict]:
    d = metrics['defect']; l = metrics['lead_time_min']
    return [
        {'metric':'Precision','value':d['precision'],'target':'Higher is better'},
        {'metric':'Recall','value':d['recall'],'target':'Higher is better'},
        {'metric':'False-positive rate','value':d['false_positive_rate'],'target':'< 5% preferred'},
        {'metric':'Median warning lead time (min)','value':l['median'],'target':'15+ min objective'},
    ]
