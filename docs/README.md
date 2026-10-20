# System Documentation Hub

Welcome to the documentation repository for the **College Attendance Management System**.

This directory houses all engineering specifications, architecture definitions, database schemas, API contracts, deployment plans, and architectural decision records for the institutional platform.

---

## Directory Organization

```text
docs/
├── README.md                  # This index
├── PROJECT_RESTART.md         # Baseline reset and archival record
├── requirements/              # Confirmed college requirements & SRS
├── architecture/              # High-level architecture, component diagrams, workflows
├── database/                  # Entity models, ERDs, schema definitions, migrations
├── frontend/                  # UI/UX specifications, component hierarchy, design system
├── api/                       # REST/GraphQL interface specifications and contracts
├── deployment/                # Production & local infrastructure, Docker, CI/CD
└── decisions/                 # Architecture Decision Records (ADRs)
```

---

## Documentation Standards

1. **Requirements-Driven:** No implementation proceeds without documented, verified requirements.
2. **Strict Versioning:** Documentation must be updated alongside architectural changes.
3. **Traceability:** Every architectural and schema decision should link back to user requirements or an ADR in `docs/decisions/`.
4. **Historical Isolation:** Historical artifacts reside exclusively in `archive/previous-version/` and are not to be mixed with active documentation.
