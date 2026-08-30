from pathlib import Path
from fastapi import FastAPI
from simulation.simulator import run_simulation
from simulation.config import SimulationConfig
from analytics.pipeline import run_analytics
from analytics.genealogy import trace_defect
import pandas as pd

app = FastAPI(title='TwinLine.ai API', version='2.0')
ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT/'data/generated', ROOT/'outputs'

@app.get('/health')
def health(): return {'status':'ok','prototype':'TwinLine.ai'}

@app.post('/scenario/{name}')
def scenario(name: str, units: int = 300):
    stations, vehicles, obs, inspections, maintenance, truth, events = run_simulation(name, SimulationConfig(n_units=units))
    DATA.mkdir(parents=True, exist_ok=True)
    for df, name_ in [(stations,'station_catalog'),(vehicles,'vehicles'),(obs,'production_observations'),(inspections,'quality_inspections'),(maintenance,'maintenance_events'),(truth,'ground_truth'),(events,'vehicle_events')]: df.to_csv(DATA/f'{name_}.csv', index=False)
    metrics = run_analytics(DATA, OUT)
    return metrics

@app.get('/genealogy/{vehicle_id}')
def genealogy(vehicle_id: str):
    stations = pd.read_csv(DATA/'station_catalog.csv'); obs = pd.read_csv(OUT/'scored_observations.csv'); inspections = pd.read_csv(DATA/'quality_inspections.csv')
    return trace_defect(vehicle_id, inspections, obs, stations)
