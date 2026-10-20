# Frontend Architecture & Specifications

The web client lives in [`frontend/`](../../frontend/) — React 18 + TypeScript + Vite + Tailwind CSS (ADR-0002).

---

## Status

- **Current state:** Clickable prototype of every Faculty, HOD and Admin screen, built from the approved reference designs and the AMS design system. Runs on **mock data** (`frontend/src/data/`); not yet wired to the DRF API.
- **Earlier mockups:** Stitch exports remain archived in `archive/previous-version/stitch_college_attendance_management_system.zip`.

## Roles and screens

Only staff sign in (email OTP). **There is no student portal** — students receive attendance alerts by email.

| Role | Screens |
| :--- | :--- |
| Faculty | Today · Roll call (Mode 1 / Mode 2, drafts, offline state) · Timetable · History · Corrections |
| HOD | Department dashboard · Correction approvals · Reports |
| Admin | Students (status changes, Excel/CSV import) · Timetable setup (clash checks) · Reports · Audit log |

Faculty screens are phone-first with a bottom tab bar, and switch to the sidebar layout from 768 px. HOD and Admin screens are desktop-first and collapse to a drawer on phones. The "Prototype · preview as" bar switches roles without signing in again.

## Design rules carried into code

- Status is always colour **plus** a written label (`StatusPill`, `MarkPill`, `RecordPill`).
- Every compliance number is measured against the 75% line; values turn red only when they breach it.
- Unmarked students are never guessed: submitting with gaps produces *Incomplete Records*.
- Destructive-ish actions (cancel session, reject correction, clash override, status change) require a reason and are written to the audit log.
- Classroom screens show only the last four PRN digits; admin and report screens show the full PRN.

## Wiring the real API

`frontend/src/store/AppStore.tsx` is the only place that mutates data. Each action is annotated with the DRF endpoint it maps to — replace the action bodies with API calls (e.g. via TanStack Query) and keep the page components unchanged.

## Build and deploy

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # static files in frontend/dist/
```

`dist/` is plain static HTML/CSS/JS with relative asset paths and hash routing, so it can be uploaded to any folder on an Apache/PHP host (e.g. `public_html/ams/`) with no Node runtime and no rewrite rules.
