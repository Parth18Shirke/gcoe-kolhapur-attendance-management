# Offline Synchronization Architecture

**Document ID:** ARCH-SYNC-001  
**Project:** College Attendance Management System  
**Date:** October 2026  
**Classification:** HARD REQUIREMENT  

---

## 1. Classroom Reality & Guiding Invariant

College lecture halls and laboratories frequently suffer from dead zones, congested access points, and intermittent campus connectivity. Faculty must never be blocked from taking attendance due to network failure.

However:
> **INVARIANT: Offline client state must NEVER become the authoritative academic record.**

The server is the sole arbiter of attendance records, timestamp verification, student enrollments, timetable validity, and audit lineage.

---

## 2. Synchronization Lifecycle

```
[Online in Staffroom]
       │
       ▼
1. Pre-Fetch: Client downloads daily schedule, active sessions, and student roster cache.
       │
[Entering Offline Classroom]
       │
       ▼
2. Classroom Capture: Faculty opens session roster, marks Present/Absent, enters lecture topics.
       │
       ▼
3. Local Persistence: Client stores attendance state in IndexedDB / local queue with:
   - client_operation_id (UUIDv4 idempotency key)
   - session_id
   - timestamp
   - status entries list: [{ student_id, status }]
   - topics_covered text
       │
[Re-establishing Connectivity]
       │
       ▼
4. Transmission: Client posts batch to /api/v1/sync/attendance/
       │
       ▼
5. Server Verification & Reconciliation:
   ├── Check A: Has client_operation_id been processed? (If yes, return stored result -> Idempotent)
   ├── Check B: Is faculty user assigned/authorized for this session?
   ├── Check C: Is session currently in an editable state (not finalized/locked by HOD)?
   ├── Check D: Are all student IDs valid active members of the division?
   ├── Check E: Does submission conflict with any concurrent administrative action?
       │
       ├─► [VALID]: Atomically commit AttendanceRecords + AuditLog + Transition state -> Return 200 OK.
       │
       └─► [CONFLICT / INVALID]: Rollback -> Return 409 Conflict with structured error diff.
```

---

## 3. Idempotency Key Architecture

Every offline submission payload must supply:
`idempotency_key`: `UUIDv4`

The backend tracks all processed operations in the `SyncIdempotencyLog` table:
- `idempotency_key` (Primary Key / Unique Index)
- `user_id` (Actor who initiated sync)
- `session_id` (Target lecture session)
- `status` (`SUCCESS`, `CONFLICT`, `REJECTED`)
- `response_payload` (Cached JSON response)
- `created_at` (Timestamp)

If network interruption causes the client to retry the POST request, the backend detects the existing `idempotency_key`, bypasses redundant writes, and returns the cached outcome immediately. This guarantees that duplicate network transmissions can never create duplicate attendance rows.

---

## 4. Conflict Resolution Strategy

| Conflict Scenario | Detection Rule | Server Resolution Policy |
| :--- | :--- | :--- |
| **Session Finalized by HOD** | Target session `status == 'FINALIZED'` or locked before sync arrives. | **Reject submission.** Return `409 Conflict`. Server state is preserved; client is notified that session was finalized administratively. |
| **Session Cancelled** | Target session `status == 'CANCELLED'`. | **Reject submission.** Cancelled sessions cannot receive attendance. Return `422 Unprocessable Entity`. |
| **Stale Student Roster** | Student in client payload was transferred/dropped from division. | **Partial commit with warnings** or reject batch depending on configuration. Standard policy: ignore dropped student, commit valid students, return warnings in response. |
| **Duplicate Student Marks** | Same `student_id` listed twice in single payload. | Sanitizer validates uniqueness in request payload before writing; rejects payload if contradictory marks exist. |
