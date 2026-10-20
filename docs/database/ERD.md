# Entity-Relationship Diagram (ERD)

**Document ID:** DOC-DB-ERD-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Domain Entity Relationship Diagram

```mermaid
erDiagram
    DEPARTMENT ||--o{ PROGRAM : offers
    DEPARTMENT ||--o{ SUBJECT : manages
    DEPARTMENT ||--o{ USER : employs
    PROGRAM ||--o{ SEMESTER : structures
    ACADEMIC_YEAR ||--o{ SEMESTER : spans
    SEMESTER ||--o{ DIVISION : divides
    SEMESTER ||--o{ SUBJECT : includes
    DIVISION ||--o{ STUDENT : enrolls
    
    USER ||--o{ FACULTY_ALLOCATION : assigned
    SUBJECT ||--o{ FACULTY_ALLOCATION : requires
    DIVISION ||--o{ FACULTY_ALLOCATION : attends
    
    ROOM ||--o{ TIMETABLE_SLOT : hosts
    FACULTY_ALLOCATION ||--o{ TIMETABLE_SLOT : scheduled_in
    
    TIMETABLE_SLOT ||--o{ LECTURE_SESSION : instantiates
    LECTURE_SESSION ||--o| LECTURE_TOPIC : documents
    LECTURE_SESSION ||--o| SESSION_STATE : tracks_lifecycle
    LECTURE_SESSION ||--o{ ATTENDANCE_RECORD : records
    
    STUDENT ||--o{ ATTENDANCE_RECORD : receives_mark
    ATTENDANCE_RECORD ||--o{ CORRECTION_REQUEST : modified_by
    
    USER ||--o{ AUDIT_ENTRY : triggers
    STUDENT ||--o{ NOTIFICATION_OUTBOX : alerted_by
    USER ||--o{ SYNC_IDEMPOTENCY_LOG : syncs
```

---

## 2. Referential Integrity & Deletion Rules

| Parent Entity | Child Entity | Foreign Key Policy | Rationale |
| :--- | :--- | :--- | :--- |
| `Department` | `Subject` | `models.PROTECT` | Deleting a department with active/historical subjects is blocked. |
| `Subject` | `LectureSession` | `models.PROTECT` | Historical conducted sessions must never lose subject reference. |
| `Student` | `AttendanceRecord` | `models.PROTECT` | Departing students cannot cause cascading loss of attendance logs. |
| `LectureSession` | `AttendanceRecord` | `models.PROTECT` | Lecture attendance records cannot be deleted via session deletion. |
| `LectureSession` | `LectureTopic` | `models.CASCADE` | Topic log is a 1-to-1 extension of the session itself. |
| `LectureSession` | `SessionState` | `models.CASCADE` | Session lifecycle state is a 1-to-1 extension of the session. |
| `User` | `AuditEntry` | `models.SET_NULL` | If a user account is removed, audit logs remain with `actor=NULL` preserving history. |
