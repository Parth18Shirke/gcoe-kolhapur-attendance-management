# Technology Stack Specification

**Document ID:** ARCH-STK-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Selected Technology Stack

| Layer | Technology | Specification / Version | Justification |
| :--- | :--- | :--- | :--- |
| **Language** | **Python** | Python 3.11 / 3.12+ | Robust ecosystem for enterprise document generation, data manipulation, and security libraries. |
| **Backend Framework** | **Django** | Django 5.2+ | Batteries-included web framework: bulletproof ORM migrations, secure authentication base, CSRF/SQLi defense, and admin governance. |
| **API Framework** | **Django REST Framework** | DRF 3.18+ | Declarative serializers, fine-grained object-level permissions, standardized status codes, and pagination. |
| **API Documentation** | **drf-spectacular** | OpenAPI 3.0 / Swagger | Automated, schema-compliant OpenAPI generation enabling client SDK generation for React/React Native. |
| **Primary Database** | **PostgreSQL** | PostgreSQL 15+ (Local / VPS) | Relational integrity, ACID transactions, composite uniqueness constraints, JSONB for audit diffs. |
| **Dev/Test Database** | **SQLite / PostgreSQL** | In-Memory / File | Fast, zero-dependency automated test execution via `pytest-django`. |
| **Test Runner** | **pytest + pytest-django** | pytest 9.1+, pytest-django 4.14+ | High-speed parameterized testing, fixture factories, and comprehensive coverage reporting. |
| **Document Generation** | **python-docx** | python-docx 1.2+ | Programmatic creation of official Microsoft Word documents with merged timetable cells and signature blocks. |
| **PDF Generation** | **ReportLab** | ReportLab 5.0+ | Direct generation of pixel-perfect A4 printable institutional sheets with headers, footers, and pagination. |
| **Spreadsheet Ingestion**| **openpyxl** | openpyxl 3.1+ | Reading and validating college-provided Excel (`.xlsx`) student roster files. |
| **Web Server Gateway** | **Gunicorn** | Gunicorn 22+ | Industry-standard WSGI HTTP server for production Python deployments on Linux. |
| **Reverse Proxy** | **Nginx** | Mainline / Stable | SSL/TLS termination, static asset offloading, request rate limiting, and reverse proxying. |
| **Future Client Target** | **React + TS (PWA) / Expo**| React 18+ / React Native | Unified REST API consumption across web and future mobile applications. |
