# ATTENDANCE MANAGEMENT SYSTEM
## Project Blueprint & Preliminary Software Requirements Specification (SRS)

**Intended Institutional Deployment:** Higher Education College / Academic Institution  
**Document Version:** 0.1 — Preliminary Review Draft  
**Prepared By:** Student Development Team (Lead Engineers)  
**Presented To:** College Academic & Teaching Staff  
**Date:** September 2026  

---

## Document Control & Clarification Notice

> **Status of Specifications in this Document:**  
> This blueprint serves as the foundational engineering and requirements specification for an institutional-grade Attendance Management System. To maintain strict engineering integrity, this document explicitly categorizes all statements:
> 1. **Confirmed Requirements:** Explicitly mandated by the college teaching staff.
> 2. **Proposed Design Decisions:** Professional technical and architectural recommendations by the development team, subject to stakeholder review.
> 3. **Open Questions / To Be Decided (TBD):** Critical operational and institutional parameters requiring formal college determination before final implementation.
> 4. **Optional / Future Extensions:** Roadmap items outside the immediate minimum viable deployment scope.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background and Problem Statement](#2-background-and-problem-statement)
3. [Objectives](#3-objectives)
4. [Scope of the System](#4-scope-of-the-system)
5. [Stakeholders and User Roles](#5-stakeholders-and-user-roles)
6. [Confirmed Functional Requirements](#6-confirmed-functional-requirements)
7. [Open Questions and Clarifications Required](#7-open-questions-and-clarifications-required)
8. [Proposed System Workflow](#8-proposed-system-workflow)
9. [Proposed Lecture & Topic Tracking Model](#9-proposed-lecture--topic-tracking-model)
10. [User Inputs and System Outputs](#10-user-inputs-and-system-outputs)
11. [Attendance Calculation Methodology](#11-attendance-calculation-methodology)
12. [Reporting Design & A4/Word Integration](#12-reporting-design--a4word-integration)
13. [Proposed System Architecture](#13-proposed-system-architecture)
14. [Preliminary Conceptual Data Model](#14-preliminary-conceptual-data-model)
15. [Security, Authorization & Auditability](#15-security-authorization--auditability)
16. [Non-Functional Requirements (NFRs)](#16-non-functional-requirements-nfrs)
17. [Deployment & Infrastructure Considerations](#17-deployment--infrastructure-considerations)
18. [Proposed Technology Stack & Technical Rationale](#18-proposed-technology-stack--technical-rationale)
19. [Risks, Constraints & Mitigation Strategies](#19-risks-constraints--mitigation-strategies)
20. [Future Extensions (Out of Current Scope)](#20-future-extensions-out-of-current-scope)
21. [Decisions Pending College Approval](#21-decisions-pending-college-approval)
22. [Development Roadmap](#22-development-roadmap)

---

## 1. Executive Summary

The **Attendance Management System (AMS)** is a web-based institutional software solution designed to modernize, streamline, and standardize student attendance recording, curricular tracking, threshold monitoring, and academic reporting across academic departments.

Unlike basic academic demonstrations, this platform is conceived as an **institutional-grade management system** capable of supporting multi-department academic structures, enforcing institutional attendance regulations, providing transparent audit trails, and generating official documentation ready for administrative and regulatory use.

### Core Capabilities:
- **Lecture-Centric Attendance Capture:** Reliable recording of attendance linked directly to individual lectures, classes, and assigned faculty.
- **Pedagogical Topic Tracking:** Mandatory recording of syllabus topics/points covered in each conducted lecture.
- **Automated Threshold Alerting:** Continuous calculation of subject-wise and overall semester attendance with automated college-email notifications to students falling below the mandatory **75% threshold**.
- **Formal Academic Reporting:** Generation of clean, standardized monthly and semester-wise attendance sheets optimized for **A4 printing** and seamless integration into **Microsoft Word (DOCX)** administrative workflows.

---

## 2. Background and Problem Statement

Higher education institutions face substantial administrative friction and risks of error when managing attendance through legacy paper registers or disjointed spreadsheets:

1. **Labor-Intensive Record Keeping:** Manual calculation of monthly and cumulative semester percentages consumes valuable faculty time and introduces computational human error.
2. **Delayed Threshold Interventions:** Under conventional systems, students with critically low attendance (<75%) are often identified only at the end of the term when it is too late for corrective remedial action.
3. **Absence of Pedagogical Auditing:** Traditional roll-calls record *who* was present, but fail to maintain a structured institutional record of *what syllabus topics* were delivered during each specific lecture block.
4. **Disjointed Administrative Reporting:** Preparing official reports for academic committees, university bodies, parent meetings, and accreditation audits (e.g., NAAC, NBA) requires extensive manual reformatting into A4 and Word-compatible tables.

The proposed system addresses these challenges by establishing a single, authoritative digital record for attendance and lecture delivery.

---

## 3. Objectives

The primary engineering and operational objectives derived from the confirmed requirements are:

- **Objective 1:** Provide an intuitive, resilient web interface for teaching staff to record attendance accurately during or immediately following scheduled lectures.
- **Objective 2:** Maintain a verifiable repository of conducted lectures, including class, subject, faculty, timestamps, and specific syllabus points covered.
- **Objective 3:** Implement an automated calculation engine that computes subject-wise and overall semester attendance percentages in real time.
- **Objective 4:** Automatically detect students below the statutory 75% attendance benchmark and dispatch standardized notification alerts to their registered college email accounts.
- **Objective 5:** Export professional, publication-quality monthly and semester attendance reports formatted specifically for standard A4 paper and Microsoft Word document editing.
- **Objective 6:** Ensure institutional data integrity, role-based security, and historical auditability across all academic sessions.

---

## 4. Scope of the System

### 4.1 In Scope (Confirmed & Proposed Base Platform)
- **Academic Hierarchy Management:** Programs, Academic Years, Semesters, Departments, Divisions/Batches, and Subjects.
- **User Authentication & Role-Based Access Control:** Distinct permission boundaries for Students, Teaching Faculty, and Academic Administrators.
- **Lecture Logging:** Recording lecture metadata (Date, Duration, Subject, Class, Assigned Faculty) along with bulleted/structured topics covered.
- **Attendance Session Management:** Generating and logging attendance records tied to specific lecture instances.
- **Threshold Rule Engine:** Evaluation of the 75% attendance rule on subject-wise and cumulative semester bases.
- **Email Notification Dispatcher:** SMTP-based integration to transmit attendance warning notices to students' institutional email IDs.
- **Document Export Engine:** Direct generation of A4-compatible printable reports (DOCX and PDF formats).
- **Administrative Audit Trails:** Logging timestamped records of attendance submissions and authorized corrections.

### 4.2 Out of Scope / Not Yet Confirmed (Advanced Mechanisms Excluded from Base Phase)
The following technologies and features are **explicitly excluded** from the baseline implementation unless formally requested and approved by the college administration:
- **Biometric Hardware Integration:** Physical fingerprint or iris scanners.
- **Facial Recognition Systems:** AI-based computer vision attendance.
- **GPS / Geofencing Verification:** Location-constrained attendance validation.
- **RFID / Smart Card Hardware:** Physical tap-card readers at classroom doors.
- **Native Mobile Apps (iOS/Android):** Base deployment is a fully responsive Web application.
- **Automated Timetable / Room Scheduling Engines:** Timetable allocation remains an external input.

---

## 5. Stakeholders and User Roles

The system recognizes three primary institutional user roles with clearly delineated responsibilities:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        INSTITUTIONAL USER ROLES                        │
├───────────────────┬───────────────────────┬────────────────────────────┤
│      STUDENT      │    TEACHING FACULTY   │  ACADEMIC ADMINISTRATOR    │
│                   │                       │     (HOD / Dean / Office)  │
├───────────────────┼───────────────────────┼────────────────────────────┤
│ • View personal   │ • Create/log lectures │ • Manage academic master   │
│   attendance %    │ • Record class        │   data (classes, subjects) │
│ • Track subject-  │   attendance          │ • Manage faculty & student │
│   wise status     │ • Log syllabus topics │   accounts / enrollments   │
│ • View topics     │ • Generate class/     │ • View department-wide     │
│   covered         │   subject reports     │   attendance analytics     │
│ • Receive <75%    │ • Submit authorized   │ • Authorize post-freeze    │
│   warning emails  │   corrections         │   attendance amendments    │
└───────────────────┴───────────────────────┴────────────────────────────┘
```

### Proposed Role Responsibilities & Confirmation Status:

| User Role | Proposed Responsibilities | Access Boundaries | Status |
| :--- | :--- | :--- | :--- |
| **Student** | • View authenticated personal attendance profile.<br>• View subject-wise breakdown (Classes Attended / Classes Conducted).<br>• Access summary of syllabus topics covered in attended/missed classes.<br>• Receive system warning emails if cumulative or subject attendance falls <75%. | Read-Only. Can only access their own student record. Cannot view peers' data. | Proposed (Standard) |
| **Teaching Faculty** | • Create and log scheduled lecture sessions.<br>• Enter detailed topics/points covered per lecture.<br>• Record student attendance for assigned subject-class pairings.<br>• Generate, preview, and download monthly and semester reports.<br>• Modify attendance within an authorized time window (e.g., 24 hours). | Read/Write for assigned subjects and classes only. Cannot modify other faculty members' records. | Proposed (Standard) |
| **Academic Administrator / HOD** | • Provision and manage student, faculty, class, and course allocations.<br>• Oversee department-wide attendance compliance.<br>• Generate institutional-level consolidated reports for academic councils.<br>• Audit and approve retroactive attendance adjustments.<br>• Trigger or configure scheduled notification batches. | Global administrative access across the department or entire institution. | **Requires College Confirmation** regarding administrative hierarchy. |

---

## 6. Confirmed Functional Requirements

The following requirements represent the authoritative baseline established by the teaching staff:

| Requirement ID | Requirement Title | Priority | Institutional Status | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Attendance Recording | High | **Confirmed** | Teaching staff to record attendance using the platform/device available to students. (Capture mechanism TBD). |
| **FR-02** | Monthly & Academic Semester Reports | High | **Confirmed** | Generation of periodic monthly and comprehensive semester attendance summaries. |
| **FR-03** | Lecture & Topic Tracking | High | **Confirmed** | Structured recording of conducted lectures, date/time, and syllabus topics covered. |
| **FR-04** | Offline Word & A4-Optimized Reporting | High | **Confirmed** | Exportable reports formatted cleanly for A4 printing and Microsoft Word (DOCX) integration. |
| **FR-05** | Percentage Calculation & <75% Email Alerts | High | **Confirmed** | Real-time calculation of subject and semester %; automated email warnings for students <75%. |

---

### Detailed Functional Specifications

#### FR-01: Attendance Recording
- **Description:** Authorized teaching staff must be able to record the attendance status (Present / Absent) of every enrolled student for a conducted lecture.
- **Platform Capability:** Accessible via standard web browsers on devices available within the classroom (faculty laptops, tablets, smartphones, or lab workstations).
- **Critical Constraint:** *The exact capture mechanism (manual roll-call, faculty-initiated session, student self-confirmation, or dynamic short-code) has not been finalized by the college.* The underlying data structure must support any of these operational modes without requiring a database redesign.

#### FR-02: Monthly and Academic Semester Reports
- **Description:** The system must compile and present attendance statistics over two distinct time horizons:
  1. *Monthly Reports:* Summary of lectures conducted, lectures attended, and monthly percentages per student for a given calendar month.
  2. *Academic / Semester Reports:* Cumulative statistics spanning the entire semester to date, highlighting overall attendance health and trends.
- **Content Requirements:** Must include Student Name, Roll/Enrollment Number, Subject Code/Title, Total Classes Conducted, Classes Attended, Absent Count, and Calculated Percentage.

#### FR-03: Lecture and Topic Tracking (Pedagogical Audit)
- **Description:** Every attendance instance must be intrinsically bound to a conducted `Lecture` entity.
- **Captured Data Fields:**
  - Subject Name and Academic Code
  - Class / Division / Section
  - Assigned Faculty Name
  - Date of Delivery
  - Actual Start Time & End Time
  - Topics / Points Covered (Structured text / bullet points detailing syllabus progression)

#### FR-04: Offline Word and A4-Optimized Reporting
- **Description:** Administrative personnel require attendance records in physical binder formats and editable institutional reports.
- **Formatting Specifications:**
  - Optimized for standard **ISO A4 page dimensions** (210 mm × 297 mm) with standard institutional margins (0.5 to 0.75 in).
  - Clean table borders, repeating table headers across page breaks, and zero horizontal truncation.
  - Export capabilities to **Microsoft Word (.docx)** format for administrative document integration, with simultaneous support for **PDF (.pdf)** for tamper-resistant archiving.

#### FR-05: Attendance Calculation and 75% Warning Dispatch
- **Description:** The system must maintain accurate, up-to-the-minute attendance percentages:
  - *Subject-Wise Percentage:* Evaluated independently for each enrolled course.
  - *Overall Semester Percentage:* Cumulative across all applicable subjects.
- **Deficit Detection:** If a student's calculated attendance drops below **75.0%**, the system identifies the student as in attendance deficit.
- **Notification Action:** An automated warning email is generated and dispatched to the student's registered institutional email address, alerting them of their status, current percentage, and missed lecture count.

---

## 7. Open Questions and Clarifications Required

To progress from this preliminary blueprint to technical implementation, the college teaching staff and administrative authorities must clarify the following operational policies:

| Category | Item # | Specific Clarification Question | Potential Options / Impact | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Attendance Capture** | Q-01 | What is the exact workflow intended by *"using the platform/device available to students"*? | **Option A:** Faculty enters attendance manually on faculty device.<br>**Option B:** Faculty opens a timed session; students confirm attendance from their own mobile/laptop.<br>**Option C:** Faculty displays a dynamic token/code; students submit via portal. | **Pending Staff Review** |
| | Q-02 | What measures are required to prevent proxy attendance if student devices are used? | Session timeout (e.g., 2 minutes), one-time validation codes, IP subnet restriction to campus Wi-Fi, or manual faculty verification. | **Pending Staff Review** |
| | Q-03 | What is the policy for retroactive attendance correction (e.g., late arrival, clerical error)? | Can faculty edit anytime, within 24 hours only, or is HOD approval required after session finalization? | **Pending Staff Review** |
| | Q-04 | What fallback procedure applies when classroom internet or student device battery fails? | Faculty manual offline paper log with bulk upload, or faculty override portal. | **Pending Staff Review** |
| **College Infrastructure** | Q-05 | Does the college maintain an existing Student Information System (SIS), ERP, or student database? | Direct database export (CSV/Excel upload), REST API integration, or greenfield database entry. | **Pending Staff Review** |
| | Q-06 | Is there a central Single Sign-On (SSO) service (e.g., Google Workspace, Microsoft 365, LDAP)? | Django standalone authentication vs. OAuth2/SAML institutional login integration. | **Pending Staff Review** |
| | Q-07 | Are standardized institutional student email addresses already assigned and active? | Institutional domain (e.g., `student@college.edu`) vs. personal Gmail/Yahoo addresses. | **Pending Staff Review** |
| **Academic Rules** | Q-08 | How are cancelled lectures, faculty leave, and public holidays recorded? | Excluded from denominator of total applicable lectures. | **Pending Staff Review** |
| | Q-09 | How are officially sanctioned absences (Medical leave, sports representation, NCC/NSS) treated? | Counted as present, excluded from calculation, or recorded under a separate "Excused" code? | **Pending Staff Review** |
| | Q-10 | Are practical/laboratory sessions (batches) calculated separately or weighted differently from lectures? | 1 lab session = 2 lecture credits, or separate independent attendance rosters? | **Pending Staff Review** |
| **Email Policies** | Q-11 | What is the exact trigger policy for <75% warning emails? | **Option A:** Immediate (sent as soon as an absence drops % < 75%).<br>**Option B:** Weekly automated digest.<br>**Option C:** Monthly checkpoint batch.<br>**Option D:** On-demand manual trigger by HOD. | **Pending Staff Review** |
| | Q-12 | Should warning emails also be CC'd to Faculty Advisors, Class Teachers, or HODs? | Direct to student only vs. multi-recipient institutional escalation. | **Pending Staff Review** |
| **Reporting Specs** | Q-13 | Is Microsoft Word (DOCX), PDF, or both required as the standard export format? | DOCX for administrative reformatting, PDF for signed official archives. | **Pending Staff Review** |
| | Q-14 | What official header/footer elements are mandatory on reports? | College Logo, Department Seal, Affiliated University Name, Principal/HOD signature blocks. | **Pending Staff Review** |
| **Deployment** | Q-15 | Where will the server be hosted? | College on-premises server / local intranet vs. Cloud VM (AWS, Azure, DigitalOcean). | **Pending Staff Review** |
| | Q-16 | What is the expected sizing (concurrent students, faculty, total records)? | Sizing determines database connection pooling and cache configuration. | **Pending Staff Review** |

---

## 8. Proposed System Workflow

The conceptual dataflow below illustrates the end-to-end lifecycle of an academic attendance session, from master data configuration to report generation and automated alerting:

```
+─────────────────────────────────────────────────────────────+
│                    ACADEMIC MASTER DATA                     │
│  (Departments, Classes, Subjects, Enrolled Students, Staff) │
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼
+─────────────────────────────────────────────────────────────+
│                    FACULTY LECTURE ENTRY                    │
│   (Selects Subject + Class, Sets Date/Time, Enters Topics)  │
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼
+─────────────────────────────────────────────────────────────+
│                 ATTENDANCE SESSION CREATION                 │
│              [Capture Mechanism: TBD by College]             │
│   (Manual Faculty Roll-Call / Session Code / Confirmation)  │
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼
+─────────────────────────────────────────────────────────────+
│                 STUDENT ATTENDANCE CAPTURE                  │
│       (Individual Records: Present / Absent / Excused)       │
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼
+─────────────────────────────────────────────────────────────+
│               VALIDATION & SESSION FINALIZATION             │
│        (Faculty Review -> Timestamped Database Commit)       │
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼
+─────────────────────────────────────────────────────────────+
│            ATTENDANCE METRICS CALCULATION ENGINE            │
│   (Computes Subject % and Cumulative Semester % per Student) │
+──────────────────────────────┬──────────────────────────────+
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
+───────────────────────────+     +───────────────────────────+
│   REPORT GENERATION HUB   │     │    THRESHOLD EVALUATOR    │
│  • Monthly Class Summaries │     │   (Checks: Attendance < 75%)│
│  • Semester Final Sheets  │     +─────────────┬─────────────+
│  • Subject-Wise Audits    │                   │ (If < 75%)
│  • A4 Word / PDF Exports  │                   ▼
+───────────────────────────+     +───────────────────────────+
                                  │   EMAIL DISPATCH SERVICE  │
                                  │ (Institutional Warning to │
                                  │   Student College Email)  │
                                  +───────────────────────────+
```

---

## 9. Proposed Lecture & Topic Tracking Model

### 9.1 Conceptual Hierarchy
In traditional basic systems, attendance is often treated merely as a standalone list of names and dates. In this institutional blueprint, the **Lecture is the central operational entity**.

```
SUBJECT (e.g., CS301 - Database Systems)
   │
   └── LECTURE SESSION
         ├── Academic Class / Division (e.g., Year 3, Div A)
         ├── Assigned Faculty (e.g., Prof. Smith)
         ├── Scheduled / Actual Date (e.g., 2026-09-05)
         ├── Start Time & End Time (e.g., 09:00 - 10:00)
         ├── Lecture Type (Theory / Practical Lab / Tutorial)
         ├── Syllabus Topics / Points Covered (Structured Narrative)
         │
         └── ATTENDANCE SESSION
               ├── Session Status (Draft / Open / Finalized / Locked)
               └── ATTENDANCE RECORDS (1 per Enrolled Student)
                     ├── Student ID
                     ├── Status (Present / Absent / Excused)
                     └── Timestamp
```

### 9.2 Institutional Benefits of Lecture-First Architecture:
1. **Accreditation & Curriculum Audit:** Provides full transparency for academic reviews (e.g., verifying if the requisite number of syllabus hours and topics were completed before examinations).
2. **Student Transparency:** When students review their attendance portal, they see not only that they were absent on a given date, but exactly what academic concepts were covered in that missed session.
3. **Substitute Faculty Support:** If a guest or substitute lecturer conducts a class, the topic continuity is preserved in the central institutional log.

---

## 10. User Inputs and System Outputs

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SYSTEM BOUNDARIES                                     │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│               USER INPUTS                 │              SYSTEM OUTPUTS                │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ [Student Inputs]                          │ [Student Outputs]                          │
│ • Authentication credentials              │ • Personal attendance overview dashboard   │
│ • Attendance confirmation (if mechanism   │ • Subject-wise attendance % & breakdown    │
│   requires student-side action - TBD)     │ • Detailed log of topics covered per class │
│                                           │ • Official <75% warning email alerts       │
│ [Faculty Inputs]                          │                                            │
│ • Selected Class, Division, and Subject   │ [Faculty Outputs]                          │
│ • Lecture Date, Start Time, and End Time  │ • Live student roster attendance view      │
│ • Detailed syllabus topics covered        │ • Class-wide attendance summaries          │
│ • Present/Absent markers per student      │ • Low-attendance student highlight lists   │
│ • Justifications for post-freeze edits    │ • Downloadable A4 Monthly/Semester reports │
│                                           │                                            │
│ [Administrator Inputs]                    │ [Administrator Outputs]                    │
│ • Master data: Departments, Programs      │ • Consolidated institutional analytics     │
│ • Academic Years, Semesters, Divisions    │ • Comprehensive accreditation audit logs   │
│ • Course/Subject catalogs & allocations   │ • System-wide deficit email dispatch logs  │
│ • Student & Faculty master profiles       │ • Formatted DOCX / PDF institutional sheets│
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 11. Attendance Calculation Methodology

### 11.1 Standard Mathematical Formulations

#### 1. Subject-Wise Attendance Percentage ($P_{sub}$)
For a given student $i$ in a specific subject $s$:

$$\text{Subject Attendance } \% = \left( \frac{\text{Present lectures for subject}}{\text{Total applicable lectures for subject}} \right) \times 100$$

Where:
- Present lectures include sessions marked Present (and officially sanctioned Excused sessions if approved by college policy).
- Total applicable lectures = Total scheduled sessions held minus officially cancelled sessions.

#### 2. Cumulative Semester Attendance Percentage ($P_{sem}$)
For a given student $i$ across all enrolled subjects in the active semester:

$$\text{Semester Attendance } \% = \left( \frac{\text{Total present applicable lectures across all subjects}}{\text{Total applicable lectures across all subjects}} \right) \times 100$$

---

### 11.2 Threshold Warning Evaluation Rule
For every student $i$:
- If **Semester Attendance % < 75.0%**, the student is flagged in Overall Attendance Deficit.
- If **Subject Attendance % < 75.0%** for any individual subject, the student is flagged in Subject-Specific Deficit.

*Note:* College must confirm whether warning triggers on overall deficit, subject deficit, or both.

---

## 12. Reporting Design & A4/Word Integration

To fulfill **FR-02** and **FR-04**, the reporting engine is architected around a single, authoritative database source, eliminating discrepancies between web views and physical printouts.

```
                                  AUTHORITATIVE DATABASE
                                             │
                                             ▼
                             REPORT COMPILATION ENGINE (Django)
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             A4-PRINTABLE PDF ENGINE                    DOCX GENERATION ENGINE
           (Tamper-Resistant Format)                   (Editable Administrative)
                       │                                           │
          • Fixed A4 dimensions (210×297mm)           • Native Microsoft Word tables
          • Repeating table headers                   • Compatible with college templates
          • Official signature blocks                 • Custom institutional styling
          • Departmental summary charts               • Easy administrative merging
```

### 12.1 Proposed Report Layout Specifications
1. **Header Block:**
   - Institutional Name, Department, Academic Year, and Semester.
   - Report Type (Monthly Attendance Sheet vs. Consolidated Semester Report).
   - Subject Code, Subject Title, and Assigned Faculty Name (for subject reports).
   - Reference Period (e.g., *01 September 2026 to 30 September 2026*).
2. **Data Matrix:**
   - Column 1: Roll / Enrollment Number
   - Column 2: Student Full Name
   - Columns 3 to N: Date-wise attendance markers (P / A) or aggregated figures.
   - Column N+1: Total Lectures Conducted
   - Column N+2: Total Lectures Attended
   - Column N+3: Attendance Percentage (%)
   - Column N+4: Status Flag (Normal >= 75% / Deficit < 75%)
3. **Footer Block:**
   - Summary Statistics: Class Average Attendance %, Total Students in Deficit.
   - Signature Placeholders: *Subject Teacher*, *Class Coordinator*, *Head of Department (HOD)*.

---

## 13. Proposed System Architecture

The proposed system adopts a robust, modular, monolithic Django architecture suited for high-reliability institutional data management:

```
+─────────────────────────────────────────────────────────────────────────────+
│                                CLIENT TIER                                  │
│     Web Browsers (Desktop PCs, Classroom Laptops, Tablets, Smartphones)     │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │ HTTPS / TLS (Port 443)
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                              WEB SERVER TIER                                │
│           Nginx (Reverse Proxy, SSL Termination, Static Asset Server)       │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │ WSGI (Unix Domain Socket)
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                           APPLICATION SERVER TIER                           │
│                     Gunicorn + Django Application Core                      │
│                                                                             │
│  ┌────────────────────┐ ┌────────────────────┐ ┌─────────────────────────┐  │
│  │   Authentication   │ │     Academics      │ │   Lecture & Attendance  │  │
│  │   & RBAC Module    │ │   Master Module    │ │       Core Engine       │  │
│  └────────────────────┘ └────────────────────┘ └─────────────────────────┘  │
│  ┌────────────────────┐ ┌────────────────────┐ ┌─────────────────────────┐  │
│  │  Calculation and   │ │   A4 PDF & DOCX    │ │    Email Dispatcher     │  │
│  │   Threshold Rule   │ │  Reporting Engine  │ │      (SMTP Client)      │  │
│  └────────────────────┘ └────────────────────┘ └─────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │    [Optional Integration Layer] Django REST Framework (DRF) APIs      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │ Django ORM (PostgreSQL Driver)
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                                DATABASE TIER                                │
│             PostgreSQL Relational Database Management System                │
│       (ACID Transactions, Foreign Keys, Unique Indexes, Audit Logs)         │
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 14. Preliminary Conceptual Data Model

The following entity relationship model represents the proposed preliminary schema designed to support all confirmed requirements while remaining adaptable to pending college decisions:

```
+──────────────────+       1:N       +──────────────────+
│    Department    │ ──────────────> │     Program      │
+──────────────────+                 +──────────────────+
                                              │ 1:N
                                              ▼
+──────────────────+       1:N       +──────────────────+
│   AcademicYear   │ ──────────────> │     Semester     │
+──────────────────+                 +──────────────────+
                                              │ 1:N
                                              ▼
+──────────────────+       1:N       +──────────────────+
│     Faculty      │                 │  ClassDivision   │
+──────────────────+                 +──────────────────+
         │ 1:N                                │ 1:N
         │                                    │
         │         +──────────────────+       │
         ├───────> │     Subject      │ <─────┤
         │         +──────────────────+       │
         │                  │ 1:N             │
         │                  ▼                 │
         │         +──────────────────+       │
         └───────> │     Lecture      │ <─────┘
                   +──────────────────+
                            │ 1:1
                            ▼
                   +──────────────────+       1:N       +──────────────────+
                   │AttendanceSession │ ──────────────> │ AttendanceRecord │
                   +──────────────────+                 +──────────────────+
                                                                 ▲
                                                                 │ N:1
+──────────────────+       1:N       +──────────────────+        │
│     Student      │ ──────────────> │    Enrollment    │ ───────┘
+──────────────────+                 +──────────────────+
         │ 1:N                                │ 1:N
         ▼                                    ▼
+──────────────────+                 +──────────────────+
│ NotificationLog  │                 │     AuditLog     │
+──────────────────+                 +──────────────────+
```

### Entity Dictionary:
1. **Department:** Academic branch (e.g., Computer Engineering, Information Technology).
2. **Program:** Degree structure (e.g., B.Tech, B.Sc, BCA).
3. **AcademicYear & Semester:** Temporal academic bounds (e.g., 2026–2027, Semester V).
4. **ClassDivision:** Specific cohort of students (e.g., Third Year - Div A).
5. **Subject:** Course module with academic code and lecture/lab designation.
6. **Faculty:** Teaching staff profile linked to system user authentication.
7. **Student:** Enrolled student profile with university roll number and institutional email.
8. **Enrollment:** Associative entity linking students to specific classes and elective subjects.
9. **Lecture:** Individual conducted class instance (Date, Time, Faculty, Class, Topics Covered).
10. **AttendanceSession:** Operational session governing the attendance capture process.
11. **AttendanceRecord:** Atomic status entry per student (`PRESENT`, `ABSENT`, `EXCUSED`).
12. **NotificationLog:** Verifiable history of dispatched <75% email warnings.
13. **AuditLog:** Security trail recording administrative modifications and timestamps.

---

## 15. Security, Authorization & Auditability

To satisfy institutional standards, the system incorporates enterprise-grade protection mechanisms:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY & ACCESS POLICIES                                │
├──────────────────────────┬─────────────────────────────────────────────────────────────┤
│ Principle of Least       │ • Students can strictly access only their own records.      │
│ Privilege (RBAC)         │ • Faculty can record/view only assigned subjects & classes. │
│                          │ • Administrators hold monitored structural permissions.     │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Session & Network        │ • HTTPS/TLS 1.3 encryption across all transmission paths.   │
│ Protection               │ • Secure session cookies (HttpOnly, SameSite=Lax).          │
│                          │ • Protection against CSRF, XSS, and SQL Injection.          │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Anti-Tampering &         │ • Attendance sessions freeze after an authorized window.    │
│ Immutability             │ • Retroactive corrections require explicit justification.   │
│                          │ • Full audit logging (user_id, timestamp, old_val).         │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Institutional Identity   │ • Strong password hashing (PBKDF2 / Argon2).                │
│                          │ • Architecture ready for College Single Sign-On (SSO).      │
└──────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 16. Non-Functional Requirements (NFRs)

The system is designed according to rigorous non-functional parameters:

- **NFR-01: Reliability & Transactional Integrity:** All attendance submissions are wrapped in ACID-compliant PostgreSQL database transactions. Partial or corrupted batch submissions are mathematically impossible.
- **NFR-02: Performance & Scalability:** Page load time under standard classroom load must remain below **1.5 seconds**. The system must handle concurrent attendance entry by up to 50 faculty members simultaneously without degradation.
- **NFR-03: Usability & Classroom Efficiency:** Recording attendance for a standard class of 60 students must take **less than 60 seconds** of faculty time via the web interface.
- **NFR-04: Availability:** The platform must maintain **99.5% uptime** during scheduled academic hours (08:00 to 18:00, Monday through Saturday).
- **NFR-05: Maintainability & Code Quality:** Adherence to standard Python PEP 8 style guides, modular Django application separation, and comprehensive docstring documentation.
- **NFR-06: Data Retention & Auditability:** Historical attendance, lecture topics, and notification logs must be preserved for the statutory academic retention period (minimum 5 years).

---

## 17. Deployment & Infrastructure Considerations

The system is designed for cost-effective, high-reliability deployment within a standard college IT environment:

```
+─────────────────────────────────────────────────────────────────────────────+
│                       PROPOSED PRODUCTION DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Operating System:      Ubuntu Server 24.04 LTS (Linux)                     │
│  Web Proxy:             Nginx (Reverse proxy, Gzip/Brotli compression, SSL) │
│  WSGI Application Host: Gunicorn (Green Unicorn, multi-worker process model)│
│  Relational Database:   PostgreSQL 16 (Dedicated local or managed instance) │
│  Containerization:      Docker & Docker Compose (Optional for portability)  │
│  Process Supervisor:    Systemd (Automated service restarts & log monitoring│
│  Backup Automation:     Daily automated pg_dump with off-site snapshotting  │
+─────────────────────────────────────────────────────────────────────────────+
```

> **Infrastructure Note:**  
> The final deployment target (College On-Premises Server vs. Managed Cloud VPS) will be finalized based on the college's server availability and network infrastructure.

---

## 18. Proposed Technology Stack & Technical Rationale

The technical stack is intentionally selected for enterprise maintainability, security, and developer productivity:

| Layer | Proposed Technology | Technical Rationale for Institutional College Deployment |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.11+ / Django 5.x** | Industry standard for institutional web systems. Provides built-in ORM, enterprise-grade authentication, CSRF protection, and a mature administrative interface out of the box. |
| **Database** | **PostgreSQL 16** | Robust relational DBMS offering high concurrency handling, strict ACID compliance, advanced indexing, and zero risk of data corruption under multi-user access. |
| **API Layer** | **Django REST Framework (DRF)** | Enables clean separation of concerns and provides ready-to-use API endpoints if future mobile apps or college portal integrations are required. |
| **Frontend UI** | **Django Templates + HTML5 + Bootstrap 5 + Vanilla JS** | Prioritizes rapid loading, high reliability, zero heavy client-side build steps, full mobile responsiveness, and easy long-term maintenance by student/faculty teams. Avoids unnecessary React SPA complexity. |
| **Email Services** | **Django SMTP Engine / College Mail Relay** | Direct integration with the institution's existing SMTP server (e.g., Google Workspace for Education / Microsoft 365 Exchange). |
| **Document Generation** | **python-docx & ReportLab / WeasyPrint** | Dedicated server-side document compilers ensuring pixel-perfect A4 printing and native Microsoft Word file generation. |
| **Version Control** | **Git / GitHub / GitLab** | Standardized version control, pull request reviews, issue tracking, and collaborative CI/CD pipelines. |

---

## 19. Risks, Constraints & Mitigation Strategies

| Identified Risk | Risk Severity | Potential Impact | Proposed Technical & Operational Mitigation |
| :--- | :--- | :--- | :--- |
| **Proxy Attendance** | Medium | Inaccurate attendance figures if student devices are used. | Implement short session validity windows, faculty verification review before final submission, or restrict capture to faculty device. |
| **Classroom Network Failure** | High | Inability to submit attendance during lecture hours. | Web interface local caching (Service Worker / LocalStorage) or fallback to quick paper log with faculty backfill. |
| **Accidental Clerical Errors** | Medium | False absence recorded for an attending student. | Provide an authorized 24-hour edit window for faculty with mandatory change logging. |
| **Email Delivery Failures** | Medium | Students claiming non-receipt of <75% warning emails. | Maintain a persistent `NotificationLog` table with timestamp, recipient address, and SMTP delivery status code. |
| **Unauthorized Grade/Attendance Tampering** | High | Compromise of academic records. | Role-Based Access Control (RBAC), database transaction logs, and immutable historical audit trails. |
| **Data Loss / Server Failure** | High | Catastrophic loss of semester attendance data. | Automated daily cron backups of PostgreSQL (`pg_dump`) to secure offsite/secondary storage. |

---

## 20. Future Extensions (Out of Current Scope)

The following capabilities represent valuable potential future enhancements that can be integrated seamlessly following successful baseline deployment:

- **Mobile Application:** Dedicated Android/iOS apps for push notifications and offline viewing.
- **Dynamic QR Code Attendance:** High-frequency rotating QR codes displayed on classroom projectors for real-time student scanning.
- **Automated Timetable Synchronization:** Direct integration with the college master scheduling system to pre-populate daily faculty lecture schedules.
- **Biometric / Smart ID Card Integration:** Tap-in attendance using college RFID student identification cards.
- **Predictive Attendance Analytics:** Machine learning models to identify students at risk of chronic absenteeism early in the term.
- **Parent Portal Integration:** Automated SMS / WhatsApp weekly attendance digests to registered parent contacts.

---

## 21. Decisions Pending College Approval

The following critical decisions require review and formal resolution by the college teaching staff:

| Item # | Strategic Decision Item | Current Status | Recommended Proposed Option | Action Required From |
| :--- | :--- | :--- | :--- | :--- |
| **D-01** | Attendance Capture Mechanism | **TBD** | Faculty-controlled device input with optional student verification session. | Teaching Staff |
| **D-02** | Master Data Source & Import | **TBD** | Standardized Excel/CSV batch import template. | Academic Office / HOD |
| **D-03** | User Authentication Method | **TBD** | Django credential system with future College SSO compatibility. | College IT Department |
| **D-04** | Email Notification Trigger Schedule | **TBD** | Automated weekly digest + immediate notification when falling <75%. | Teaching Staff / HOD |
| **D-05** | Official Report Format Standard | **TBD** | Dual export: Editable DOCX for office staff + Signed A4 PDF for archives. | Academic Committee |
| **D-06** | Treatment of Excused Absences | **TBD** | Distinct `EXCUSED` status excluded from absence penalty upon medical proof. | Academic Committee |
| **D-07** | Hosting & Server Infrastructure | **TBD** | College on-premises Linux server with cloud backup. | College IT / System Admin |

---

## 22. Development Roadmap

The project follows a structured engineering lifecycle designed for transparency, rapid iteration, and institutional validation:

```
[ Phase 1: Requirements & Blueprint Review ]
   • Presentation of Project Blueprint to Teaching Staff
   • Formal resolution of Open Questions (D-01 through D-07)
   • Final sign-off on Software Requirements Specification (SRS)
                     │
                     ▼
[ Phase 2: Architectural & Database Engineering ]
   • PostgreSQL relational schema creation & migrations
   • Django core project configuration & security setup
   • Role-Based Access Control (RBAC) & user model implementation
                     │
                     ▼
[ Phase 3: Core Module Implementation ]
   • Academic master data management (Classes, Subjects, Students)
   • Lecture logging & topic tracking interface
   • Attendance capture engine (implementing finalized mechanism)
                     │
                     ▼
[ Phase 4: Calculation, Reporting & Email Subsystems ]
   • Real-time percentage computation engine
   • A4-optimized PDF & DOCX document generation modules
   • SMTP email notification service with audit logging
                     │
                     ▼
[ Phase 5: Verification, Testing & Institutional Pilot ]
   • Unit, integration, and security penetration testing
   • User acceptance testing (UAT) with select faculty members
   • Departmental pilot run in parallel with legacy register
                     │
                     ▼
[ Phase 6: Final Deployment & Operations ]
   • Production deployment on institutional server
   • Faculty & student onboarding and documentation
   • Continuous monitoring and maintenance
```

---
*End of Project Blueprint & Preliminary SRS Document.*
