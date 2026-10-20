# API Architecture & Overview

**Document ID:** DOC-API-001  
**Project:** College Attendance Management System  
**Base URL:** `/api/v1/`  
**Protocol:** HTTPS / RESTful JSON  
**Date:** October 2026  

---

## 1. Design Principles

1. **RESTful Resource Hierarchy:** Resources represent domain entities (`/api/v1/sessions/`, `/api/v1/attendance/`).
2. **Standard HTTP Semantics:** 
   - `GET` for safe retrieval.
   - `POST` for creation and complex state transitions.
   - `PUT`/`PATCH` for resource updates.
   - `DELETE` for soft deletion where permitted.
3. **Stateless Bearer Authentication:** Requests supply `Authorization: Bearer <token>` header.
4. **Idempotency Header:** Mutating offline-sync operations accept `X-Idempotency-Key: <UUID>`.
5. **Standardized Response Envelope:** Predictable pagination, data payload, and unified error structures.
6. **OpenAPI 3.0 Compatible:** Schema auto-generated via `drf-spectacular` at `/api/v1/schema/` with Swagger UI at `/api/v1/docs/`.
