# Database Design & Schema

This directory maintains the relational database schema, Entity-Relationship Diagrams (ERD), data dictionary, and migration strategy.

---

## Status

- **Current State:** Clean baseline. No legacy database migrations or development SQLite/PostgreSQL instances carried over.
- **Reference Only:** Conceptual models from the v0.1 draft are archived at `archive/previous-version/`.

---

## Areas to Cover

1. **Entity Models:** Academic hierarchy (Department, Semester, Division/Section, Subject), User/Role mapping, Lecture Sessions, Topic Logs, Attendance Records, and Audit Logs.
2. **Data Integrity & Constraints:** Composite unique keys, foreign key cascading rules, check constraints.
3. **Auditability:** Immutability rules for attendance records and audit logs for administrative modifications.
