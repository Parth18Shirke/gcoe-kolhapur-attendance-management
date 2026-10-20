// Domain types. Names mirror the Django models (see backend/apps/*/models.py)
// so the mock data layer can later be swapped for the DRF API.

export type Role = 'faculty' | 'hod' | 'admin';

export type Tone = 'green' | 'red' | 'amber' | 'gray' | 'info';

export type ClassKey = 'SY-A' | 'SY-B' | 'TY-A' | 'TY-B' | 'BT-A' | 'BT-B';

export type StudentStatus = 'Active' | 'Inactive' | 'Archived';

export interface Student {
  prn: string;
  name: string;
  classKey: ClassKey;
  email: string;
  status: StudentStatus;
  /** Lab batch within the division, e.g. "A1" / "B2". */
  batch: string;
}

export interface Subject {
  code: string;
  name: string;
  classYear: 'SY' | 'TY' | 'BT';
}

export interface Person {
  id: string;
  name: string;
  initials: string;
  email: string;
  role: Role;
}

export type Day = 0 | 1 | 2 | 3 | 4 | 5; // Mon..Sat
export type SlotType = 'theory' | 'lab';

/** A recurring weekly timetable slot (timetable.TimetableSlot). */
export interface Slot {
  id: string;
  day: Day;
  /** Index into PERIODS (0 = 09:15). Labs occupy two consecutive periods. */
  period: number;
  type: SlotType;
  subject: string; // subject code
  facultyId: string;
  classKey: ClassKey;
  batch?: string;
  room: string;
}

/** timetable.LectureSession.status */
export type SessionStatus = 'scheduled' | 'conducted' | 'cancelled';
/** attendance.SessionLifecycleState.status */
export type RecordState = 'draft' | 'incomplete' | 'reviewed' | 'finalized';
export type Mark = 'present' | 'absent' | 'unmarked';
export type MarkMode = 'mode1' | 'mode2';

export interface LectureSession {
  id: string;
  /** ISO date YYYY-MM-DD */
  date: string;
  period: number;
  type: SlotType;
  subject: string;
  facultyId: string;
  classKey: ClassKey;
  batch?: string;
  room: string;
  status: SessionStatus;
  record?: RecordState;
  mode: MarkMode;
  marks: Record<string, Mark>; // prn -> mark
  topic?: string;
  cancelReason?: string;
  rescheduledNote?: string;
  /** Local draft not yet acknowledged by the server. */
  pendingSync?: boolean;
  draftSavedAt?: string;
}

export type CorrectionStatus = 'auto' | 'pending' | 'approved' | 'rejected';

export interface Correction {
  id: string;
  prn: string;
  sessionId: string;
  facultyId: string;
  from: Mark;
  to: Mark;
  reason: string;
  status: CorrectionStatus;
  requestedAt: string; // ISO datetime
  decidedAt?: string;
  decisionNote?: string;
}

export type AuditRole = 'Faculty' | 'HOD' | 'Admin' | 'System';

export interface AuditEntry {
  id: string;
  at: string; // ISO datetime
  actor: string;
  role: AuditRole;
  action: string;
  entity: string;
  old: string;
  next: string;
}
