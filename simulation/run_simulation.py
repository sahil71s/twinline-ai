from __future__ import annotations
import argparse
from pathlib import Path
from .simulator import run_simulation
from .config import SimulationConfig


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--scenario', default='hidden_degradation', choices=['normal','hidden_degradation','bottleneck','sensor_gap'])
    p.add_argument('--units', type=int, default=300)
    p.add_argument('--output-dir', default='data/generated')
    args = p.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    cfg = SimulationConfig(n_units=args.units)
    stations, vehicles, obs, inspections, maintenance, truth, events = run_simulation(args.scenario, cfg)
    stations.to_csv(out/'station_catalog.csv', index=False)
    vehicles.to_csv(out/'vehicles.csv', index=False)
    obs.to_csv(out/'production_observations.csv', index=False)
    inspections.to_csv(out/'quality_inspections.csv', index=False)
    maintenance.to_csv(out/'maintenance_events.csv', index=False)
    truth.to_csv(out/'ground_truth.csv', index=False)
    events.to_csv(out/'vehicle_events.csv', index=False)
    print(f'Generated {len(vehicles)} vehicles x {len(stations)} stations = {len(obs)} observations')

if __name__ == '__main__':
    main()
