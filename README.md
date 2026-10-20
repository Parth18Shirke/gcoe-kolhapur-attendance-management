# College Attendance Management System (AMS)

A robust, production-ready, server-authoritative institutional web platform engineered for real college operations.

---

## 1. System Vision & Architecture

The **Attendance Management System (AMS)** replaces error-prone paper registers and ad-hoc spreadsheets with a secure, auditable, and regulatory-compliant digital system. It features:
- **Server-Authoritative Core:** Official attendance percentages, timetable rules, statutory 75% thresholds, permissions, and audit logs are computed strictly on the backend.
- **Offline-First Synchronization:** Classroom attendance can be marked offline by faculty on smartphones/tablets and synchronized via idempotent, conflict-detecting APIs upon reconnection.
- **Privacy-by-Design:** Classroom attendance rosters display only the **last 4 digits of PRN + Student Name** (e.g. `1234 — Rahul Sharma`), hiding full PRNs from routine classroom view.
- **Passwordless Institutional Auth:** Secure Email OTP (6-digit, 10-minute expiry, rate-limited, brute-force protected) with an extensible provider abstraction ready for future Google/M365 SSO or LDAP.
- **Multi-Format Reporting:** Generates pixel-perfect **A4 printable PDFs**, editable **Microsoft Word (`.docx`)** documents with official institutional headers and signatures, and **CSV** data exports.

---

## 2. Technology Stack

- **Backend:** Python 3.11+, Django 5.2+, Django REST Framework 3.18+
- **API Documentation:** OpenAPI 3.0 / Swagger via `drf-spectacular`
- **Database:** PostgreSQL 15+ (Production) / SQLite (Dev & Testing)
- **Document Engines:** `python-docx` (Native Word documents), `ReportLab` (A4 PDFs), `openpyxl` (Excel ingestion)
- **Test Runner:** `pytest` + `pytest-django` (29 comprehensive automated tests)
- **Deployment:** Linux VPS (Hostinger), Nginx, Gunicorn, systemd

---

## 3. Directory Structure

```text
attendance_management_system/
├── backend/
│   ├── config/              # Project settings, URL routing, WSGI/ASGI gateways
│   ├── apps/
│   │   ├── common/          # Base models, custom permissions, unified error handling
│   │   ├── accounts/        # Custom user model, Email OTP, Bearer token auth, rate limits
│   │   ├── academics/       # Departments, programs, semesters, divisions, subjects
│   │   ├── students/        # Student master, PRN privacy, CSV/Excel ingestion
│   │   ├── faculty/         # Faculty workload and subject allocation
│   │   ├── rooms/           # Classrooms, labs, and capacity management
│   │   ├── timetable/       # Recurring slots, sessions, conflict detection, reschedule lineage
│   │   ├── attendance/      # Roster capture, Mode 1 & 2, conservative finalization, 75% engine
│   │   ├── corrections/     # Hybrid 24h faculty self-correction + HOD approval workflow
│   │   ├── notifications/   # Threshold 75% alerts, cooldown throttling, email outbox worker
│   │   ├── reports/         # A4 PDF, Word DOCX, and CSV report builders
│   │   ├── synchronization/ # Offline sync API, UUID idempotency, conflict detection
│   │   └── audit/           # Append-only institutional audit trail (immutable)
│   ├── tests/               # 29 automated test cases (pytest)
│   ├── manage.py            # Django management CLI
│   ├── pytest.ini           # Pytest configuration
│   └── requirements.txt     # Python backend dependencies
│
├── docs/                    # Complete institutional engineering documentation
│   ├── requirements/        # Requirements baseline, ambiguity register, traceability
│   ├── architecture/        # Architecture diagrams, tech stack, offline sync, auth, ADRs
│   ├── database/            # Database schema design, ERD, data ownership boundaries
│   ├── api/                 # API overview, endpoint contracts, unified error model
│   ├── deployment/          # Deployment guide, Hostinger requirements, backup & recovery
│   └── testing/             # Test strategy and backend test plan register
│
├── archive/                 # Isolated historical reference materials (v0.1 preliminary)
├── .env.example             # Documented configuration template
├── manage.py                # Root convenience wrapper
├── pytest.ini               # Root test runner configuration
└── schema.yml               # Generated OpenAPI 3.0 specification
```

---

## 4. Local Development Setup

### 4.1 Prerequisites
- Python 3.11 or 3.12
- Git

### 4.2 Installation
```bash
# 1. Clone repository and navigate to folder
cd attendance_management_system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Apply database migrations
python manage.py migrate

# 5. Seed clean development/test academic fixtures (OPTIONAL - DEV ONLY)
python manage.py seed_development_data
```

### 4.3 Running the Development Server
```bash
python manage.py runserver 8000
```
- API Base URL: `http://127.0.0.1:8000/api/v1/`
- Interactive Swagger UI: `http://127.0.0.1:8000/api/v1/docs/`
- ReDoc Documentation: `http://127.0.0.1:8000/api/v1/redoc/`
- OpenAPI Raw Schema: `http://127.0.0.1:8000/api/v1/schema/`
- Django Admin: `http://127.0.0.1:8000/admin/`

---

## 5. Automated Testing

The backend includes 29 comprehensive test cases covering authentication, RBAC, timetable conflicts, offline synchronization, attendance calculations, conservative finalization, and document exports.

Run all tests:
```bash
pytest
```

---

## 6. Authentication Workflow (Email OTP)

The system uses passwordless Email OTP:
1. **Request OTP:** `POST /api/v1/auth/otp/request/` with `{"email": "faculty@college.edu"}`
   - Transmits a 6-digit numeric code to the institutional email.
   - Enforces rate limiting (max 3 requests per 15 minutes).
2. **Verify OTP:** `POST /api/v1/auth/otp/verify/` with `{"email": "...", "otp": "..."}`
   - Returns a 64-character bearer token valid for 30 days.
   - Brute-force protected (invalidated after 3 incorrect attempts).
3. **Authenticated Requests:** Include `Authorization: Bearer <token>` in HTTP headers.

---

## 7. Key Domain Subsystems

### 7.1 Conservative Auto-Finalization
When finalizing an attendance session:
> **UNMARKED STUDENTS ARE NEVER GUESSED.**
If any enrolled student remains unmarked, the system flags the session as `INCOMPLETE_RECORDS` and refuses to auto-fill them as Present or Absent.

### 7.2 Hybrid Attendance Corrections
- **Within 24 Hours:** Faculty who conducted the session can correct mistakes directly; changes are logged immediately in the immutable audit trail.
- **After 24 Hours / Locked Sessions:** Automatically routes to a `CorrectionRequest` requiring formal review and approval by the Head of Department (HOD).

### 7.3 Offline Attendance Synchronization
- Offline clients generate a UUID `idempotency_key` per submission.
- When network is restored, client posts to `/api/v1/sync/attendance/`.
- Duplicate submissions return cached responses without double-marking.
- Submissions against cancelled or finalized sessions return structured `409 Conflict` errors.

### 7.4 75% Statutory Rules & Notifications
- Calculation: $\text{Attendance \%} = (\text{Attended} / \text{Conducted}) \times 100$.
- Cancelled sessions are excluded from the denominator.
- Exactly $75.00\%$ is compliant; $< 75.00\%$ triggers an immediate warning email followed by a weekly reminder cycle (7-day cooldown).
- When a student's percentage recovers to $\ge 75.00\%$, the deficiency state resets automatically.

---

## 8. Deployment Overview

For full production deployment instructions targeting Hostinger Linux VPS with Nginx, Gunicorn, systemd, and PostgreSQL, refer to [`docs/deployment/DEPLOYMENT.md`](docs/deployment/DEPLOYMENT.md).
