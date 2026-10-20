# Backend Test Strategy

**Document ID:** DOC-TST-001  
**Project:** College Attendance Management System  
**Test Runner:** `pytest` + `pytest-django`  
**Date:** October 2026  

---

## 1. Testing Philosophy

Because the Attendance Management System governs authoritative academic records and statutory 75% student compliance, testing prioritizes **correctness, data integrity, security enforcement, and boundary conditions** over surface-level superficial tests.

---

## 2. Test Classification

1. **Unit & Domain Tests:**
   - Calculation engine verification (exact 75.00% vs 74.99%).
   - Timetable conflict detection algorithms.
   - OTP generation, hashing, rate limiting, and expiry.
2. **Workflow & Service Tests:**
   - Attendance lifecycle (Draft -> Reviewed -> Finalized).
   - Conservative auto-finalization (never guess unrecorded students).
   - Hybrid attendance correction rules (faculty <=24h, HOD review >24h).
   - 75% notification trigger, recovery reset, and cooldown throttling.
3. **API & Security Tests:**
   - RBAC enforcement (Faculty, HOD, Admin roles).
   - Object-level permission barriers.
   - Offline sync idempotency (replaying identical idempotency keys).
   - CSV/Excel student ingestion error handling.
4. **Report Generation Tests:**
   - Verification of A4 PDF binary output.
   - Verification of Microsoft Word `.docx` structure and table generation.
   - CSV export content accuracy.
