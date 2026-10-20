# Architecture Decision Records (ADR)

This directory serves as the formal decision log for significant architectural, technical, and operational decisions made throughout the project lifecycle.

---

## Decision Record Format

Each decision is documented in a markdown file named `ADR-XXXX-<short-title>.md` following this structure:

- **Decision ID:** Unique identifier (e.g., `ADR-0001`)
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** The problem or circumstance requiring a decision.
- **Decision:** The specific architectural or technical choice.
- **Alternatives Considered:** Other options evaluated and why they were rejected.
- **Reason:** Core justification for the chosen approach.
- **Impact:** Consequences, benefits, tradeoffs, and downstream effects.

---

## Decision Log Index

| ID | Title | Date | Status |
| :--- | :--- | :--- | :--- |
| [ADR-0001](ADR-0001-project-restart-and-clean-baseline.md) | Repository Cleanup and Project Restart from Clean Baseline | 2026-09-27 | Accepted |
| [ADR-0002](ADR-0002-technology-stack.md) | Selection of Technology Stack (Django + DRF + React/TS + PostgreSQL) | 2026-09-27 | Proposed |
