from pathlib import Path
from simulation.simulator import run_simulation
from simulation.config import SimulationConfig
from analytics.pipeline import run_analytics
from validation.backtest import run_backtest

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'data/generated'
OUT = ROOT/'outputs'

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    stations, vehicles, obs, inspections, maintenance, truth, events = run_simulation('hidden_degradation', SimulationConfig(n_units=300))
    for df, name in [(stations,'station_catalog'),(vehicles,'vehicles'),(obs,'production_observations'),(inspections,'quality_inspections'),(maintenance,'maintenance_events'),(truth,'ground_truth'),(events,'vehicle_events')]:
        df.to_csv(DATA/f'{name}.csv', index=False)
    print('Analytics:', run_analytics(DATA, OUT))
    print('Validation:', run_backtest(DATA, OUT))

if __name__ == '__main__': main()
