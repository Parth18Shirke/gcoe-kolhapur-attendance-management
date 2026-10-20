# Attendance Management System — Requirements Baseline (v2.0 Frozen)

**Document ID:** REQ-BASE-002  
**Version:** 2.0 — Requirements Baseline Freeze  
**Date:** October 2026  
**Status:** Approved Requirements Baseline  
**Target Environment:** College / Higher Education Institutional Deployment  

---

## 1. System Vision & Purpose `[CONFIRMED]`

The **College Attendance Management System (AMS)** is an institutional-grade, server-authoritative web platform engineered to modernize student attendance recording, curricular lecture tracking, regulatory 75% threshold compliance, and official academic reporting.

The system is designed for real institutional deployment initially targeting a **Hostinger** Linux environment, with zero vendor lock-in, long-term portability, offline-first client synchronization support, and a single REST API supporting future React PWA and React Native (Expo) mobile applications.

---

## 2. Institutional Roles & Server-Authoritative RBAC `[CONFIRMED]`

Authorization is strictly enforced server-side. Frontend role representations are purely cosmetic.

### 2.1 Faculty ("Sir")
- View assigned classes, subjects, and timetable slots.
- Take manual classroom attendance.
- Record lecture delivered topics (structured syllabus points + free-text notes).
- Perform recent attendance corrections within the **24-hour** grace window.
- Cancel or reschedule their own assigned sessions with mandatory justification.
- View subject-wise and division-wise attendance summaries and reports.
- Support offline attendance recording on client devices with subsequent synchronization.

### 2.2 Head of Department (HOD)
- Departmental oversight across all faculty, subjects, and divisions.
- Review and approve/reject restricted attendance correction requests (older than 24 hours).
- Manage, adjust, and override schedules and timetable allocations.
- Cancel or reschedule any departmental session.
- Access and export department-wide monthly, semester, and deficiency (<75%) reports.
- Configure departmental attendance policy overrides.

### 2.3 System Administrator (Admin)
- System-wide administrative governance and user/role management.
- Academic master catalog management (Departments, Programs, Academic Years, Semesters, Divisions, Subjects, Rooms).
- Student enrollment data ingestion, validation, and reconciliation.
- Faculty workload assignment.
- System parameter configuration (SMTP settings, threshold rules, retention policies).
- Audit trail review, data export, and disaster recovery execution.

### 2.4 Students `[CONFIRMED - CURRENT REQUIREMENT]`
- **No System Accounts:** Students do **NOT** have user accounts or login access in this phase.
- Students exist strictly as academic profile records in the institutional database.
- Students interact with the platform passively via automated **college email notifications**.
- Any future student self-service portal or check-in mechanism is strictly `[FUTURE]`.

---

## 3. Student Identity & Privacy `[CONFIRMED]`

### 3.1 Data Ownership Boundary
- **College-Authoritative:** University PRN (Permanent Registration Number) / Student ID, full legal name, program, branch, academic year, semester, division, official college email, enrollment status.
- **System-Authoritative:** Lecture sessions, attendance marks, draft/finalization states, correction requests, approvals, calculation metrics, notification history, and audit trails.
- Synchronization from the external college master will **never overwrite or destroy attendance history**.

### 3.2 Student Record Lifecycle
- Student records support states: `ACTIVE`, `INACTIVE`, `ARCHIVED`.
- Graduated, suspended, or departing students are transitioned to `ARCHIVED` or `INACTIVE`; student history and historical attendance records are **never physically deleted**.

### 3.3 PRN Classroom Privacy Standard
- Full PRN is retained in the database for official university reporting and institutional identification.
- In everyday classroom attendance rosters, the UI displays only the **Student Name + last 4 digits of PRN** (e.g., `1234 — Rahul Sharma`).
- Full PRN exposure is restricted to administrative and official report generation endpoints.

---

## 4. Authentication Architecture: Email OTP `[CONFIRMED]`

### 4.1 Zero Passwords Initially
- To eliminate password-related institutional vulnerabilities (weak passwords, credential stuffing, credential sharing), authentication operates exclusively via **One-Time Passwords (OTP) transmitted to verified institutional email addresses**.

### 4.2 Security Specification
- **Length:** 6-digit cryptographically secure numeric token (`secrets.choice`).
- **Lifespan:** Valid for exactly **10 minutes**.
- **Usage:** Single-use only; immediately invalidated upon verification or upon issuance of a replacement OTP.
- **Storage:** Stored in the database as a salted cryptographic hash (never plaintext).
- **Brute-Force Protection:** Maximum **3 failed verification attempts** per OTP before invalidation.
- **Rate Limiting:** Maximum **3 OTP requests per 15-minute window** per email address / IP address.
- **Session Tokens:** Successful verification issues an expiring JSON Web Token (JWT) or secure bearer token containing user identity and role.
- **Extensibility Abstraction:** The authentication subsystem sits behind an abstract `AuthenticationProvider` interface so institutional OIDC, Google Workspace / Microsoft 365 OAuth2, or LDAP can be added without modifying domain logic.

---

## 5. Timetable, Sessions & Room Management `[CONFIRMED]`

### 5.1 Timetable Planning
- Supports recurring weekly timetable slots linked to Academic Year, Semester, Department, Subject, Division, Faculty, Room, Day of Week, Start Time, and End Time.
- Specific calendar dates instantiate concrete `LectureSession` instances from the recurring slots.

### 5.2 Session Classification: Theory vs Lab / Practical
- **Theory Sessions:** Standard classroom lectures (typically single period).
- **Lab / Practical Sessions:** Extended laboratory sessions spanning multiple periods.
- The domain model explicitly stores session duration in minutes / periods rather than assuming 1-hour slots.
- Attendance calculations evaluate Theory %, Lab %, and Overall Subject % with configurable weighting.

### 5.3 Rooms & Conflict Detection
- Master room catalog: Classrooms, Lecture Halls, Laboratories with capacity and equipment tags.
- **Automated Conflict Engine:** Detects scheduling collisions across three dimensions:
  1. **Faculty Conflict:** Faculty scheduled in two sessions simultaneously.
  2. **Division Conflict:** Class/Division scheduled in two sessions simultaneously.
  3. **Room Conflict:** Room allocated to two sessions simultaneously.
- **Conflict Policy:** The system **blocks** conflicting scheduling operations by default. Authorized HOD/Admin users may supply an explicit override justification.

### 5.4 Timetable Grace Period
- Attendance capture outside the scheduled time window is tracked via a configurable grace period (e.g., within 2 hours or same calendar day).
- Sessions marked outside the window record a `TIMETABLE_WINDOW_WARNING` flag in the session audit log without hard-blocking faculty in classroom situations.

### 5.5 Cancellation & Rescheduling
- **Cancellation:** Faculty can cancel their own sessions; HOD/Admin can cancel any session. Cancelled sessions remain permanently in the database with status `CANCELLED`, recording actor, timestamp, and mandatory reason. By default, cancelled sessions are excluded from the attendance calculation denominator.
- **Rescheduling:** Rescheduling does **not** overwrite the original session. The system preserves the original session, creates a rescheduling link, and generates a new scheduled session referencing the original.

---

## 6. Manual Attendance Roster & Lifecycle `[CONFIRMED]`

### 6.1 Faculty Attendance Capture
- Attendance is recorded manually by faculty using touch-friendly roster toggles.
- Supports two initial UI modes per session:
  - **Mode 1 (Default Present):** All students initialized as Present; faculty rapidly marks absentees.
  - **Mode 2 (Default Absent):** All students initialized as Absent; faculty marks attendees.
- The backend accepts the resulting state idempotently regardless of which mode was utilized.
- Status values: `PRESENT`, `ABSENT`. The domain model utilizes an extensible choice enum allowing future statuses (`LATE`, `ON_DUTY`, `MEDICAL`) without schema refactoring.

### 6.2 Session Lifecycle & Conservative Auto-Finalization
```text
DRAFT  ──(Faculty Review)──>  REVIEWED  ──(Submission/Lock)──>  FINALIZED
```
- **Conservative Finalization Rule:** If students remain unmarked when a session is finalized or auto-finalized:
  > **NEVER GUESS UNMARKED STUDENTS.**
  - Unmarked students are **never** auto-converted to Present or Absent.
  - The session is flagged with status `INCOMPLETE_RECORDS` and requires explicit faculty or HOD resolution.

---

## 7. Attendance Corrections & Audit Governance `[CONFIRMED]`

### 7.1 Hybrid Correction Policy
- **Faculty Self-Correction:** Faculty may directly correct attendance records within **24 hours** of session completion/finalization.
- **HOD Approval Required:** Any correction requested after 24 hours, or for an administratively locked session, creates a formal `CorrectionRequest` requiring HOD review and approval.

### 7.2 Immutable Audit Trail
- All modifications generate an append-only `AttendanceAuditLog` capturing:
  - Student, Lecture Session, Old Status, New Status, Initiating Actor, Approving Actor, Timestamp, Reason / Justification, and Client IP.
- Historical audit records cannot be edited or deleted under any circumstance.

---

## 8. Attendance Calculation & 75% Statutory Rules `[CONFIRMED]`

### 8.1 Calculation Formula
$$\text{Attendance \%} = \left( \frac{\text{Conducted Lectures Attended}}{\text{Total Conducted Lectures Scheduled - Cancelled Lectures}} \right) \times 100$$
- Exactly **$75.00\%$** is compliant.
- Anything strictly below **$75.00\%$** (e.g. $74.99\%$) triggers non-compliant status.

### 8.2 Notification Cycle & Anti-Spam Control
1. **Immediate Alert:** As soon as an attendance submission or correction causes a student's percentage to drop below $75.00\%$, an initial warning email is queued.
2. **Periodic Reminders:** If the student remains $< 75.00\%$, reminder notices are dispatched at a configurable interval (default: weekly, 7-day cooldown).
3. **State Reset:** If the student attends subsequent lectures and their percentage recovers to $\ge 75.00\%$, the deficiency state resets to `COMPLIANT`.
4. **Subsequent Drop:** If attendance later drops below $75.00\%$ again, a fresh warning cycle initiates.
5. **Recipient:** Student's official college email initially; extensible to CC Class Coordinators or HOD.

---

## 9. Offline-First Synchronization Architecture `[CONFIRMED HARD REQUIREMENT]`

### 9.1 Core Invariant
> **Offline client state must NEVER become the authoritative academic record.**
The server remains the sole validator and authority.

### 9.2 Synchronization Protocol
- Client downloads required session rosters while online.
- When offline in classroom, faculty marks attendance and commits to local client storage.
- Each submission batch generates a client-side **UUID Idempotency Key**.
- When network reconnects, client posts batch to `/api/v1/sync/attendance/`.
- Server validates:
  1. Idempotency Key (prevents duplicate submission on retry).
  2. Faculty authorization for the session.
  3. Session status (not already finalized/locked by HOD).
  4. Student enrollment validity.
  5. Timestamp sanity check against grace period.
- If valid, commits atomically and returns success receipt. If conflict occurs, server returns structured conflict payload without corrupting existing records.

---

## 10. Reporting Pipeline `[CONFIRMED]`

- **A4 Printable PDF:** Official institutional reports rendered with exact 15mm margins, college header, tabular attendance grid, summary statistics, and signature hierarchy (Teacher, HOD, Principal).
- **Microsoft Word (`.docx`):** Fully formatted editable Word documents matching administrative archival workflows.
- **CSV Data Export:** Raw tabular export for administrative data analysis.
- **Report Types:** Monthly Subject/Division Grid, Semester Consolidated Summary, Subject-wise Deficiency (<75%) Warning List, Faculty Conduction Log.

---

## 11. Email Subsystem & Provider Abstraction `[CONFIRMED]`

- Abstract `EmailService` interface supporting:
  - College SMTP Relay (TLS/SSL, authenticated).
  - Transactional Email APIs (Amazon SES, SendGrid, etc.).
  - Console / In-Memory Mock (Development and automated testing).
- Persistent `NotificationOutbox` table tracking: Recipient, Subject, Body, Timestamp, Delivery Status (`PENDING`, `SENT`, `FAILED`), Retry Count, Error Log.
- Database-backed retry worker with exponential backoff (no mandatory Redis requirement).
