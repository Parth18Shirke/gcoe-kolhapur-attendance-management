# ADR-0001: Repository Cleanup and Project Restart from Clean Baseline

- **Decision ID:** ADR-0001
- **Date:** 2026-09-27
- **Status:** Accepted

---

## Context

The initial Attendance Management System repository contained preliminary drafts, document generation scripts, and prototype UI mockups (v0.1) based on preliminary assumptions (including speculative attendance capture methods such as student self-confirmation sessions and dynamic tokens). Teaching staff and college stakeholders have subsequently clarified institutional requirements. Retaining prototype materials alongside new development introduces confusion, technical debt, and risk of accidental dependency on obsolete assumptions.

---

## Decision

Perform a complete repository cleanup and fresh baseline restart:
1. Isolate and preserve all v0.1 documents, generation scripts, and prototype mockups inside `archive/previous-version/` using Git to maintain full historical traceability.
2. Establish a modular documentation structure under `docs/` with explicit separation of requirements, architecture, database, frontend, API, deployment, and decision logs.
3. Establish a comprehensive `.gitignore` preventing commits of secrets, virtual environments, build artifacts, and local databases.
4. Establish an updated root `README.md` defining the institutional purpose and development conventions.
5. Explicitly prohibit feature implementation until confirmed requirements and specifications are documented.

---

## Alternatives Considered

- **In-place Refactoring:** Incrementally modifying the existing draft files.  
  *Rejected because:* The prototype documents contained numerous unverified questions and assumptions that contradicted recently clarified institutional practices.
- **Hard Deletion / New Repo Creation:** Deleting the Git repository and starting a new one.  
  *Rejected because:* Destroys repository commit history, links to remotes, and historical accountability.

---

## Reason

Preserving Git history while isolating legacy material in an archive provides the best balance of historical reference and clean-slate implementation. It ensures developers cannot inadvertently import or depend on outdated assumptions.

---

## Impact

- **Positive:** Clean, professional working environment with zero technical debt or obsolete code clutter.
- **Positive:** Full Git history preserved.
- **Downstream Action:** Requirements intake must occur before architectural design or coding begins.
