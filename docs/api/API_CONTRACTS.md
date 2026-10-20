# API Endpoints & Contracts Specification

**Document ID:** DOC-API-CON-001  
**Project:** College Attendance Management System  
**Base URL:** `/api/v1/`  
**Date:** October 2026  

---

## 1. Authentication (`/api/v1/auth/`)

### 1.1 Request OTP
- **Endpoint:** `POST /api/v1/auth/otp/request/`
- **Access:** Public (Rate-limited: 3 per 15 min)
- **Request Body:**
  ```json
  { "email": "faculty@college.edu" }
  ```
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "message": "One-Time Password has been transmitted to your verified institutional email.",
    "expires_in_seconds": 600
  }
  ```

### 1.2 Verify OTP & Obtain Session Token
- **Endpoint:** `POST /api/v1/auth/otp/verify/`
- **Access:** Public (Rate-limited: 3 attempts per OTP)
- **Request Body:**
  ```json
  {
    "email": "faculty@college.edu",
    "otp": "849201"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 12,
      "email": "faculty@college.edu",
      "full_name": "Prof. S. R. Kulkarni",
      "role": "FACULTY",
      "department": { "id": 1, "code": "IT", "name": "Information Technology" }
    }
  }
  ```

---

## 2. Academics, Students & Timetable

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/academics/departments/` | List departments | Any Authenticated |
| `POST` | `/api/v1/academics/departments/` | Create department | Admin |
| `GET` | `/api/v1/academics/subjects/` | List subjects (filtered by semester/dept) | Any Authenticated |
| `GET` | `/api/v1/students/` | List students (classroom view displays last-4 PRN) | Faculty/HOD/Admin |
| `POST` | `/api/v1/students/import/` | Upload Excel/CSV student roster file | Admin |
| `GET` | `/api/v1/rooms/` | List classrooms/labs with capacity & type | Any Authenticated |
| `GET` | `/api/v1/timetable/slots/` | List recurring weekly timetable slots | Any Authenticated |
| `POST` | `/api/v1/timetable/slots/` | Create slot (executes conflict checks) | HOD/Admin |
| `GET` | `/api/v1/timetable/sessions/` | List dated lecture sessions (date/faculty filter) | Any Authenticated |
| `POST` | `/api/v1/timetable/sessions/{id}/cancel/` | Cancel session with mandatory reason | Assigned Faculty/HOD/Admin |
| `POST` | `/api/v1/timetable/sessions/{id}/reschedule/`| Reschedule session preserving original slot | Assigned Faculty/HOD/Admin |

---

## 3. Attendance Roster & Offline Sync

### 3.1 Fetch Session Attendance Roster
- **Endpoint:** `GET /api/v1/attendance/sessions/{session_id}/roster/`
- **Access:** Assigned Faculty, HOD, Admin
- **Response `200 OK`:**
  ```json
  {
    "session": {
      "id": 105,
      "subject": "CS301 — Database Management Systems",
      "division": "Division A",
      "faculty": "Prof. S. R. Kulkarni",
      "date": "2026-10-05",
      "time": "10:00 - 11:00",
      "session_type": "THEORY",
      "status": "SCHEDULED",
      "state": "DRAFT"
    },
    "roster": [
      {
        "student_id": 401,
        "roll_number": "IT-01",
        "display_name": "0124 — Aarav Patel",
        "status": "PRESENT"
      },
      {
        "student_id": 402,
        "roll_number": "IT-02",
        "display_name": "0125 — Ananya Sharma",
        "status": "ABSENT"
      }
    ]
  }
  ```

### 3.2 Submit / Synchronize Attendance (Offline & Online)
- **Endpoint:** `POST /api/v1/sync/attendance/`
- **Access:** Assigned Faculty, HOD, Admin
- **Headers:** `X-Idempotency-Key: <UUID>`
- **Request Body:**
  ```json
  {
    "idempotency_key": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "session_id": 105,
    "client_timestamp": "2026-10-05T10:45:00Z",
    "structured_topic": "B-Tree and B+ Tree Indexing",
    "free_text_notes": "Covered node split operations and tree depth bounds.",
    "records": [
      { "student_id": 401, "status": "PRESENT" },
      { "student_id": 402, "status": "ABSENT" }
    ],
    "finalize": true
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "idempotency_key": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "session_id": 105,
    "status": "FINALIZED",
    "records_recorded": 2,
    "present_count": 1,
    "absent_count": 1
  }
  ```

---

## 4. Corrections, Calculations & Reports

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/corrections/request/` | Request correction (auto-applies if within 24h) | Faculty/HOD/Admin |
| `GET` | `/api/v1/corrections/pending/` | List pending corrections requiring review | HOD/Admin |
| `POST` | `/api/v1/corrections/{id}/review/` | Approve or reject correction request | HOD/Admin |
| `GET` | `/api/v1/analytics/attendance/summary/`| Real-time subject/division attendance % & <75% | Any Authenticated |
| `GET` | `/api/v1/reports/monthly/pdf/` | Export monthly A4 printable PDF report | Faculty/HOD/Admin |
| `GET` | `/api/v1/reports/monthly/docx/` | Export monthly editable Microsoft Word report | Faculty/HOD/Admin |
| `GET` | `/api/v1/reports/deficiency/csv/` | Export raw CSV of students below 75% threshold | HOD/Admin |
| `GET` | `/api/v1/audit/logs/` | Query immutable institutional audit trail | HOD/Admin |
