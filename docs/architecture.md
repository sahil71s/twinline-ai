# Architecture

## Core flow

Sense → Understand → Predict → Confidence → Simulate → Recommend → Act.

### Sense
Synthetic vehicle/station observations model imperfect factory data and three sensor tiers.

### Understand
SPC-style rolling z-scores, queue/cycle trends and vehicle history create interpretable evidence.

### Predict
Risk scores estimate emerging defect/bottleneck risk. The prototype favors simple, defensible methods over deep learning.

### Confidence
Confidence is computed from sensor coverage, recency, stability, model agreement and corroborating evidence. Manual/partial stations are explicitly downgraded.

### Simulate
What-if logic compares intervention outcomes without changing real OT systems.

### Recommend / Act
The system recommends a containment or maintenance action. A human approves/overrides; the decision is logged.

## OT integration principle

Prototype integration is passive/read-only: historian/OPC-UA-style data access is assumed. No PLC modification or autonomous stop logic is implemented.
