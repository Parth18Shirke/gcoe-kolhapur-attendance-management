# ADR-0002: Selection of Technology Stack (Django + DRF + React/TS + PostgreSQL)

- **Decision ID:** ADR-0002
- **Date:** 2026-09-27
- **Status:** Proposed / Recommended (Pending Hostinger Plan Verification)

---

## 1. Context

The College Attendance Management System is restarting development as an institutional production platform. Key institutional requirements dictate:
1. Fast, touch-friendly manual attendance capture by faculty on desktop, tablet, and mobile devices in classrooms.
2. Mandatory generation of official A4 printable reports and Microsoft Word (`.docx`) files with academic tables and signature blocks.
3. Strict server-authoritative calculations, regulatory 75% threshold enforcement, automated college email warnings, and immutable audit logging.
4. Deployment to the college's existing Hostinger subscription without unnecessary infrastructure bloat (no Redis, Celery, or Kubernetes).
5. Future-proof architecture capable of supporting progressive web app (PWA) offline queuing and potential future native mobile clients.

---

## 2. Requirements & Constraints Considered

- **Hostinger Deployability:** Must run on standard Linux hosting environment (VPS or managed Python environment).
- **Document Generation:** Must reliably build native Microsoft Word `.docx` documents and A4 PDFs.
- **Data Integrity & Security:** Must support ACID transactions, composite uniqueness constraints, robust migrations, and role-based access control (RBAC).
- **Client Responsiveness:** Must deliver immediate, lag-free UI interactions for faculty marking rosters of 60–80 students on mobile/tablet devices.
- **Zero Premature Infrastructure:** Must not require external memory brokers (Redis/RabbitMQ) for basic background tasks.

---

## 3. Options Considered

- **Option A (Recommended):** Django + Django REST Framework + React / TypeScript (SPA/PWA) + PostgreSQL
- **Option B:** Django Monolith + Django Templates + HTMX / Alpine.js + PostgreSQL
- **Option C:** Node.js / NestJS + React / TypeScript + PostgreSQL
- **Option D:** FastAPI + React / TypeScript + PostgreSQL

---

## 4. Decision

We recommend **Option A: Django 5.x + Django REST Framework + React 18+ / TypeScript + PostgreSQL 15+**, deployed as a decoupled modular monolith with PWA capabilities.

---

## 5. Rationale

1. **Unmatched Document Generation:** Python is the premier ecosystem for programmatic Microsoft Word generation (`python-docx`) and A4 PDF styling (`ReportLab` / `WeasyPrint`). Complex institutional reporting with merged timetable cells, official college crests, and multi-tier signature blocks is clean and reliable in Python, whereas Node.js libraries (`docx` npm package) are brittle and painful to maintain.
2. **Batteries-Included Security & Data Governance:** Django provides a battle-tested ORM, rock-solid schema migrations, native PostgreSQL support, session/token authentication, and built-in administrative controls. This drastically reduces bespoke boilerplate compared to FastAPI or NestJS.
3. **Optimized Classroom Touch UX:** Decoupling the frontend into a React/TypeScript SPA allows for optimistic, touch-responsive student roster toggling with zero perceived network latency on faculty mobile devices.
4. **Clean Offline Queueing Pathway:** A client-side SPA with a Service Worker and `IndexedDB` can cache the day's class roster and cleanly queue attendance submissions during spotty classroom connectivity, reconciling with the server upon reconnection.
5. **No Overhead for Background Tasks:** Email notifications and report generation can be handled via a database-backed outbox queue processed by standard cron-driven management commands, avoiding the operational overhead and memory consumption of Redis/Celery on the college's Hostinger server.

---

## 6. Trade-offs

- **Two Codebases:** Maintaining a separate Python backend and TypeScript frontend requires managing two toolchains (Python/pip and Node/Vite) compared to a pure Django template monolith (Option B).
- **API Serialization Overhead:** Data contracts between Django and React must be explicitly defined using DRF serializers and TypeScript types.
- *Mitigation:* The development team benefits from end-to-end type safety, modern component development, and a backend that is immediately ready for any future mobile client.

---

## 7. Consequences

- **Backend:** Python 3.11+, Django 5.x, Django REST Framework, `python-docx`, `WeasyPrint` / `reportlab`, `psycopg3`.
- **Frontend:** React 18+, TypeScript 5+, Vite, Tailwind CSS, TanStack Query, `vite-plugin-pwa`.
- **Database:** PostgreSQL 15+.
- **Hosting:** Hostinger VPS (Ubuntu LTS) with Nginx + Gunicorn, or Hostinger Cloud/Shared Python environment.

---

## 8. Revisit Conditions

This architecture decision will be formally revisited if:
1. The college confirms that its Hostinger plan is a restricted shared-hosting tier that prohibits Python WSGI or PostgreSQL, forcing a specialized runtime configuration.
2. The college administration mandates a single unified monolithic codebase with zero JavaScript build steps (in which case Option B: Django + Templates/HTMX would be adopted).
3. The college already possesses a pre-existing enterprise API standard (e.g., Node.js / Java Spring) required for central ERP integration.
