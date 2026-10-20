import os
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Attendance Management System — Project Blueprint & Preliminary SRS</title>
<style>
  @page {
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
    @top-center {
      content: "Attendance Management System — Project Blueprint & Preliminary SRS";
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 8pt;
      color: #64748b;
    }
    @bottom-center {
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 8pt;
      color: #64748b;
    }
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.5;
    color: #1e293b;
    background: #fff;
    margin: 0;
    padding: 0;
  }

  /* Cover Page */
  .cover-page {
    page-break-after: always;
    min-height: 250mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 15mm 0 10mm 0;
    border-bottom: 3px solid #0284c7;
  }

  .cover-header {
    border-left: 6px solid #0284c7;
    padding-left: 18px;
    margin-top: 20mm;
  }

  .cover-badge {
    display: inline-block;
    background: #0f172a;
    color: #38bdf8;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 4px;
    margin-bottom: 12px;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin: 0 0 10px 0;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-weight: 500;
    color: #0284c7;
    margin: 0 0 16px 0;
  }

  .cover-description {
    font-size: 10pt;
    color: #475569;
    max-width: 600px;
    line-height: 1.6;
    margin-top: 15px;
  }

  .cover-meta-grid {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 30mm;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }

  .meta-item {
    font-size: 9pt;
  }

  .meta-label {
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }

  .meta-value {
    font-weight: 600;
    color: #0f172a;
  }

  .cover-footer-note {
    font-size: 8pt;
    color: #94a3b8;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
  }

  /* Content Styling */
  h1 {
    font-size: 14pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 22pt;
    margin-bottom: 10pt;
    page-break-after: avoid;
    break-after: avoid;
  }

  h2 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #0369a1;
    margin-top: 14pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
    break-after: avoid;
  }

  h3 {
    font-size: 10pt;
    font-weight: 700;
    color: #334155;
    margin-top: 10pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
    break-after: avoid;
  }

  p {
    margin-top: 0;
    margin-bottom: 8pt;
    text-align: justify;
  }

  ul, ol {
    margin-top: 0;
    margin-bottom: 8pt;
    padding-left: 18px;
  }

  li {
    margin-bottom: 3pt;
  }

  /* Callout Boxes */
  .notice-box {
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    padding: 10px 14px;
    margin: 10pt 0;
    border-radius: 0 6px 6px 0;
    font-size: 9pt;
  }

  .notice-title {
    font-weight: 700;
    color: #0369a1;
    margin-bottom: 4px;
  }

  .warning-box {
    background: #fffbeb;
    border-left: 4px solid #d97706;
    padding: 10px 14px;
    margin: 10pt 0;
    border-radius: 0 6px 6px 0;
    font-size: 9pt;
  }

  .warning-title {
    font-weight: 700;
    color: #b45309;
    margin-bottom: 4px;
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 7.5pt;
    font-weight: 700;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .badge-confirmed {
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
  }

  .badge-proposed {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
  }

  .badge-tbd {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
  }

  .badge-future {
    background: #fdf4ff;
    color: #7e22ce;
    border: 1px solid #f0abfc;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  th {
    background: #0f172a;
    color: #f8fafc;
    font-weight: 700;
    text-align: left;
    padding: 6px 9px;
    border: 1px solid #334155;
    font-size: 8pt;
    letter-spacing: 0.3px;
  }

  td {
    padding: 6px 9px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }

  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Code / Diagram Blocks */
  pre {
    background: #0f172a;
    color: #f1f5f9;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.8pt;
    line-height: 1.35;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 10pt 0;
    overflow-x: auto;
    page-break-inside: avoid;
    break-inside: avoid;
    border: 1px solid #1e293b;
  }

  .diagram-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8pt;
    line-height: 1.35;
    color: #0f172a;
    margin: 10pt 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .page-break {
    page-break-before: always;
    break-before: page;
  }

  /* Print specific header/footer rules */
  @media print {
    body {
      color: #000;
    }
    .cover-page {
      min-height: 90vh;
    }
    pre {
      background: #1e293b !important;
      color: #f8fafc !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    th {
      background: #0f172a !important;
      color: #ffffff !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .badge {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .notice-box, .warning-box, .cover-meta-grid {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-badge">Institutional Engineering Specification</div>
    <h1 class="cover-title">ATTENDANCE MANAGEMENT SYSTEM</h1>
    <div class="cover-subtitle">Project Blueprint / Preliminary Software Requirements Specification</div>
    <div class="cover-description">
      A comprehensive technical blueprint and requirements specification for an institutional-grade attendance recording, lecture syllabus tracking, automated deficit threshold notification, and academic reporting system designed for higher education college deployment.
    </div>
  </div>

  <div class="cover-meta-grid">
    <div class="meta-item">
      <div class="meta-label">Document Nature</div>
      <div class="meta-value">Preliminary Engineering Blueprint & SRS</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Target Deployment Environment</div>
      <div class="meta-value">College / Higher Education Academic Institution</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Document Version</div>
      <div class="meta-value">0.1 — Preliminary Review Draft</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Publication Date</div>
      <div class="meta-value">September 2026 / Academic Year 2026–2027</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Engineering Team</div>
      <div class="meta-value">Lead Student Developers (Python / Django)</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Primary Stakeholders</div>
      <div class="meta-value">College Teaching Staff & Academic Administration</div>
    </div>
  </div>

  <div class="cover-footer-note">
    Confidential Institutional Planning Document — Strictly for Review & Requirement Confirmation with Teaching Staff.
  </div>
</div>

<!-- SECTION 1 -->
<h1>1. Executive Summary</h1>
<p>
The <strong>Attendance Management System (AMS)</strong> is a production-oriented institutional software solution engineered to digitize, standardize, and streamline attendance recording, pedagogical topic delivery logging, regulatory threshold compliance, and official academic documentation across collegiate departments.
</p>
<p>
Unlike conventional academic toy projects or demo scripts, this system is designed from inception as an <strong>institutional-grade management platform</strong> capable of supporting multi-department academic structures, enforcing institutional attendance regulations (notably the statutory 75% attendance rule), maintaining immutable audit trails, and generating standardized documentation ready for administrative and accreditation scrutiny (e.g., NAAC, NBA, and University inspection committees).
</p>
<div class="notice-box">
  <div class="notice-title">Status Categorization Discipline:</div>
  To preserve rigorous engineering integrity during this consultation phase, all specifications are categorized as:
  <strong>(1) Confirmed Requirements</strong> (mandated by teaching staff), <strong>(2) Proposed Design Decisions</strong> (recommended technical solutions), <strong>(3) Open Questions / TBD</strong> (pending institutional determination), or <strong>(4) Future Extensions</strong> (deferred enhancements).
</div>

<!-- SECTION 2 -->
<h1>2. Background and Problem Statement</h1>
<p>
Higher education institutions consistently experience operational inefficiencies and data integrity risks stemming from manual paper attendance registers and disjointed spreadsheets:
</p>
<ul>
  <li><strong>Labor-Intensive Record Keeping:</strong> Faculty manually aggregate daily roll-calls into monthly percentages, consuming valuable teaching hours and introducing mathematical errors.</li>
  <li><strong>Delayed Remedial Intervention:</strong> Students who fall below the required 75% threshold are frequently detected only at the end of the semester, eliminating opportunities for timely academic counselling.</li>
  <li><strong>Absence of Pedagogical Auditing:</strong> Conventional attendance logs record <em>who</em> was present, but entirely omit <em>what syllabus topics</em> were delivered during that specific lecture block.</li>
  <li><strong>Disjointed Administrative Reporting:</strong> Producing standardized attendance lists for faculty meetings, university submissions, and student notices requires tedious, error-prone manual re-entry into Microsoft Word or spreadsheet templates.</li>
</ul>

<!-- SECTION 3 -->
<h1>3. Objectives</h1>
<p>Derived directly from confirmed faculty requirements, the core engineering objectives are:</p>
<ol>
  <li><strong>Classroom Attendance Recording:</strong> Enable teaching staff to record student attendance efficiently using platform/devices available within the classroom.</li>
  <li><strong>Pedagogical Topic Tracking:</strong> Maintain an authoritative institutional record of every conducted lecture, linking class, subject, faculty, timestamps, and specific syllabus points covered.</li>
  <li><strong>Real-Time Percentage Computation:</strong> Automatically calculate accurate subject-wise and cumulative semester attendance metrics.</li>
  <li><strong>Automated Threshold Warning Dispatch:</strong> Systematically detect students falling below 75% attendance and dispatch automated warning notifications to their official college email.</li>
  <li><strong>A4 & Word-Compatible Document Export:</strong> Generate publication-quality monthly and semester reports formatted strictly for ISO A4 printing and Microsoft Word (DOCX) administrative workflows.</li>
  <li><strong>Enterprise Data Integrity:</strong> Guarantee transactional reliability, role-based authorization, and tamper-resistant auditability.</li>
</ol>

<!-- SECTION 4 -->
<h1>4. Scope of the System</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 50%;">In Scope (Confirmed & Proposed Base Phase)</th>
      <th style="width: 50%;">Out of Scope / Not Yet Confirmed (Advanced Scope)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        • Multi-tier academic hierarchy (Departments, Semesters, Divisions, Subjects)<br>
        • Role-Based Access Control (Student, Faculty, Academic Admin)<br>
        • Lecture session logging with mandatory syllabus topic entries<br>
        • Atomic attendance capture linked directly to lecture instances<br>
        • Automated 75% threshold monitoring engine<br>
        • SMTP email dispatcher for student warning notices<br>
        • ISO A4-optimized printable PDF and Microsoft Word (.docx) exports<br>
        • Faculty edit window & administrative audit logging
      </td>
      <td>
        • Biometric fingerprint / iris hardware integration<br>
        • Facial recognition / computer vision attendance<br>
        • GPS / geofencing validation<br>
        • RFID / NFC smart student ID card readers<br>
        • Native mobile apps (iOS/Android) — Web-first responsive UI<br>
        • Automated timetable scheduling & room allocation engines<br>
        <em>*Advanced mechanisms will only be introduced upon formal institutional request.</em>
      </td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 5 -->
<h1>5. Stakeholders and User Roles</h1>
<p>The system defines three core institutional user roles with strict boundary controls:</p>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 22%;">Institutional Role</th>
      <th style="width: 48%;">Proposed Responsibilities</th>
      <th style="width: 18%;">Access Boundaries</th>
      <th style="width: 12%;">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Student</strong></td>
      <td>
        • View authenticated personal attendance profile and subject breakdown.<br>
        • Track syllabus topics covered in conducted lectures.<br>
        • Receive automated institutional email alerts if attendance falls &lt;75%.
      </td>
      <td>Strictly Read-Only for personal records.</td>
      <td><span class="badge badge-proposed">Proposed</span></td>
    </tr>
    <tr>
      <td><strong>Teaching Faculty</strong></td>
      <td>
        • Create lecture logs and record topics/points covered.<br>
        • Record attendance for assigned classes and subjects.<br>
        • Generate, preview, and download monthly and semester reports.<br>
        • Submit authorized attendance corrections within permitted timeframes.
      </td>
      <td>Read/Write for assigned classes and courses only.</td>
      <td><span class="badge badge-proposed">Proposed</span></td>
    </tr>
    <tr>
      <td><strong>Academic Administrator / HOD</strong></td>
      <td>
        • Manage academic master data (departments, classes, courses, enrollments).<br>
        • Oversee department-wide attendance compliance and analytics.<br>
        • Audit and authorize post-freeze attendance amendments.<br>
        • Generate institutional consolidation reports for academic councils.
      </td>
      <td>Departmental or Institutional Global Administrative Access.</td>
      <td><span class="badge badge-tbd">Pending TBD</span></td>
    </tr>
  </tbody>
</table>

<!-- SECTION 6 -->
<h1>6. Confirmed Functional Requirements</h1>
<p>The following requirements constitute the authoritative baseline established by the teaching staff:</p>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 10%;">Req ID</th>
      <th style="width: 28%;">Requirement Title</th>
      <th style="width: 12%;">Priority</th>
      <th style="width: 15%;">Status</th>
      <th style="width: 35%;">Institutional Reference & Summary</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>FR-01</strong></td>
      <td>Attendance Recording</td>
      <td>High</td>
      <td><span class="badge badge-confirmed">Confirmed</span></td>
      <td>Teaching staff must be able to record student attendance using platform/devices available to students. (Capture mechanism TBD).</td>
    </tr>
    <tr>
      <td><strong>FR-02</strong></td>
      <td>Monthly & Academic Reports</td>
      <td>High</td>
      <td><span class="badge badge-confirmed">Confirmed</span></td>
      <td>System must generate monthly summaries and comprehensive semester attendance reports.</td>
    </tr>
    <tr>
      <td><strong>FR-03</strong></td>
      <td>Lecture & Topic Tracking</td>
      <td>High</td>
      <td><span class="badge badge-confirmed">Confirmed</span></td>
      <td>Recording of conducted lectures, date/time duration, and specific syllabus topics/points covered.</td>
    </tr>
    <tr>
      <td><strong>FR-04</strong></td>
      <td>A4 & Word-Compatible Reporting</td>
      <td>High</td>
      <td><span class="badge badge-confirmed">Confirmed</span></td>
      <td>Generated reports must be optimized for A4 paper and easy integration into Microsoft Word (.docx).</td>
    </tr>
    <tr>
      <td><strong>FR-05</strong></td>
      <td>Attendance % & &lt;75% Email Alerts</td>
      <td>High</td>
      <td><span class="badge badge-confirmed">Confirmed</span></td>
      <td>Accurate calculation of subject and semester %; automated warning emails to students below 75%.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 7 -->
<h1>7. Open Questions and Clarifications Required</h1>
<div class="warning-box">
  <div class="warning-title">Action Required from Teaching Staff & College Administration:</div>
  The following items require formal institutional decisions to finalize design and proceed with implementation:
</div>

<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 16%;">Domain</th>
      <th style="width: 6%;">#</th>
      <th style="width: 40%;">Clarification Question</th>
      <th style="width: 28%;">Options / Engineering Implications</th>
      <th style="width: 10%;">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="4"><strong>Attendance Capture</strong></td>
      <td>Q1</td>
      <td>What specific workflow is intended by <em>"using the platform/device available to students"</em>?</td>
      <td>(A) Faculty manual entry, (B) Faculty-initiated session with student confirmation, (C) Dynamic token entry.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q2</td>
      <td>How should proxy attendance be mitigated if student devices are involved?</td>
      <td>Short session countdown, one-time code, campus subnet check, or faculty roster sign-off.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q3</td>
      <td>What is the policy for retroactive attendance corrections?</td>
      <td>Faculty edit window (e.g. 24h) vs. HOD approval required after session locking.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q4</td>
      <td>What fallback applies when classroom internet or student device fails?</td>
      <td>Faculty manual override portal or offline paper log with batch backfill.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>College Infrastructure</strong></td>
      <td>Q5</td>
      <td>Does the college have an existing Student Information System (SIS) / ERP?</td>
      <td>Standardized CSV/Excel batch upload vs. REST API database sync.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q6</td>
      <td>Is there an institutional Single Sign-On (SSO) service available?</td>
      <td>Google Workspace / Microsoft 365 OAuth2 vs. standalone Django credentials.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q7</td>
      <td>Are student college email addresses assigned and active?</td>
      <td>Institutional domain (@college.edu) vs. personal email addresses.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>Academic Rules</strong></td>
      <td>Q8</td>
      <td>How are cancelled lectures and official holidays handled in calculation?</td>
      <td>Excluded from total applicable lectures (denominator).</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q9</td>
      <td>How are officially sanctioned absences (Medical, Sports, NSS/NCC) treated?</td>
      <td>Counted as present, marked excused, or excluded from calculation?</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q10</td>
      <td>Are practical/lab sessions calculated separately or with weighted credits?</td>
      <td>1 Lab = 2 Lecture credits vs. independent practical attendance roster.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Email Policy</strong></td>
      <td>Q11</td>
      <td>What is the exact trigger schedule for &lt;75% warning emails?</td>
      <td>(A) Immediate on drop, (B) Weekly digest, (C) Monthly checkpoint batch, (D) Manual HOD trigger.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q12</td>
      <td>Should warning emails be copied (CC) to Faculty Advisors or HODs?</td>
      <td>Direct to student only vs. departmental escalation copy.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Reporting & Hosting</strong></td>
      <td>Q13</td>
      <td>Is Word (DOCX), PDF, or both required as official standards?</td>
      <td>DOCX for office reformatting; PDF for official signed archives.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
    <tr>
      <td>Q14</td>
      <td>Where will the server be hosted (On-premises server vs. Cloud)?</td>
      <td>College server room / intranet vs. dedicated Cloud VPS.</td>
      <td><span class="badge badge-tbd">TBD</span></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 8 -->
<h1>8. Proposed System Workflow</h1>
<p>The end-to-end dataflow illustrates how academic records progress from master data creation to attendance capture, threshold checking, and report generation:</p>

<div class="diagram-box">
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
│        (Faculty Review -&gt; Timestamped Database Commit)       │
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
│  • Monthly Class Summaries │     │   (Checks: Attendance &lt; 75%)│
│  • Semester Final Sheets  │     +─────────────┬─────────────+
│  • Subject-Wise Audits    │                   │ (If &lt; 75%)
│  • A4 Word / PDF Exports  │                   ▼
+───────────────────────────+     +───────────────────────────+
                                  │   EMAIL DISPATCH SERVICE  │
                                  │ (Institutional Warning to │
                                  │   Student College Email)  │
                                  +───────────────────────────+
</div>

<!-- SECTION 9 -->
<h1>9. Proposed Lecture & Topic Tracking Model</h1>
<p>
In this institutional architecture, the <strong>Lecture is the central operational entity</strong>. Attendance is never recorded as an isolated date-marker; it is directly attached to a specific instructional session:
</p>

<div class="diagram-box">
SUBJECT (e.g., CS301 - Database Systems)
   │
   └── LECTURE SESSION
         ├── Class / Division (e.g., Third Year, Div A)
         ├── Assigned Faculty (e.g., Prof. Smith)
         ├── Scheduled / Actual Date (e.g., 2026-09-05)
         ├── Start Time &amp; End Time (e.g., 09:00 - 10:00)
         ├── Lecture Type (Theory / Practical Lab / Tutorial)
         ├── Syllabus Topics / Points Covered (Structured Bullet Points)
         │
         └── ATTENDANCE SESSION
               ├── Session Status (Draft / Open / Finalized / Locked)
               └── ATTENDANCE RECORDS (1 per Enrolled Student)
                     ├── Student ID
                     ├── Status (Present / Absent / Excused)
                     └── Timestamp
</div>

<p><strong>Institutional Benefits:</strong> (1) Fulfills curriculum audit requirements (e.g. NAAC / NBA), (2) Provides student transparency regarding concepts missed during absences, and (3) Ensures instructional continuity for substitute faculty.</p>

<!-- SECTION 10 -->
<h1>10. User Inputs and System Outputs</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 50%;">User Inputs</th>
      <th style="width: 50%;">System-Generated Outputs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <strong>Student Inputs:</strong><br>
        • Login credentials<br>
        • Session confirmation (if student-side mechanism approved - TBD)<br><br>
        <strong>Faculty Inputs:</strong><br>
        • Subject, Class, Date, Start/End Time<br>
        • Detailed syllabus points/topics covered<br>
        • Present / Absent markers per student roster<br>
        • Justification for retroactive corrections<br><br>
        <strong>Administrator Inputs:</strong><br>
        • Master catalogs: Programs, Years, Semesters, Divisions<br>
        • Faculty & Student profiles, Subject course allocations
      </td>
      <td>
        <strong>Student Outputs:</strong><br>
        • Real-time personal attendance dashboard<br>
        • Subject-wise attendance % and deficit indicator<br>
        • Summary log of syllabus points covered<br>
        • Official &lt;75% warning email notifications<br><br>
        <strong>Faculty & Administrator Outputs:</strong><br>
        • Live class roster attendance management views<br>
        • Monthly attendance summary tables<br>
        • Cumulative semester final attendance sheets<br>
        • Exportable A4 printable PDFs and editable Word (.docx) documents<br>
        • Dispatched email audit logs
      </td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 11 -->
<h1>11. Attendance Calculation Methodology</h1>
<p>The system enforces mathematically rigorous attendance tracking:</p>

<h3>1. Subject-Wise Attendance Percentage:</h3>
<pre>Subject Attendance % = (Present Lectures in Subject / Total Applicable Lectures in Subject) * 100</pre>
<p>Where Total Applicable Lectures = Total conducted lectures minus officially cancelled lectures.</p>

<h3>2. Cumulative Semester Attendance Percentage:</h3>
<pre>Semester Attendance % = (Total Present Lectures Across All Subjects / Total Applicable Lectures Across All Subjects) * 100</pre>

<h3>3. Statutory 75% Warning Evaluation Rule:</h3>
<ul>
  <li>If <strong>Semester Attendance % &lt; 75.0%</strong>, the student is marked in <em>Overall Deficit</em>.</li>
  <li>If <strong>Subject Attendance % &lt; 75.0%</strong> for any enrolled course, the student is marked in <em>Subject-Specific Deficit</em>.</li>
  <li><em>Trigger:</em> The notification service drafts and dispatches an official institutional warning email to the student's registered college address.</li>
</ul>

<!-- SECTION 12 -->
<h1>12. Reporting Design & A4/Word Integration</h1>
<p>
To satisfy <strong>FR-02</strong> and <strong>FR-04</strong>, the reporting module is decoupled from presentation and generated directly from the authoritative PostgreSQL database:
</p>
<ul>
  <li><strong>A4 Layout Optimization:</strong> Formatted strictly for standard 210 × 297 mm page dimensions, with 0.5–0.75 in margins, repeating table headers across page breaks, and zero horizontal column overflow.</li>
  <li><strong>Dual-Format Architecture:</strong>
    <ul>
      <li><strong>Microsoft Word (.docx):</strong> Generated using server-side OpenXML formatting, allowing academic departments to incorporate attendance tables directly into administrative notices and formal college templates.</li>
      <li><strong>Printable PDF (.pdf):</strong> Tamper-resistant, publication-quality format containing institutional headers, department seals, and signature blocks (*Subject Teacher*, *Class Coordinator*, *Head of Department*).</li>
    </ul>
  </li>
  <li><strong>Standard Report Types:</strong> (1) Monthly Class Attendance Sheets, (2) Cumulative Semester Attendance Sheets, (3) Subject-Specific Audit Sheets, and (4) Below-75% Deficit Summaries.</li>
</ul>

<!-- SECTION 13 -->
<h1>13. Proposed System Architecture</h1>
<div class="diagram-box">
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
│  │   Authentication   │ │     Academics      │ │   Lecture &amp; Attendance  │  │
│  │   &amp; RBAC Module    │ │   Master Module    │ │       Core Engine       │  │
│  └────────────────────┘ └────────────────────┘ └─────────────────────────┘  │
│  ┌────────────────────┐ ┌────────────────────┐ ┌─────────────────────────┐  │
│  │  Calculation and   │ │   A4 PDF &amp; DOCX    │ │    Email Dispatcher     │  │
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
</div>

<!-- SECTION 14 -->
<h1>14. Preliminary Conceptual Data Model</h1>
<p>The relational database schema is structured around normalized institutional entities:</p>
<ul>
  <li><strong>Department &amp; Program:</strong> Academic hierarchy and degree structures.</li>
  <li><strong>AcademicYear &amp; Semester:</strong> Temporal academic terms (e.g. 2026–2027, Sem V).</li>
  <li><strong>ClassDivision &amp; Subject:</strong> Student cohorts and course catalog mappings.</li>
  <li><strong>Faculty &amp; Student:</strong> User identity profiles linked to system authentication.</li>
  <li><strong>Enrollment:</strong> Maps students to specific class divisions and elective subjects.</li>
  <li><strong>Lecture:</strong> Conducted session (Date, Time, Faculty, Class, Syllabus Topics Covered).</li>
  <li><strong>AttendanceSession &amp; Record:</strong> Operational session linking individual atomic student statuses (`PRESENT`, `ABSENT`, `EXCUSED`).</li>
  <li><strong>NotificationLog &amp; AuditLog:</strong> Dispatched email audit trail and security modification log.</li>
</ul>

<div class="page-break"></div>

<!-- SECTION 15 & 16 -->
<h1>15. Security, Authorization & Auditability</h1>
<ul>
  <li><strong>Principle of Least Privilege (RBAC):</strong> Students access solely their personal records; faculty access assigned classes; administrators hold audited institutional access.</li>
  <li><strong>Session Security & Defense-in-Depth:</strong> HTTPS/TLS encryption, CSRF protection on all forms, SQL injection defense via Django ORM, and HttpOnly session cookies.</li>
  <li><strong>Immutability & Correction Logs:</strong> Attendance sessions freeze after an authorized window. All post-freeze modifications require justification and generate immutable audit logs (`user_id`, `timestamp`, `previous_value`, `new_value`).</li>
</ul>

<h1>16. Non-Functional Requirements (NFRs)</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 25%;">Quality Attribute</th>
      <th style="width: 75%;">Institutional Engineering Specification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Reliability</strong></td>
      <td>ACID transactions on all batch attendance submissions to prevent partial or corrupted records.</td>
    </tr>
    <tr>
      <td><strong>Performance</strong></td>
      <td>Server response time &lt; 1.5 seconds under standard load. Concurrent entry by 50+ faculty simultaneously.</td>
    </tr>
    <tr>
      <td><strong>Usability</strong></td>
      <td>Classroom attendance entry workflow completed in &lt; 60 seconds for a roster of 60 students.</td>
    </tr>
    <tr>
      <td><strong>Availability</strong></td>
      <td>99.5% uptime during operational college hours (08:00 to 18:00, Monday through Saturday).</td>
    </tr>
    <tr>
      <td><strong>Data Retention</strong></td>
      <td>Historical attendance and syllabus topic logs preserved for statutory minimum of 5 years.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 17 & 18 -->
<h1>17. Deployment & Technology Stack</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 20%;">Component</th>
      <th style="width: 25%;">Proposed Technology</th>
      <th style="width: 55%;">Technical Rationale</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Backend</strong></td>
      <td>Python 3.11+ / Django 5.x</td>
      <td>Industry standard for institutional systems. Built-in ORM, robust RBAC, automatic CSRF/XSS protection, mature administrative dashboard.</td>
    </tr>
    <tr>
      <td><strong>Database</strong></td>
      <td>PostgreSQL 16</td>
      <td>Enterprise-grade relational database with high concurrent transaction handling, data integrity constraints, and rock-solid reliability.</td>
    </tr>
    <tr>
      <td><strong>Frontend UI</strong></td>
      <td>Django Templates + Bootstrap 5 + Vanilla JS</td>
      <td>Lightning-fast page loads, full mobile/tablet responsiveness, zero client-side build complexity, easy long-term institutional maintainability.</td>
    </tr>
    <tr>
      <td><strong>API Layer</strong></td>
      <td>Django REST Framework (DRF)</td>
      <td>Provides modular endpoints for future integrations (e.g. mobile app, college ERP) without altering core models.</td>
    </tr>
    <tr>
      <td><strong>Documents</strong></td>
      <td>python-docx &amp; WeasyPrint / ReportLab</td>
      <td>Server-side compiled A4 PDFs and native Microsoft Word (.docx) document generation.</td>
    </tr>
    <tr>
      <td><strong>Hosting</strong></td>
      <td>Linux (Ubuntu 24.04), Nginx, Gunicorn</td>
      <td>Proven production stack for high-availability web applications with reverse proxying and automated systemd management.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 19 & 20 -->
<h1>18. Risks & Mitigation Strategies</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 25%;">Identified Risk</th>
      <th style="width: 12%;">Severity</th>
      <th style="width: 63%;">Proposed Technical &amp; Operational Mitigation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Proxy Attendance</td>
      <td>Medium</td>
      <td>Short session timer, faculty roster verification before final locking, or faculty-device-only entry.</td>
    </tr>
    <tr>
      <td>Classroom Network Failure</td>
      <td>High</td>
      <td>Client-side offline caching (LocalStorage) or fallback paper roster with batch backfill.</td>
    </tr>
    <tr>
      <td>Clerical Absence Errors</td>
      <td>Medium</td>
      <td>Authorized 24-hour faculty correction window with mandatory change audit logging.</td>
    </tr>
    <tr>
      <td>Email Delivery Failures</td>
      <td>Medium</td>
      <td>Persistent `NotificationLog` table tracking SMTP delivery status codes and timestamps.</td>
    </tr>
    <tr>
      <td>Data Loss / Hardware Failure</td>
      <td>High</td>
      <td>Automated daily PostgreSQL `pg_dump` backups archived to secure secondary/cloud storage.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 21 & 22 -->
<h1>19. Decisions Pending Approval & Development Roadmap</h1>
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 10%;">Item #</th>
      <th style="width: 32%;">Strategic Decision</th>
      <th style="width: 12%;">Status</th>
      <th style="width: 46%;">Recommended Option for Review</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>D-01</strong></td>
      <td>Attendance Capture Workflow</td>
      <td><span class="badge badge-tbd">TBD</span></td>
      <td>Faculty-controlled interface with optional student verification session.</td>
    </tr>
    <tr>
      <td><strong>D-02</strong></td>
      <td>Master Data Import</td>
      <td><span class="badge badge-tbd">TBD</span></td>
      <td>Standardized CSV / Excel batch import template.</td>
    </tr>
    <tr>
      <td><strong>D-03</strong></td>
      <td>Email Notification Trigger</td>
      <td><span class="badge badge-tbd">TBD</span></td>
      <td>Weekly automated digest + immediate alert upon dropping below 75%.</td>
    </tr>
    <tr>
      <td><strong>D-04</strong></td>
      <td>Official Report Standard</td>
      <td><span class="badge badge-tbd">TBD</span></td>
      <td>Dual Export: Microsoft Word (.docx) + Signed A4 PDF (.pdf).</td>
    </tr>
    <tr>
      <td><strong>D-05</strong></td>
      <td>Excused Absence Handling</td>
      <td><span class="badge badge-tbd">TBD</span></td>
      <td>Formal `EXCUSED` status excluded from absence penalty upon medical proof.</td>
    </tr>
  </tbody>
</table>

<div class="diagram-box" style="margin-top: 15px;">
[Phase 1: Requirements &amp; Blueprint Sign-Off] ──&gt; [Phase 2: Database &amp; Security Architecture]
                                                                  │
                                                                  ▼
[Phase 4: Reports, Calculation &amp; Email Engine] &lt;── [Phase 3: Core Attendance &amp; Lecture Module]
             │
             ▼
[Phase 5: Testing &amp; Departmental Pilot Run]  ──&gt; [Phase 6: Full Institutional Deployment]
</div>

</body>
</html>
"""

def generate_html():
    path = r"c:\Users\DELL\Downloads\Attendance\Attendance_Management_System_Blueprint_SRS.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"HTML written to {path}")
    return path

def generate_pdf(html_path):
    pdf_path = r"c:\Users\DELL\Downloads\Attendance\Attendance_Management_System_Blueprint_SRS.pdf"
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    print("Running Edge command:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Edge return code:", res.returncode)
    if os.path.exists(pdf_path):
        print(f"PDF successfully generated at {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
    else:
        print("PDF generation failed:", res.stderr)

def generate_docx():
    docx_path = r"c:\Users\DELL\Downloads\Attendance\Attendance_Management_System_Blueprint_SRS.docx"
    doc = docx.Document()
    
    # Page setup - A4
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    
    # Title
    title = doc.add_paragraph()
    title_run = title.add_run("ATTENDANCE MANAGEMENT SYSTEM\n")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    
    sub_run = title.add_run("Project Blueprint & Preliminary Software Requirements Specification (SRS)\n")
    sub_run.font.size = Pt(13)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(2, 132, 199)
    
    desc_run = title.add_run("Intended Institutional Deployment: Higher Education College / Academic Institution\nVersion: 0.1 — Preliminary Review Draft | Date: September 2026")
    desc_run.font.size = Pt(9.5)
    desc_run.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_paragraph("―" * 55)
    
    # Notice
    p_notice = doc.add_paragraph()
    p_notice_run = p_notice.add_run("Document Control Notice: This blueprint explicitly distinguishes between: (1) Confirmed Requirements from teaching staff, (2) Proposed Design Decisions, (3) Open Questions / TBD requiring institutional confirmation, and (4) Optional Future Extensions.")
    p_notice_run.font.italic = True
    p_notice_run.font.size = Pt(9)
    p_notice_run.font.color.rgb = RGBColor(3, 105, 161)
    
    # Sections
    sections_data = [
        ("1. Executive Summary", 
         "The Attendance Management System (AMS) is an institutional-grade web software solution engineered to modernize student attendance recording, curricular lecture tracking, regulatory 75% threshold compliance, and official academic reporting. Designed for multi-department college deployment with strict security, auditability, and A4/Word document compatibility."),
        
        ("2. Background & Problem Statement",
         "Higher education institutions face significant challenges with manual paper registers: (1) Labor-intensive calculation of monthly/semester percentages, (2) Delayed intervention for chronic absenteeism, (3) Lack of structured topic/syllabus audit trails for conducted lectures, and (4) Time-consuming manual preparation of official Word/A4 reports for academic councils and accreditation bodies (NAAC/NBA)."),
        
        ("3. Core Objectives",
         "• Enable classroom attendance recording on available devices.\n• Maintain verifiable lecture logs with syllabus topics/points covered.\n• Compute real-time subject-wise and semester-wise attendance percentages.\n• Automatically dispatch <75% warning emails to students' college email addresses.\n• Generate publication-quality A4 printable PDF and Microsoft Word (DOCX) reports.\n• Guarantee institutional data integrity, role-based security, and audit trails."),
        
        ("4. System Scope",
         "IN SCOPE: Multi-department hierarchy, RBAC (Student/Faculty/Admin), lecture logging with syllabus topics, attendance session management, 75% rule engine, SMTP warning email dispatcher, A4 PDF & DOCX export engine, administrative audit logging.\n\nOUT OF SCOPE (BASE PHASE): Biometric fingerprint hardware, facial recognition, GPS geofencing, RFID cards, and native mobile apps (responsive web-first architecture)."),
    ]
    
    for heading, text in sections_data:
        h = doc.add_heading(heading, level=1)
        h.runs[0].font.color.rgb = RGBColor(15, 23, 42)
        h.runs[0].font.size = Pt(13)
        p = doc.add_paragraph(text)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(8)
        
    # Table of Confirmed Requirements
    h = doc.add_heading("5. Confirmed Functional Requirements", level=1)
    h.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    h.runs[0].font.size = Pt(13)
    
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["Req ID", "Requirement Title", "Priority", "Institutional Status"]
    for i, title_text in enumerate(headers):
        hdr_cells[i].text = title_text
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F172A"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shd)
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(8.5)
                
    reqs = [
        ("FR-01", "Attendance Recording", "High", "CONFIRMED (Mechanism TBD)"),
        ("FR-02", "Monthly & Academic Reports", "High", "CONFIRMED"),
        ("FR-03", "Lecture & Topic Tracking", "High", "CONFIRMED"),
        ("FR-04", "Offline Word & A4 Reporting", "High", "CONFIRMED"),
        ("FR-05", "Attendance % & <75% Email Alerts", "High", "CONFIRMED"),
    ]
    for r_id, title_text, prio, stat in reqs:
        row = table.add_row()
        row.cells[0].text = r_id
        row.cells[1].text = title_text
        row.cells[2].text = prio
        row.cells[3].text = stat
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    
    # Table of Decisions Pending Approval
    h = doc.add_heading("6. Decisions Pending College Approval (TBD)", level=1)
    h.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    h.runs[0].font.size = Pt(13)
    
    table2 = doc.add_table(rows=1, cols=3)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells2 = table2.rows[0].cells
    headers2 = ["Item #", "Strategic Decision Item", "Recommended Proposed Option"]
    for i, title_text in enumerate(headers2):
        hdr_cells2[i].text = title_text
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F172A"/>')
        hdr_cells2[i]._tc.get_or_add_tcPr().append(shd)
        for p in hdr_cells2[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(8.5)
                
    decisions = [
        ("D-01", "Attendance Capture Mechanism", "Faculty-controlled web entry with optional student verification session."),
        ("D-02", "Master Data Import", "Standardized CSV / Excel batch upload templates for classes and enrollments."),
        ("D-03", "Email Notification Trigger", "Automated weekly digest + immediate notification when falling <75%."),
        ("D-04", "Official Report Standard", "Dual Export: Editable Microsoft Word (.docx) + Signed A4 PDF (.pdf)."),
        ("D-05", "Excused Absence Handling", "Formal EXCUSED status excluded from absence penalty upon medical proof."),
        ("D-06", "Deployment Infrastructure", "College on-premises Linux server with automated offsite backup."),
    ]
    for d_id, title_text, prop in decisions:
        row = table2.add_row()
        row.cells[0].text = d_id
        row.cells[1].text = title_text
        row.cells[2].text = prop
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    
    # Technology Stack
    h = doc.add_heading("7. Proposed Production Technology Stack", level=1)
    h.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    h.runs[0].font.size = Pt(13)
    
    p_tech = doc.add_paragraph()
    p_tech.add_run("• Backend: ").bold = True
    p_tech.add_run("Python 3.11+ / Django 5.x (Robust ORM, RBAC, CSRF/XSS protection, Admin UI)\n")
    p_tech.add_run("• Database: ").bold = True
    p_tech.add_run("PostgreSQL 16 (ACID compliance, relational integrity, high concurrency)\n")
    p_tech.add_run("• Frontend: ").bold = True
    p_tech.add_run("Django Templates + Bootstrap 5 + Vanilla JS (Rapid load, mobile responsive, high maintainability)\n")
    p_tech.add_run("• API Layer: ").bold = True
    p_tech.add_run("Django REST Framework (DRF) for future integrations\n")
    p_tech.add_run("• Document Export: ").bold = True
    p_tech.add_run("python-docx & WeasyPrint / ReportLab for pixel-perfect A4 PDF and native DOCX generation\n")
    p_tech.add_run("• Production Host: ").bold = True
    p_tech.add_run("Ubuntu Linux, Nginx, Gunicorn, Systemd, Automated pg_dump backups")
    
    doc.save(docx_path)
    print(f"DOCX successfully generated at {docx_path}")

if __name__ == "__main__":
    html_file = generate_html()
    generate_pdf(html_file)
    generate_docx()
