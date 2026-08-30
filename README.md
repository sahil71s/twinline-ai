# TwinLine.ai v2 — Round 2 Prototype

**Predict the problem. Trace who it touched. Simulate the decision. Keep the human in control.**

TwinLine.ai is a synthetic, confidence-aware digital twin prototype for a 40-station vehicle assembly line. It is designed to demonstrate the Round 2 requirements and the Round 1 concept evolution: **Sense → Understand → Predict → Confidence → Simulate → Recommend → Act**.

## What changed in v2

- 40 stations across Weld, Paint, Assembly, Trim, Electrical and Inspection.
- Uneven sensor coverage: **28 rich / 8 partial / 4 manual-only**.
- Vehicle-level event history with timestamps.
- Multi-causal process signals and delayed defect manifestation.
- Transparent SPC-style anomaly and bottleneck risk.
- Confidence engine with an explicit evidence/coverage gate.
- Sensor-poor inference without fabricating sensor values.
- Defect Genealogy Tracer: backward origin + forward affected vehicles.
- What-if intervention comparison with human approval/override logging.
- Chronological backtest with precision, recall, false-positive rate and warning lead time.
- Five Streamlit screens matching the demo strategy.
- Read-only/passive OT integration story; no PLC write logic.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m simulation.run_simulation --scenario hidden_degradation --units 300
python -c "from analytics.pipeline import run_analytics; print(run_analytics())"
python -c "from validation.backtest import run_backtest; print(run_backtest())"
streamlit run app/dashboard.py
```

If PowerShell blocks activation, you can use the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m simulation.run_simulation --scenario hidden_degradation --units 300
.\.venv\Scripts\python.exe -m validation.backtest
.\.venv\Scripts\python.exe -m streamlit run app/dashboard.py
```

## Scenarios

- `normal` — stable line.
- `hidden_degradation` — ST-12 drift followed by late inspection defects; signature genealogy demo.
- `bottleneck` — ST-14 cycle-time/queue growth.
- `sensor_gap` — manual station inference story.

## Demo flow

1. Line Overview → normal baseline.
2. Station Detail → show emerging risk, evidence and confidence.
3. Defect Genealogy → select a failed vehicle and trace the likely origin.
4. What-If → compare continue / repair / quarantine / full stop and log a human decision.
5. Validation & ROI → show synthetic backtest metrics and clearly labelled illustrative ROI.

## Architecture

```text
Simulation → Observations → Analytics → Confidence → Genealogy / What-if → Streamlit
     │             │              │              │             │
 Ground truth   sensor gaps     SPC/risk      trust gate     human decision
```

The numerical source of truth is Python/statistics/rules. An optional LLM may translate already-computed payloads, but must not invent or modify numeric values.

## Important prototype caveat

All production data are synthetic. Performance numbers are **development/backtest results only** and must not be represented as real client performance.
