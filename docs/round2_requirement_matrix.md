# Round 2 requirement coverage

| Requirement from strategy | Implementation | Evidence |
|---|---|---|
| Uneven sensor coverage | `sensor_tier`: rich/partial/manual | station catalog + Line Overview |
| Multi-causal/intermittent root causes | cycle, queue, vibration, temperature, torque, quality, upstream signals | production observations + Station Detail |
| Early defect caught late | vehicle history + late inspection + genealogy | Defect Genealogy screen |
| Read-only OT integration | no PLC write logic | architecture/business docs |
| Persona views | floor, plant manager, leadership | five-screen app |
| Validation / false alarms | precision, recall, FPR, lead time | Validation & ROI screen |
| Data gaps | neighbor/process inference + confidence downgrade | Station Detail / inference.py |
| Human-in-the-loop | approve/override + decision log | What-If screen |
| What-if intervention | continue/repair/quarantine/full stop | what_if.py + screen |
| Scalability | documented architecture; no multi-plant build | business proposal |
