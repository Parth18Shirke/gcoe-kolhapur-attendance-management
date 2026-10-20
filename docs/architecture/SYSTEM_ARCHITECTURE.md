# System Architecture Specification

**Document ID:** ARCH-SYS-001  
**Project:** College Attendance Management System  
**Date:** October 2026  
**Pattern:** API-First Modular Monolith (Server-Authoritative)  

---

## 1. High-Level Architecture Topology

The Attendance Management System is architected as an **API-first modular monolith**. All business rules, statutory attendance calculations, role authorizations, and audit records reside strictly within the server.

```mermaid
flowchart TB
    subgraph Clients ["Client Layer (Future & Initial)"]
        WebPWA["React 18 / TypeScript PWA (Offline-Enabled)"]
        MobileApp["Future Mobile Client (React Native / Expo)"]
        AdminWeb["Admin Web Dashboard"]
    end

    subgraph Gateway ["Edge & Ingress (Hostinger VPS / Linux)"]
        Nginx["Nginx Reverse Proxy (SSL, Static Assets, Rate Limiting)"]
        WSGI["Gunicorn WSGI Application Server"]
    end

    subgraph CoreBackend ["Django 5.x / DRF Modular Monolith"]
        APIAuth["Auth & Identity (Email OTP, Session/JWT Abstraction)"]
        APIRouter["API v1 Gateway & Serializer Validation Layer"]
        
        subgraph DomainModules ["Domain Subsystems"]
            AcademicsMod["apps.academics (Hierarchy & Catalogs)"]
            StudentsMod["apps.students (Student Master & Ingestion)"]
            FacultyMod["apps.faculty (Faculty Workload Allocations)"]
            RoomsMod["apps.rooms (Classrooms, Labs & Resources)"]
            TimetableMod["apps.timetable (Slots, Conflict Engine & Sessions)"]
            AttendanceMod["apps.attendance (Rosters, Lifecycle & 75% Engine)"]
            CorrectionsMod["apps.corrections (Hybrid 24h & HOD Workflow)"]
            SyncMod["apps.synchronization (Offline Idempotency & Conflict Resolver)"]
            ReportsMod["apps.reports (A4 PDF, python-docx, CSV)"]
            NotificationsMod["apps.notifications (Outbox Queue & Email Abstraction)"]
            AuditMod["apps.audit (Append-Only Institutional Audit Log)"]
        end
    end

    subgraph Storage ["Persistence & External Services"]
        PGDB[("PostgreSQL 15+ Relational Database")]
        FileStorage[("Document Storage / Media / Reports")]
        CollegeSMTP["College SMTP Server / External Mail Relay"]
    end

    WebPWA -- "HTTPS / REST JSON" --> Nginx
    MobileApp -- "HTTPS / REST JSON" --> Nginx
    AdminWeb -- "HTTPS / REST JSON" --> Nginx

    Nginx --> WSGI --> APIRouter
    APIRouter --> APIAuth
    APIRouter --> DomainModules
    DomainModules <--> PGDB
    DomainModules --> FileStorage
    NotificationsMod -- "Background Dispatch" --> CollegeSMTP
```

---

## 2. Invariant: Server Authority

Clients (whether future React PWA or React Native mobile apps) are untrusted runtimes. The server enforces:
1. **Academic Truth:** Official percentages, threshold alerts, and attendance totals are computed exclusively on the backend.
2. **Timetable Rules:** Sessions, cancellations, and reschedulings are verified against master schedule rules.
3. **Audit Immutability:** Audit records are generated automatically on write operations and cannot be modified by client payloads.
4. **Idempotency:** Offline synchronization batches are validated against existing database state; re-transmissions cannot double-count marks.

---

## 3. Modular Monolith Subsystem Breakdown

| Subsystem Module | Directory | Core Responsibilities |
| :--- | :--- | :--- |
| `accounts` | `backend/apps/accounts/` | Custom User model, Email OTP generation/verification, rate limiting, RBAC permissions, token lifecycle. |
| `academics` | `backend/apps/academics/` | Department, Program, AcademicYear, Semester, Division, Subject models and relations. |
| `students` | `backend/apps/students/` | Student profiles, privacy display formatting (last-4 PRN), enrollment records, CSV/Excel import parser. |
| `faculty` | `backend/apps/faculty/` | Faculty profile, department affiliation, subject/division workload assignments. |
| `rooms` | `backend/apps/rooms/` | Classroom and Laboratory catalogs, capacity, resource tagging, and conflict detection queries. |
| `timetable` | `backend/apps/timetable/` | Recurring timetable slots, concrete dated sessions (theory & lab), scheduling conflict engine, cancellations, rescheduling lineage. |
| `attendance` | `backend/apps/attendance/` | Roster attendance marking, session state lifecycle (Draft -> Reviewed -> Finalized), conservative auto-finalization, 75% calculation engine. |
| `corrections` | `backend/apps/corrections/` | Hybrid attendance correction requests (faculty <=24h self-correction, older HOD review/approval), approval history. |
| `synchronization`| `backend/apps/synchronization/`| Offline sync contract, idempotency token verification, conflict detection, atomic batch commit. |
| `notifications` | `backend/apps/notifications/`| Outbox queue, delivery status tracking, 75% deficiency state machine, anti-spam cooldown, email provider abstraction. |
| `reports` | `backend/apps/reports/` | Official A4 PDF rendering (ReportLab/WeasyPrint), editable Microsoft Word (`python-docx`), and CSV exports. |
| `audit` | `backend/apps/audit/` | Immutable append-only audit trail capturing actor, action, timestamp, object reference, old/new state, and reason. |
| `common` | `backend/apps/common/` | Shared utilities, base models (`TimeStampedModel`), standard pagination, unified error envelope. |
