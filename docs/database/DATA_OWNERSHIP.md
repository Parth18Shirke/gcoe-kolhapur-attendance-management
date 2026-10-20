# Data Ownership & Boundary Model

**Document ID:** DOC-DB-OWN-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. System Boundary Definition

The Attendance Management System co-exists alongside the college's broader administrative ecosystem (Registrar ERP, Student Admissions Portal, Examination Cell). Clear data ownership boundaries are mandatory to prevent split-brain inconsistencies.

---

## 2. Ownership Distribution

```
┌───────────────────────────────────────────────┐      ┌───────────────────────────────────────────────┐
│     EXTERNAL COLLEGE AUTHORITATIVE DOMAIN     │      │        AMS AUTHORITATIVE DOMAIN               │
│                                               │      │                                               │
│  - Student University PRN & Legal Identity    │      │  - Timetable Slots & Lecture Sessions         │
│  - Official Student Institutional Email       │ ───► │  - Session Cancellation & Rescheduling        │
│  - Student Admission & Graduation Status      │ Sync │  - Syllabus Topics Covered (Structured/Notes) │
│  - Academic Year & Term Calendar Boundaries   │      │  - Daily Attendance Marks (Present/Absent)    │
│  - Official Course/Subject Curriculum Catalog │      │  - Attendance Draft / Finalization States     │
│  - Faculty Institutional Employment Status    │      │  - Attendance Corrections & HOD Approvals     │
│                                               │      │  - 75% Statutory Calculation Metrics          │
│                                               │      │  - Warning Notification Outbox & Logs         │
│                                               │      │  - Immutable Audit History                    │
└───────────────────────────────────────────────┘      └───────────────────────────────────────────────┘
```

---

## 3. Synchronization Invariants

1. **Non-Destructive Ingestion:** Ingesting updated student lists from the college will update demographic fields (`full_name`, `official_email`, `division_id`, `status`), but will **never delete or overwrite existing attendance records**.
2. **Missing Records Handling:** If an existing student is absent from a new batch import file, their status is transitioned to `INACTIVE` or `ARCHIVED`, preserving all prior attendance history for university reporting.
3. **Identifier Authority:** The University PRN is the immutable anchor. If a student changes divisions or roll numbers, PRN preserves their historical continuity.
