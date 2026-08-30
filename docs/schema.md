# Data schema

## station_catalog.csv
`station_id, station_name, stage, base_cycle_time_s, station_criticality, sensor_tier, sensor_coverage_pct`

## vehicles.csv
`vehicle_id, model, line_entry_min`

## production_observations.csv
Vehicle × station observations with arrival/start/completion times and available process signals. Manual-only stations contain nulls for unavailable sensors.

## quality_inspections.csv
`vehicle_id, station_id, timestamp_min, inspection_result, defect_flag, true_root_station_id`

## maintenance_events.csv
`station_id, start_min, end_min, event_type`

## ground_truth.csv
Hidden simulation truth used only for evaluation: root station/time, shipped-by-snapshot and scenario.

## vehicle_events.csv
Normalized event stream: ARRIVAL, START, COMPLETE, QUALITY_CHECK, DEFECT, MAINTENANCE.
