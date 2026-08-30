from __future__ import annotations
import numpy as np
import pandas as pd
from .config import SimulationConfig, MODELS
from .factory import build_station_catalog
from .events import make_event_log
from .scenarios import SCENARIOS, Scenario


def run_simulation(scenario_name: str = "hidden_degradation", cfg: SimulationConfig | None = None):
    cfg = cfg or SimulationConfig()
    scenario = SCENARIOS[scenario_name]
    rng = np.random.default_rng(cfg.seed + list(SCENARIOS).index(scenario_name))
    stations = build_station_catalog(cfg.seed)
    n = cfg.n_units
    vehicles = pd.DataFrame({
        "vehicle_id": [f"VIN-{i:04d}" for i in range(1, n + 1)],
        "model": rng.choice(MODELS, n, p=[0.45, 0.35, 0.20]),
        "line_entry_min": np.arange(n) * (cfg.interarrival_s / 60.0),
    })
    prev_completion = np.full(len(stations), -np.inf)
    rows = []
    truth_rows = []
    inspection_rows = []
    maintenance_rows = []
    unit_quality = np.ones(n)
    root_station = np.full(n, -1, dtype=int)
    root_time = np.full(n, np.nan)

    for sidx, st in stations.iterrows():
        sid = int(st.station_id)
        prev_vehicle_completion = -np.inf
        for i, v in vehicles.iterrows():
            entry = float(v.line_entry_min)
            upstream_completion = prev_completion[sidx - 1] if sidx > 0 else entry
            arrival = max(entry if sidx == 0 else rows[-1]["completion_min"], prev_vehicle_completion) if rows else max(entry, upstream_completion)
            # For subsequent stations, locate the current vehicle's prior station completion.
            if sidx > 0:
                prior = rows[-1]["completion_min"] if rows and rows[-1]["vehicle_id"] == v.vehicle_id else next(
                    r["completion_min"] for r in reversed(rows) if r["vehicle_id"] == v.vehicle_id and r["station_id"] == sid - 1
                )
                arrival = max(prior, prev_vehicle_completion)
            model_effect = {"Apex-150": -2.0, "Apex-250": 0.0, "Apex-350": 2.5}[v.model]
            minute = arrival
            drift = 0.0
            if scenario.drift_station_id == sid and scenario.drift_start_min <= minute <= scenario.drift_end_min:
                progress = (minute - scenario.drift_start_min) / max(scenario.drift_end_min - scenario.drift_start_min, 1)
                drift = 14.0 * progress + 5.0
            if scenario.bottleneck_station_id == sid and 90 <= minute <= 150:
                drift += scenario.bottleneck_strength * 35
            if scenario.sensor_gap_station_id == 37 and sid == 36 and 100 <= minute <= 145:
                drift += 12.0
            wear = np.clip((minute / 1800.0) + st.station_criticality * 0.08, 0, 1.35)
            part_quality = np.clip(unit_quality[i] + rng.normal(0, 0.008), 0.75, 1.03)
            cycle = max(35.0, float(st.base_cycle_time_s) + model_effect + drift + 7.5 * wear + rng.normal(0, 1.4))
            queue = max(0.0, (cycle / cfg.interarrival_s) * 5 + rng.normal(0, 1.0))
            vibration = np.nan if st.sensor_tier == "manual" else max(0.25, 0.65 + 0.75 * wear + drift / 20 + rng.normal(0, .08))
            temperature = np.nan if st.sensor_tier == "manual" else 48 + 7 * wear + drift / 5 + rng.normal(0, .8)
            torque = np.nan if st.sensor_tier != "rich" else 62 - 3.0 * wear - drift * 0.35 + rng.normal(0, .9)
            operator_var = rng.normal(0, .25)
            start = max(arrival, prev_vehicle_completion)
            completion = start + cycle / 60.0
            prev_vehicle_completion = completion
            prev_completion[sidx] = completion

            defect_pressure = 0.0
            if scenario.drift_station_id == sid and drift >= 8.0:
                defect_pressure += 1.40
            if sidx > 0:
                defect_pressure += max(0, 0.97 - unit_quality[i]) * 4
            if scenario.drift_station_id and sidx > scenario.drift_station_id - 1 and root_station[i] == scenario.drift_station_id:
                defect_pressure += 0.85
            defect_flag_local = defect_pressure > 1.15
            if defect_flag_local and root_station[i] == -1:
                root_station[i] = sid
                root_time[i] = minute
                unit_quality[i] = max(0.78, unit_quality[i] - 0.07)
            if sidx > 0 and root_station[i] > 0:
                unit_quality[i] = max(0.78, unit_quality[i] - 0.004)

            # Once an early root cause is established, carry a weak downstream signal.
            if scenario.drift_station_id == sid and drift >= 8.0:
                upstream_signal = 0.22
            elif root_station[i] > 0 and sid > root_station[i]:
                upstream_signal = min(0.30, 0.12 + 0.18 * max(0, 1.0 - (sid-root_station[i])/30))
            else:
                upstream_signal = float(max(0, 1-unit_quality[i]))

            rows.append({
                "vehicle_id": v.vehicle_id, "station_id": sid, "station_name": st.station_name,
                "stage": st.stage, "model": v.model, "arrival_min": arrival, "start_min": start,
                "completion_min": completion, "cycle_time_s": cycle, "queue_length": queue,
                "vibration_rms": vibration, "temperature_c": temperature, "torque_nm": torque,
                "part_quality_score": part_quality, "operator_variation": operator_var,
                "sensor_tier": st.sensor_tier, "sensor_coverage_pct": st.sensor_coverage_pct,
                "maintenance_age_h": minute / 60.0, "upstream_defect_signal": upstream_signal,
            })
        
    observations = pd.DataFrame(rows)
    # Create explicit late inspection outcomes from the hidden root-cause state.
    last_station = observations[observations.station_id.isin(cfg.inspection_stations)].copy()
    for vin, g in last_station.groupby("vehicle_id"):
        g = g.sort_values("station_id")
        has_root = int((root_station[int(vin.split('-')[1]) - 1] == cfg.drift_station_id))
        for r in g.itertuples(index=False):
            prob = 0.01 + 0.94 * has_root
            failed = int(rng.random() < prob)
            inspection_rows.append({"vehicle_id": vin, "station_id": r.station_id, "timestamp_min": r.completion_min,
                                    "inspection_result": "FAIL" if failed else "PASS", "defect_flag": failed,
                                    "true_root_station_id": cfg.drift_station_id if failed and has_root else None})
    inspections = pd.DataFrame(inspection_rows)

    if scenario.drift_station_id:
        for minute in np.arange(cfg.drift_start_min - 50, cfg.drift_end_min + 20, 100):
            maintenance_rows.append({"station_id": scenario.drift_station_id, "start_min": float(minute), "end_min": float(minute + 12), "event_type": "INSPECTION_MAINTENANCE"})
    maintenance = pd.DataFrame(maintenance_rows)

    truth = pd.DataFrame({
        "vehicle_id": vehicles.vehicle_id,
        "true_root_station_id": root_station,
        "true_root_time_min": root_time,
        "shipped_by_snapshot": observations.groupby("vehicle_id").completion_min.max().reindex(vehicles.vehicle_id).fillna(0).values < cfg.snapshot_min,
    })
    truth["true_root_station_id"] = truth["true_root_station_id"].replace(-1, np.nan)
    truth["scenario"] = scenario.name
    truth["snapshot_min"] = cfg.snapshot_min
    events = make_event_log(observations, inspections, maintenance)
    return stations, vehicles, observations, inspections, maintenance, truth, events
