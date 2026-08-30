from dataclasses import dataclass

@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    drift_station_id: int | None = None
    drift_start_min: float = 110.0
    drift_end_min: float = 150.0
    drift_strength: float = 0.0
    bottleneck_station_id: int | None = None
    bottleneck_strength: float = 0.0
    sensor_gap_station_id: int | None = None

SCENARIOS = {
    "normal": Scenario("normal", "Stable line with natural process variation."),
    "hidden_degradation": Scenario("hidden_degradation", "Gradual machine-health drift at ST-12 before inspection detects downstream quality issues.", 12, 110, 150, 0.0),
    "bottleneck": Scenario("bottleneck", "Cycle-time and queue growth at ST-14 creates an early bottleneck warning.", None, bottleneck_station_id=14, bottleneck_strength=0.55),
    "sensor_gap": Scenario("sensor_gap", "Risk emerges near a manual-only station and must be inferred from neighboring signals.", None, sensor_gap_station_id=37),
}
