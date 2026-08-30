from __future__ import annotations
import pandas as pd


def make_event_log(observations: pd.DataFrame, inspections: pd.DataFrame, maintenance: pd.DataFrame) -> pd.DataFrame:
    events = []
    for r in observations.itertuples(index=False):
        events.append((r.vehicle_id, r.station_id, "ARRIVAL", r.arrival_min))
        events.append((r.vehicle_id, r.station_id, "START", r.start_min))
        events.append((r.vehicle_id, r.station_id, "COMPLETE", r.completion_min))
    for r in inspections.itertuples(index=False):
        events.append((r.vehicle_id, r.station_id, "QUALITY_CHECK", r.timestamp_min))
        if int(r.defect_flag):
            events.append((r.vehicle_id, r.station_id, "DEFECT", r.timestamp_min))
    for r in maintenance.itertuples(index=False):
        events.append(("SYSTEM", r.station_id, "MAINTENANCE", r.start_min))
    return pd.DataFrame(events, columns=["vehicle_id", "station_id", "event_type", "timestamp_min"]).sort_values("timestamp_min")
