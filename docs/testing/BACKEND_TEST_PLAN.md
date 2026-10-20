# Backend Test Plan & Test Case Register

**Document ID:** DOC-TST-PLN-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Test Suite Modules

| Test Module | Coverage Scope | Target Test Cases |
| :--- | :--- | :--- |
| `tests/test_auth.py` | OTP request, verification, expiry, brute force lockout, rate limit. | TC-AUTH-01 through TC-AUTH-07 |
| `tests/test_rbac.py` | Role barriers for Admin, HOD, and Faculty endpoints. | TC-RBAC-01 through TC-RBAC-05 |
| `tests/test_academics.py`| Academic hierarchy, Department, Semester, Subject, Division models. | TC-ACAD-01 through TC-ACAD-04 |
| `tests/test_students.py` | Student privacy (last-4 PRN display), enrollment, CSV/Excel import. | TC-STUD-01 through TC-STUD-05 |
| `tests/test_timetable.py`| Slots, sessions, conflict detection (faculty, room, division), override. | TC-TIME-01 through TC-TIME-08 |
| `tests/test_attendance.py`| Manual roster capture, Mode 1 & Mode 2, conservative finalization. | TC-ATT-01 through TC-ATT-07 |
| `tests/test_calculation.py`| 75% calculation engine, boundary checks (75.00% vs 74.99%), cancelled exclusion. | TC-CALC-01 through TC-CALC-05 |
| `tests/test_corrections.py`| Faculty 24h self-correction, HOD approval workflow, immutable audit log. | TC-CORR-01 through TC-CORR-06 |
| `tests/test_offline_sync.py`| Idempotency keys, duplicate submissions, conflict detection. | TC-SYNC-01 through TC-SYNC-05 |
| `tests/test_notifications.py`| 75% outbox queueing, recovery reset, recurring cooldown, email retry. | TC-NOTIF-01 through TC-NOTIF-06 |
| `tests/test_reports.py` | A4 PDF, Word DOCX, and CSV report builders. | TC-REP-01 through TC-REP-04 |
| `tests/test_audit.py` | Append-only audit trail logging for institutional operations. | TC-AUD-01 through TC-AUD-04 |
