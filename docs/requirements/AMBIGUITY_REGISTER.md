# Ambiguity & Assumptions Register

**Document ID:** DOC-REQ-AMB-001  
**Project:** College Attendance Management System  
**Date:** October 2026  
**Status:** Active Governance Register  

---

## 1. Classification Methodology

Every unresolved item, design assumption, and external dependency is cataloged according to urgency:

- **P0 — Critical Blocker:** Must be clarified before database schema or core workflow freeze.
- **P1 — High Priority:** Must be clarified before final production deployment.
- **P2 — Medium Priority:** Operational refinement; default fallback policy can be deployed initially.
- **P3 — Future Consideration:** Beyond initial scope; documented for architectural extensibility.

---

## 2. Active Ambiguity Register

| ID | Domain | Unresolved Item / Question | Why It Matters | Priority | Working Assumption / Safe Default | Responsible Party | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **AMB-01** | Hosting | **Exact Hostinger Subscription Tier** | Determines whether Docker, systemd, PostgreSQL 15+, and custom daemons can run natively (VPS) or if shared hosting constraints apply. | **P0** | Design as a decoupled modular monolith deployable on standard Linux VPS (Docker/systemd) with fallback to WSGI/cron. | College Administration / IT | Open |
| **AMB-02** | Integration | **Authoritative Student Data Source** | Determines the exact parser needed: Excel (`.xlsx`), CSV, direct read-only SQL view, or college ERP REST API. | **P0** | Standard structured Excel/CSV import engine with schema validation, preview, and reconciliation boundaries. | Academic Office / Sir | Open |
| **AMB-03** | Operations | **Attendance Marking Grace Period** | Determines whether faculty are restricted to marking attendance strictly during scheduled lecture hours. | **P1** | Faculty can record attendance on the lecture date. Submissions outside the scheduled window record a warning flag without hard-blocking. | Academic Committee | Open |
| **AMB-04** | Security | **Correction Authorization Policy** | Determines whether faculty can self-correct recent mistakes or if all corrections require HOD sign-off. | **P1** | Hybrid model: Faculty can self-correct within **24 hours**; older or finalized corrections require HOD review and approval. | HOD / Teaching Staff | Provisionally Confirmed |
| **AMB-05** | Reporting | **Official College Report Layouts** | Columns, header metadata, college crest, and signature hierarchy required for official records. | **P1** | Implement clean, standardized A4 PDF and editable `.docx` templates adhering to standard Indian university conventions pending exact samples. | Academic Cell / Sir | Open |
| **AMB-06** | Email | **Institutional SMTP Specifications** | Hostname, port, TLS/SSL mode, credentials, and outbound rate limits for warning emails. | **P1** | Environment-configured email provider abstraction supporting standard SMTP with exponential backoff and rate-limiting queue. | College IT | Open |
| **AMB-07** | Email | **75% Warning Notification Interval** | Frequency of reminder emails to prevent mail server throttling and inbox fatigue. | **P2** | Immediate notification upon crossing below 75%, followed by a weekly reminder cycle with a 7-day cooldown per student/subject. | Academic Committee | Provisionally Confirmed |
| **AMB-08** | Operations | **Lecture Cancellation Policy** | Who has cancellation authority and whether students receive automated cancellation notices. | **P2** | Faculty may cancel their own sessions; HOD/Admin can cancel any session. Mandatory text reason required. Students not notified in phase 1. | Academic Committee | Provisionally Confirmed |
| **AMB-09** | Academic | **Attendance Status Values** | Whether special statuses (On Duty, Medical Leave, Excused) are recognized in statutory calculations. | **P2** | Binary `Present` / `Absent` model initially, with extensible database enum design to allow new statuses without schema refactoring. | Teaching Staff | Provisionally Confirmed |
| **AMB-10** | Infrastructure | **Background Job Runner on Hostinger** | Availability of Redis/Celery on the assigned Hostinger plan. | **P1** | Database-backed job queue processed via cron-triggered Django management commands to eliminate Redis dependency on constrained hosts. | System Architect | Resolved by Design |

---

## 3. Assumptions Register

1. **Academic Department Scope:** The initial pilot serves a single academic department, but the data architecture supports multiple departments without multi-tenant database partitioning.
2. **Student Identity Stability:** University PRN (Permanent Registration Number) or College Roll Number is globally unique and immutable per student.
3. **Threshold Definition:** Statutory threshold is strictly $75.00\%$. A calculated percentage of $74.99\%$ is **below threshold**; exactly $75.00\%$ is **compliant**.
4. **Cancelled Lecture Denominator:** Cancelled lectures are excluded from both the attendance numerator and denominator by default.
5. **Classroom Offline Mode:** Offline attendance capture will be performed via the client application caching rosters; the server evaluates all sync submissions idempotently upon reconnection.
