# Project Restart & Clean Baseline Document

**Document ID:** DOC-RESTART-001  
**Date:** September 27, 2026  
**Status:** Approved Baseline  
**Project:** College Attendance Management System  

---

## 1. Why the Project Was Restarted

The Attendance Management System was initially conceived with preliminary drafts, exploratory document generation scripts, and prototype UI mockups (v0.1). During this early phase, several design decisions—including attendance capture mechanisms, session models, token/QR workflows, and reporting architectures—were speculative and pending stakeholder review.

Teaching staff and academic stakeholders have since provided explicit clarifications on how college attendance must function in their environment. Rather than attempting to incrementally patch prototype materials that contain obsolete assumptions and technical debt, the repository has been restarted from a clean, disciplined engineering foundation.

---

## 2. What Was Preserved (Archived)

All previous work, preliminary specifications, and mockups have been cleanly moved into `archive/previous-version/` with their full Git commit history intact:

- **Preliminary Software Requirements Specification (v0.1):**
  - `archive/previous-version/Attendance_Management_System_Blueprint_SRS.md`
  - `archive/previous-version/Attendance_Management_System_Blueprint_SRS.docx`
  - `archive/previous-version/Attendance_Management_System_Blueprint_SRS.html`
  - `archive/previous-version/Attendance_Management_System_Blueprint_SRS.pdf`
- **Document Generation Scripts:**
  - `archive/previous-version/build_documents.py`
  - `archive/previous-version/build_full_suite.py`
  - `archive/previous-version/generate_full_docx.py`
- **UI Screen Stitch Mockups:**
  - `archive/previous-version/stitch_college_attendance_management_system.zip`
- **Archive Context Guide:**
  - `archive/previous-version/README.md`

Git history has been strictly preserved; no history rewriting or `.git` deletion was performed.

---

## 3. What Was Removed

- **Obsolete Root Clutter:** All unapproved draft documents and prototype Python scripts have been cleared from the root working directory.
- **Unverified Assumptions:** Unconfirmed attendance workflows (such as QR codes, student self-confirmation, or dynamic tokens) have been removed from the active specification baseline.
- **Build/Artifact Dependencies:** Root document generators have been retired to the archive.

---

## 4. What Remains Active

The repository has established a clean, production-oriented baseline:

- **Clean Directory Hierarchy:**
  - `docs/` — Structured documentation repository (requirements, architecture, database, frontend, api, deployment, decisions).
  - `docs/decisions/` — Formal Architecture Decision Record (ADR) framework.
  - `archive/previous-version/` — Isolated historical reference.
- **Repository Configuration:**
  - Comprehensive `.gitignore` covering Python, Node.js, databases, secrets, virtual environments, IDEs, and OS artifacts.
- **Root Documentation:**
  - Root `README.md` defining project purpose, institutional context, governance, and development roadmap.

---

## 5. Important Warning

> [!WARNING]
> **Previous implementation and archived documents are historical references only. They must not be treated as current requirements unless explicitly re-approved.**

Any feature, schema entity, API endpoint, or UI design from the previous version must be validated against the newly confirmed college requirements before inclusion in the new architecture.

---

## 6. Next Step

> [!IMPORTANT]
> **The next phase is to incorporate the newly confirmed college requirements into the project requirements/specification before implementation begins.**

The strict engineering development chain is:

$$\text{Clean Repo} \longrightarrow \text{Confirmed Requirements} \longrightarrow \text{Updated Blueprint/SRS} \longrightarrow \text{Architecture} \longrightarrow \text{Database} \longrightarrow \text{Backend} \longrightarrow \text{Frontend} \longrightarrow \text{Testing} \longrightarrow \text{Deployment}$$
