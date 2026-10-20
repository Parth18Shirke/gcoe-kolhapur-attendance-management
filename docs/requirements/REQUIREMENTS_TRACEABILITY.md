# Requirements Traceability Matrix

**Document ID:** DOC-REQ-TRC-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Traceability Matrix

| Req ID | Requirement Description | Category | Architecture Component | Backend Module | Database Table | Test Reference |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **REQ-01** | Email OTP Authentication (No password initially, rate-limited, brute-force protected) | CONFIRMED | Auth Subsystem / Token Handler | `apps.accounts` | `accounts_user`, `accounts_otp` | `test_auth.py` |
| **REQ-02** | Role-Based Access Control (Faculty, HOD, Admin server-side enforced) | CONFIRMED | Security & Permission Layer | `apps.accounts` | `accounts_user.role` | `test_rbac.py` |
| **REQ-03** | Academic Master Catalogs (Dept, Program, Year, Semester, Division, Subject) | CONFIRMED | Academics Subsystem | `apps.academics` | `academics_*` | `test_academics.py` |
| **REQ-04** | Student Master (No student login, PRN last-4 privacy in classroom views, active/archived state) | CONFIRMED | Student Subsystem | `apps.students` | `students_student`, `students_enrollment` | `test_students.py` |
| **REQ-05** | Student Data Import / Sync Abstraction (CSV/Excel import, boundary for future ERP sync) | CONFIRMED | Data Ingestion Pipeline | `apps.students` | `students_import_log` | `test_student_import.py` |
| **REQ-06** | Faculty Workload & Subject Assignment (Admin & HOD assign responsibility) | CONFIRMED | Faculty Workload Subsystem | `apps.faculty` | `faculty_assignment` | `test_faculty.py` |
| **REQ-07** | Timetable & Scheduling (Recurring weekly, dated sessions, rooms, theory & lab durations) | CONFIRMED | Timetable Engine | `apps.timetable` | `timetable_slot`, `timetable_session`, `rooms_room` | `test_timetable.py` |
| **REQ-08** | Timetable Conflict Detection (Faculty, Division, Room; default blocking with HOD/Admin override) | CONFIRMED | Conflict Resolver Service | `apps.timetable` | Validation Layer | `test_timetable_conflicts.py` |
| **REQ-09** | Session Cancellation & Rescheduling (Historical retention, non-destructive, audit trail) | CONFIRMED | Session Lifecycle Engine | `apps.timetable` | `timetable_session.status`, `timetable_session.rescheduled_from` | `test_rescheduling.py` |
| **REQ-10** | Manual Roster Attendance (Present/Absent initial, extensible, Mode 1 & 2 UI support) | CONFIRMED | Attendance Capture Engine | `apps.attendance` | `attendance_record`, `attendance_session_state` | `test_attendance.py` |
| **REQ-11** | Conservative Lifecycle & Auto-Finalization (Draft -> Reviewed -> Finalized, never guess unrecorded) | CONFIRMED | State Machine Validator | `apps.attendance` | `attendance_session_state.status` | `test_attendance_lifecycle.py` |
| **REQ-12** | Hybrid Attendance Corrections (Faculty <=24h, older requires HOD approval, immutable audit log) | CONFIRMED | Correction & Workflow Service | `apps.corrections` | `corrections_request`, `audit_log` | `test_corrections.py` |
| **REQ-13** | Statutory 75% Calculation Engine (< 75% is alert, exactly 75.00% is safe, cancelled excluded) | CONFIRMED | Analytical Rules Engine | `apps.attendance` | Query Layer / Aggregate Views | `test_calculation.py` |
| **REQ-14** | Automated 75% Email Alerts (Immediate alert, weekly recurring reminder, state reset on recovery) | CONFIRMED | Notification Dispatcher | `apps.notifications` | `notifications_log`, `notifications_state` | `test_notifications.py` |
| **REQ-15** | Email Provider Abstraction (College SMTP, transactional providers, delivery tracking, retries) | CONFIRMED | Outbox Delivery Worker | `apps.notifications` | `notifications_outbox` | `test_email_provider.py` |
| **REQ-16** | Formal Academic Reports (Monthly, Semester, Subject-wise, Theory/Lab, A4 PDF, Word DOCX, CSV) | CONFIRMED | Document Generation Pipeline | `apps.reports` | `reports_generation_task` | `test_reports.py` |
| **REQ-17** | Offline Synchronization Engine (Idempotency keys, conflict detection, server-authoritative validation) | CONFIRMED | Offline Ingestion API | `apps.synchronization` | `sync_idempotency_log` | `test_offline_sync.py` |
| **REQ-18** | Comprehensive Institutional Audit Logging (Actor, action, timestamp, old/new diff, context) | CONFIRMED | System Audit Framework | `apps.audit` | `audit_entry` | `test_audit.py` |
| **REQ-19** | Hostinger Deployment & Portability (Modular monolith, systemd/docker, cloud-portable) | CONFIRMED | Container & WSGI Infra | `deployment/` | Config files | Deployment Verification |
