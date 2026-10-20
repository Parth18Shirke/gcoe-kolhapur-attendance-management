# Technology Architecture & Evaluation Decision

**Document ID:** ARCH-DEC-001  
**Version:** 1.0  
**Date:** September 27, 2026  
**Status:** Architecture Recommendation (Subject to Hostinger Plan Confirmation)  
**System:** College Attendance Management System  

---

## 1. Architectural Goals & Guiding Principles

The Attendance Management System is an institutional software solution intended for real college operation. The architecture is guided by six non-negotiable principles:

1. **Server-Authoritative Integrity:** The backend is the sole source of truth for attendance percentages, threshold compliance (<75%), schedule validation, access control, and audit logs. The client never calculates official institutional records.
2. **Strict Simplicity (No Over-Engineering):** Avoid premature distributed architectures. No Kubernetes, no microservices, no Kafka, no mandatory Redis/Celery infrastructure unless proven necessary by operational constraints. A clean **Modular Monolith** is adopted.
3. **Institutional Reporting First-Class Citizen:** Generating pixel-perfect A4 printable sheets and native Microsoft Word (`.docx`) files with official headers, tables, and signature blocks is a primary requirement, not an afterthought.
4. **Hardware & Infrastructure Portability:** The system must run smoothly on the college's available Hostinger subscription while remaining 100% cloud-agnostic (easily migratable to AWS, Azure, DigitalOcean, or an on-premise college server).
5. **Classroom Device Agnosticism:** Faculty must be able to record attendance effortlessly on personal smartphones, classroom tablets, laptops, or staff-room desktops.
6. **Immutable Auditability:** Any post-submission modification to attendance records must be permanently logged in an append-only store with user identity, timestamp, and justification.

---

## 2. Infrastructure Constraints & Hostinger Realities

### 2.1 Hostinger Environment Assessment
- **Known Factor:** The college has an active Hostinger subscription.
- **Critical Unknown (P0):** The exact plan tier has not yet been confirmed by college administration:
  - *Tier 1: Hostinger KVM VPS (Linux Root Access).* Supports Docker, PostgreSQL 15+, systemd daemons, Nginx reverse proxy, and custom runtime environments. This is the optimal institutional deployment target.
  - *Tier 2: Hostinger Cloud / Shared Web Hosting (Managed hPanel).* Provides limited SSH, shared resources, MySQL by default (PostgreSQL may require external hosting or add-ons), no root access, and restricted background daemons.
- **Architectural Mitigation:** The system must be engineered so that:
  - Under a VPS: Deployed via lightweight Docker Compose or standard systemd services.
  - Under Shared/Cloud Hosting: Can operate using standard WSGI/ASGI configurations with database-backed queues rather than memory-heavy background brokers.

---

## 3. Candidate Architectures Evaluated

Four viable technology architectures were rigorously evaluated against the project's institutional constraints:

- **Option A: Django + Django REST Framework + React / TypeScript (SPA/PWA) + PostgreSQL**  
  Decoupled modern architecture: Python/Django backend exposing REST APIs, coupled with a React/TypeScript client running as a Progressive Web App.
- **Option B: Django Monolith + Django Templates + HTMX / Alpine.js + PostgreSQL**  
  Server-rendered monolith: HTML rendered directly by Django views, enhanced with HTMX/Alpine for dynamic interactive UI without a separate JavaScript build toolchain.
- **Option C: Node.js / NestJS + React / TypeScript + PostgreSQL**  
  Full-stack TypeScript architecture: NestJS backend utilizing TypeORM/Prisma with a React/TypeScript frontend.
- **Option D: FastAPI + React / TypeScript + PostgreSQL**  
  Python async micro-framework: FastAPI for high-performance async REST endpoints, SQLAlchemy ORM, and React frontend.

---

## 4. Evaluation Matrix

Each candidate was evaluated across 17 criteria ranked by institutional importance:

| Evaluation Criterion | Importance | Option A: Django + DRF + React/TS | Option B: Django + Templates/HTMX | Option C: NestJS + React/TS | Option D: FastAPI + React/TS |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Hostinger Deployment** | **Critical** | **High** (Standard WSGI/Static) | **Highest** (Single service) | **Medium** (Node on Hostinger varies) | **Medium-High** (Uvicorn ASGI) |
| **Web Browser Support** | **Critical** | **Highest** | **High** | **Highest** | **Highest** |
| **Mobile / Tablet UX** | **High** | **Highest** (Touch-native UI) | **Medium** (HTML re-render latency) | **Highest** (Touch-native UI) | **Highest** (Touch-native UI) |
| **PWA Capability** | **High** | **Highest** (Clean client cache) | **Medium-Low** (SSR offline complexity)| **Highest** (Clean client cache) | **Highest** (Clean client cache) |
| **Offline Queueing** | **High** | **High** (IndexedDB client queue)| **Low** (Hard to queue SSR forms) | **High** (IndexedDB client queue)| **High** (IndexedDB client queue)|
| **PostgreSQL Support** | **Critical** | **Highest** (Django ORM native) | **Highest** (Django ORM native) | **High** (Prisma / TypeORM) | **High** (SQLAlchemy / Alembic) |
| **Authentication Engine**| **High** | **Highest** (Django Auth / Knox) | **Highest** (Built-in session auth) | **Medium** (Passport/JWT manual) | **Medium** (Custom OAuth/JWT setup) |
| **Role-Based Access (RBAC)**| **Critical**| **Highest** (Django Permissions) | **Highest** (Django Permissions) | **Medium-High** (CASL/Guards) | **Medium** (Custom dependency guards) |
| **A4 PDF & Word DOCX** | **Critical** | **Highest** (`python-docx`, ReportLab)| **Highest** (`python-docx`, ReportLab)| **Low-Medium** (`docx` npm is clunky) | **Highest** (`python-docx`, ReportLab)|
| **Auditability & ORM Signals**|**Critical**| **Highest** (Django signals/audit) | **Highest** (Django signals/audit) | **Medium** (Subscriber hooks) | **Medium-High** (SQLAlchemy events) |
| **Maintainability** | **Critical** | **High** (Clear separation) | **High** (Single codebase) | **Medium** (Node dependency drift) | **Medium** (Boilerplate glue) |
| **Development Complexity**| **High** | **Medium** (Two sub-projects) | **Lowest** (Single codebase) | **Medium-High** (NestJS ceremony) | **Medium** (Async/ORM complexity) |
| **Runtime Performance** | **High** | **High** (Sufficient for college) | **High** (Low server overhead) | **Highest** (V8 event loop) | **Highest** (Async event loop) |
| **Security Defaults** | **Critical** | **Highest** (Django security battery)| **Highest** (Django security battery)| **Medium** (Manual middleware) | **Medium** (Manual middleware) |
| **Future Native Mobile** | **Medium** | **Highest** (Reuses DRF API & types)| **Low** (Must rewrite API from scratch)| **Highest** (Reuses API & types) | **Highest** (Reuses API & types) |
| **Portability** | **High** | **Highest** (Runs anywhere) | **Highest** (Runs anywhere) | **High** (Runs anywhere) | **Highest** (Runs anywhere) |
| **Team Learning Curve** | **Medium** | **Low-Medium** (Industry standard) | **Low** (Python + HTML) | **Medium** (TypeScript backend) | **Medium** (Pydantic + Async ORM) |

---

## 5. Architectural Comparison Analysis

### Why Option C (NestJS + React) Was Rejected
1. **Document Generation Deficit:** A mandatory requirement is generating official A4 printable reports and editable Microsoft Word (`.docx`) files with complex academic formatting, merged timetable cells, and institutional signature blocks. Python's `python-docx` library is by far the most mature, reliable, and robust tool for this task. Node.js alternatives (`docx` npm package) are noticeably less capable and notoriously painful to maintain for complex multi-table layouts.
2. **Institutional Data Modeling:** Django's ORM, schema migration framework, and built-in administrative data governance provide superior out-of-the-box auditability and relational constraint enforcement compared to TypeORM/Prisma.

### Why Option D (FastAPI + React) Was Rejected
FastAPI is an exceptional framework for high-throughput microservices. However, for an institutional attendance platform, it requires assembling independent libraries for ORM migrations (Alembic), administrative controls, authentication, and permission management. Django provides these critical features as a coherent, battle-tested, batteries-included framework, eliminating substantial bespoke glue code.

### Why Option B (Django Templates + HTMX) Was Not Selected for Primary UI
While Option B is enticingly simple and requires zero JavaScript build tooling, it has major limitations for this specific operational environment:
1. **Classroom Rapid Attendance UX:** In a classroom with 60–80 students, a faculty member on a smartphone needs instant, optimistic, touch-responsive toggling with zero perceived latency. Full or partial server round-trips over spotty classroom Wi-Fi hinder this rapid flow.
2. **Offline Resilience & Queueing:** When connectivity drops inside a classroom, an SPA/PWA can cache the student roster in browser storage (`IndexedDB`) and queue submissions locally. HTMX requires continuous server communication for every element swap, making robust offline queueing significantly more complex.
3. **Future Native App Pathway:** A decoupled REST API guarantees that if the college later requires a mobile app (Capacitor or React Native), the backend remains 100% reusable without modification.

---

## 6. Recommended Architecture & Technology Stack

### 6.1 Recommended Architecture: **Option A (Decoupled Modular Monolith)**

We recommend **Option A: Django + Django REST Framework + React/TypeScript (PWA) + PostgreSQL**, architected as a **decoupled modular monolith**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER (CLIENT)                     │
│                                                                        │
│   Responsive React 18+ / TypeScript SPA                                │
│   ├── Faculty Attendance Matrix (Touch-Optimized)                      │
│   ├── HOD Department Compliance & Review Portal                        │
│   ├── Admin Master Catalogs & Excel Ingestion UI                       │
│   └── PWA Layer: Service Worker + IndexedDB Offline Submission Queue  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS / REST (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION TIER (BACKEND)                      │
│                                                                        │
│   Python 3.11+ / Django 5.x + Django REST Framework (DRF)              │
│   ├── Authentication & RBAC Service (Session / Token / Knox)           │
│   ├── Academic Timetable & Lecture Session Manager                     │
│   ├── Server-Authoritative Attendance Engine                           │
│   ├── Statutory 75% Calculation & Compliance Evaluator                 │
│   ├── Document Generation Pipeline (python-docx + WeasyPrint / PDF)    │
│   ├── Email Notification Outbox Engine (College SMTP)                  │
│   └── Append-Only Audit Logging Middleware                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Django ORM / SQL
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          DATA TIER (PERSISTENCE)                       │
│                                                                        │
│   PostgreSQL 15+ Relational Database Engine                            │
│   ├── Master Catalogs (Departments, Classes, Subjects, Students)       │
│   ├── Timetables, Sessions, Topics Covered                             │
│   ├── Attendance Records (Unique Indexes & Check Constraints)          │
│   ├── Immutable Audit Log Tables                                       │
│   └── Notification Queue & Delivery Log                                │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Recommended Technology Stack Specifications

| Component | Selected Technology | Version / Tooling | Justification |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | **Python / Django** | Python 3.11+, Django 5.x | Mature ORM, battle-tested security, robust migrations, native PostgreSQL integration. |
| **API Layer** | **Django REST Framework** | DRF 3.15+ | Serializers, declarative validation, standardized pagination, browsable API for debugging. |
| **Database** | **PostgreSQL** | PostgreSQL 15+ | ACID guarantees, JSONB support for audit diffs, composite unique indexing, institutional reliability. |
| **Frontend Framework** | **React with TypeScript** | React 18+, TypeScript 5+ | Type safety, component modularity, vast ecosystem, easy integration with PWA toolchains. |
| **Build & Tooling** | **Vite** | Vite 5+ | Blazing fast build times, lightweight bundle sizes, clean PWA plugin integration (`vite-plugin-pwa`). |
| **UI Styling** | **Tailwind CSS** | Tailwind 3.4+ | Utility-first, responsive design, fast development without heavy UI framework bloat. |
| **PWA & Offline** | **Workbox / IndexedDB** | `idb` / Workbox | Local caching of rosters, service worker asset caching, background sync queue for classroom resilience. |
| **Report Generation** | **python-docx & WeasyPrint**| `python-docx` 1.1+ | Native Microsoft Word (`.docx`) file building with tables and headers; HTML/CSS to PDF for A4 sheets. |
| **Web Server / Reverse Proxy**| **Nginx** | Mainline / Stable | Reverse proxy, static asset delivery, SSL termination, rate limiting. |
| **WSGI Server** | **Gunicorn** | Gunicorn 22+ | Lightweight Python WSGI HTTP server, reliable process management on Linux. |
| **Email Relay** | **Django Core Mail** | Built-in SMTP Engine | Direct TLS/SSL integration with college SMTP server; no third-party cloud email vendor lock-in. |

---

## 7. Deep-Dive Strategy Specifications

### 7.1 Backend Strategy (Modular Monolith)
The backend is structured into domain-focused Django apps within a single repository:
- `apps.accounts`: User authentication, profile management, and RBAC permissions.
- `apps.academics`: Departments, programs, semesters, divisions, subjects, student enrollments.
- `apps.timetable`: Upfront schedule slots, faculty allocations, timetable conflicts.
- `apps.lectures`: Lecture sessions (scheduled/conducted/cancelled/rescheduled), topic/syllabus tracking.
- `apps.attendance`: Attendance roster marking, batch submission, 75% calculation engine.
- `apps.audit`: Immutable audit trail for all attendance corrections and cancellations.
- `apps.notifications`: Outbox email queue, throttling, SMTP delivery worker, delivery logs.
- `apps.reports`: A4 PDF generation and Microsoft Word (`.docx`) document builders.

### 7.2 Frontend Strategy (Responsive Touch PWA)
- **State Management:** React Query (TanStack Query) for server-state caching, automatic cache invalidation, and background refetching.
- **Roster Component:** Touch-optimized attendance roster designed for smartphones and tablets. Single-tap toggle for Present/Absent with a quick "Mark All Present" default action.
- **Design Tokens:** Strict responsive breakpoints (Mobile 375px+, Tablet 768px+, Desktop 1024px+).

### 7.3 Database & Data Integrity Strategy
- **Relational Constraints:** Every `AttendanceRecord` is bound by a composite unique constraint `UNIQUE (lecture_id, student_id)`.
- **Referential Integrity:** `ON DELETE PROTECT` on core academic entities to prevent accidental cascading deletion of historical attendance data.
- **Audit Immutability:** Audit tables are append-only. Database triggers or application-level rules prevent `UPDATE` or `DELETE` on `AttendanceAuditLog` rows.

### 7.4 Offline & Intermittent Connectivity Strategy
Classroom connectivity is notoriously volatile. To prevent data loss without violating server-authoritative integrity:
1. **Pre-fetch:** Faculty logs into the app while connected (staff room or corridor). The current day's lecture schedule and class student rosters are cached in client `IndexedDB`.
2. **Offline Capture:** If network drops during lecture, faculty marks attendance as normal. The client records the marks along with a local timestamp and cryptographically hashed session token in `IndexedDB`.
3. **Queue Status:** A persistent UI banner displays: `"Offline — 1 Attendance Session Queued for Sync"`.
4. **Reconciliation Protocol:**
   - Once network is restored, the client posts the queued payload to `/api/v1/attendance/sync/`.
   - The server validates: Is the session valid? Is the user authorized? Has attendance already been submitted by another session?
   - If valid, records are committed atomically, and the client queue is purged.
   - If a conflict occurs (e.g., session already marked/frozen), the server rejects the batch and prompts the faculty with the conflict details.

### 7.5 Authentication & Modular SSO Strategy
- **Initial Baseline:** Secure username/email + password with Django session or token authentication (e.g., `django-rest-knox`).
- **Decoupled Architecture:** Authentication logic is isolated behind an authentication adapter. If the college later enables Google Workspace, Microsoft 365, or LDAP/Active Directory, an OAuth2/SAML backend can be added to Django without altering any application endpoints or database relationships.

### 7.6 Reporting Strategy (A4 & Word DOCX)
- **DOCX Generation:** Built using `python-docx`. A pre-formatted institutional template `.docx` (with college crest, styles, and page margins) is loaded; tables are programmatically populated with student roll numbers, attendance counts, percentages, and signature lines.
- **A4 PDF Generation:** Built using semantic HTML/CSS templates rendered to PDF via `WeasyPrint` or `ReportLab`, guaranteeing strict `@page { size: A4; margin: 15mm; }` compliance for physical printing.

### 7.7 Email Delivery & Outbox Strategy
- **Outbox Pattern:** Email warnings are never sent synchronously during an HTTP request. Instead, crossing below the 75% threshold writes a record to the `NotificationLog` table with status `PENDING`.
- **Lightweight Worker:** A Django management command (`python manage.py process_email_queue`) runs periodically via standard Linux cron (e.g., every 15 minutes) or a lightweight Python thread.
- **Non-Aggressive Throttling:** The engine enforces a 7-day cooldown per student/subject before dispatching a repeat warning.
- **Zero Redis Dependency:** By utilizing a database-backed queue, the system avoids needing Redis or Celery, saving precious RAM on the Hostinger server.

### 7.8 Deployment Strategy (Hostinger Focus)
- **Primary Configuration (VPS Target):**
  - OS: Ubuntu 22.04 / 24.04 LTS.
  - Reverse Proxy: Nginx handling SSL (Let's Encrypt), static file serving, and proxying API requests to Gunicorn.
  - Application Server: Gunicorn running Django WSGI with 3–4 worker processes.
  - Database: Local PostgreSQL instance with automated daily `pg_dump` backups scheduled via cron.
  - Frontend: Vite-compiled static bundle served directly by Nginx.
- **Fallback Configuration (Shared/Cloud Hosting Target):**
  - If the Hostinger plan turns out to be managed Cloud Hosting without root, Django is deployed via Hostinger's Python App Setup (Passenger/WSGI) with MySQL/PostgreSQL support, and cron jobs configured via hPanel.

---

## 8. Architectural Risk Analysis

| Risk ID | Risk Description | Severity | Mitigation Strategy |
| :--- | :--- | :---: | :--- |
| **RSK-01** | **Hostinger Plan Insufficiency** | High | Confirm plan immediately. If shared host lacks PostgreSQL, either upgrade to Hostinger KVM VPS (standard practice) or leverage managed DB add-on. |
| **RSK-02** | **College SMTP Rate Limits** | Medium | College mail relays often restrict outbound emails to 100–500/hour. Outbox worker includes batch rate-limiting to avoid IP blacklisting. |
| **RSK-03** | **Student Roster Inconsistencies** | Medium | College Excel lists may have missing PRNs or misspelled names. Implement strict validation and preview step before committing student imports. |
| **RSK-04** | **Uncoordinated Attendance Edits** | Low | Unique constraints and optimistic concurrency checks on attendance records prevent conflicting simultaneous submissions. |

---

## 9. Remaining Architectural Decisions Awaiting Stakeholder Clarification

1. **Hostinger Plan Confirmation (AMB-01):** Verify VPS vs Shared hosting with college IT.
2. **Attendance Marking Window (AMB-03):** Permitted window for faculty submission (same-day vs 24h grace).
3. **Correction Workflow Model (AMB-04):** Faculty self-edit window vs mandatory HOD sign-off.
4. **Official Report Layout (AMB-05):** Receipt of 1 physical/digital sample of the college's monthly and semester reports.
