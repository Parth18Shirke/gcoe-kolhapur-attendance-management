# Database Design & Schema Architecture

**Document ID:** DOC-DB-001  
**Project:** College Attendance Management System  
**Engine:** PostgreSQL 15+ (SQLite for local testing/dev)  
**Date:** October 2026  

---

## 1. Schema Design Principles

1. **Strict Referential Integrity:** Foreign keys enforce valid academic relationships. Cascading deletions on core academic records (`Department`, `Subject`, `Student`, `LectureSession`) are strictly prohibited (`on_delete=models.PROTECT`) to preserve academic history.
2. **Composite Uniqueness:** Prevents logical corruption (e.g., `UNIQUE (session_id, student_id)` on `AttendanceRecord`).
3. **Audit Immutability:** Historical audit records and correction logs are append-only.
4. **Normalized Structure:** 3NF structure balancing query performance with clean integrity constraints.

---

## 2. Core Entity Tables

### 2.1 Accounts & Authentication
- `accounts_user`: Custom user model. Fields: `id`, `email` (unique), `full_name`, `role` (`ADMIN`, `HOD`, `FACULTY`), `department_id` (nullable), `is_active`, `created_at`.
- `accounts_email_otp`: Hashed OTP challenges. Fields: `id`, `user_id`, `otp_hash`, `expires_at`, `attempts_remaining`, `is_used`, `created_at`.

### 2.2 Academic Hierarchy
- `academics_department`: `id`, `name`, `code` (unique, e.g. `IT`, `CS`), `is_active`.
- `academics_program`: `id`, `department_id`, `name`, `code` (e.g. `B.Tech`), `duration_years`.
- `academics_academic_year`: `id`, `name` (e.g. `2026-2027`), `start_date`, `end_date`, `is_current`.
- `academics_semester`: `id`, `academic_year_id`, `program_id`, `semester_number` (1–8), `term_type` (`ODD`, `EVEN`).
- `academics_division`: `id`, `semester_id`, `name` (e.g. `Division A`), `academic_year_id`.
- `academics_subject`: `id`, `department_id`, `semester_id`, `name`, `code` (e.g. `CS301`), `subject_type` (`THEORY`, `LAB`, `BOTH`), `is_active`.

### 2.3 Students & Privacy
- `students_student`: `id`, `prn` (unique, full university number), `roll_number`, `full_name`, `official_email` (unique), `division_id`, `status` (`ACTIVE`, `INACTIVE`, `ARCHIVED`), `created_at`.
- `students_import_log`: `id`, `uploaded_by_id`, `file_name`, `total_rows`, `imported_count`, `error_count`, `error_details` (JSON), `created_at`.

### 2.4 Faculty Allocations & Rooms
- `rooms_room`: `id`, `name` (e.g. `Room 204`, `Lab 3`), `room_type` (`CLASSROOM`, `LAB`, `SEMINAR_HALL`), `capacity`, `is_active`.
- `faculty_workload_allocation`: `id`, `faculty_id`, `subject_id`, `division_id`, `academic_year_id`, `is_primary`.

### 2.5 Timetable & Lecture Sessions
- `timetable_slot`: Recurring weekly timetable rule. Fields: `id`, `academic_year_id`, `division_id`, `subject_id`, `faculty_id`, `room_id`, `day_of_week` (0=Monday...6=Sunday), `start_time`, `end_time`, `session_type` (`THEORY`, `LAB`), `is_active`.
- `timetable_session`: Concrete scheduled/conducted session. Fields: `id`, `slot_id` (nullable for unscheduled ad-hoc lectures), `division_id`, `subject_id`, `faculty_id`, `room_id`, `session_date`, `start_time`, `end_time`, `duration_minutes`, `session_type` (`THEORY`, `LAB`), `status` (`SCHEDULED`, `CONDUCTED`, `CANCELLED`), `rescheduled_from_id` (nullable link), `cancellation_reason` (text), `cancelled_by_id` (nullable).
- `timetable_topic_log`: `id`, `session_id` (unique), `structured_topic`, `free_text_notes`, `created_at`.

### 2.6 Attendance & Lifecycle
- `attendance_session_state`: `id`, `session_id` (unique), `status` (`DRAFT`, `REVIEWED`, `FINALIZED`, `INCOMPLETE_RECORDS`), `finalized_by_id` (nullable), `finalized_at` (nullable).
- `attendance_record`: `id`, `session_id`, `student_id`, `status` (`PRESENT`, `ABSENT`), `marked_by_id`, `created_at`, `updated_at`. `UNIQUE (session_id, student_id)`.

### 2.7 Corrections & Approvals
- `corrections_request`: `id`, `attendance_record_id`, `requested_by_id`, `original_status`, `new_status`, `reason`, `status` (`PENDING`, `APPROVED`, `REJECTED`), `reviewed_by_id`, `reviewed_at`, `review_remarks`, `created_at`.

### 2.8 Notifications & Audit
- `notifications_outbox`: `id`, `recipient_email`, `student_id`, `notification_type` (`THRESHOLD_75_WARNING`, `CORRECTION_ALERT`), `subject`, `body_text`, `status` (`PENDING`, `SENT`, `FAILED`), `retry_count`, `error_message`, `sent_at`, `created_at`.
- `audit_entry`: `id`, `actor_id` (nullable for system), `action_type` (`CREATE`, `UPDATE`, `DELETE`, `FINALIZE`, `CORRECT`, `OVERRIDE`), `entity_name`, `entity_id`, `old_values` (JSON), `new_values` (JSON), `reason`, `client_ip`, `created_at`.
- `sync_idempotency_log`: `idempotency_key` (UUID, PK), `user_id`, `session_id`, `status`, `response_payload` (JSON), `created_at`.
