# R1 Prototype → Round 2 v2 changes

The supplied prototype was kept as a baseline, but the following changes were made to align it with the Round 2 strategy.

## Simulation
- Replaced generic Body/Paint/FinalAssembly grouping with 6 explicit production stages and 40 stations.
- Added 28 rich, 8 partial and 4 manual-only sensor tiers.
- Added vehicle arrival/start/completion timestamps and a flow/event log.
- Added explicit hidden-degradation, bottleneck, sensor-gap and normal scenarios.
- Added separate ground-truth output so truth is not exposed to analytics.
- Added maintenance events and delayed inspection outcomes.

## Analytics
- Kept transparent SPC-style logic.
- Added an explicit confidence formula and evidence gate.
- Added manual-station neighbor inference without fabricating sensor readings.
- Added station graph and vehicle-level genealogy tracing.
- Added what-if intervention comparison and human decision logging.
- Added scenario-level backtesting and lead-time measurement.

## Validation
- Removed the original random unit shuffle as the main validation claim.
- Validation now documents its synthetic scenario protocol and does not present synthetic metrics as client performance.

## Product
- Added five Streamlit views matching the Round 2 strategy.
- Added passive/read-only OT integration language.
- Added demo script, schema, assumptions and business-proposal narrative.
