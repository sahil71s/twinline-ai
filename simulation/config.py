from dataclasses import dataclass

@dataclass(frozen=True)
class SimulationConfig:
    n_units: int = 300
    seed: int = 42
    interarrival_s: float = 48.0
    snapshot_min: float = 155.5
    drift_start_min: float = 110.0
    drift_end_min: float = 150.0
    drift_station_id: int = 12
    inspection_stations: tuple[int, ...] = (39, 40)

STAGES = (
    ("Weld", 8),
    ("Paint", 6),
    ("Assembly", 16),
    ("Trim", 6),
    ("Electrical", 2),
    ("Inspection", 2),
)

SENSOR_TIERS = {"rich": 28, "partial": 8, "manual": 4}
MODELS = ("Apex-150", "Apex-250", "Apex-350")
