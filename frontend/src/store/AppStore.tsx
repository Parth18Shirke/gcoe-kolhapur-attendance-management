import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import type {
  AuditEntry, AuditRole, Correction, LectureSession, Mark, MarkMode, Role, Slot, Student, StudentStatus,
} from '../types';
import { CLASSES, NOW, PEOPLE, PERIODS, ROLE_USER, SUBJECTS, TODAY } from '../data/catalog';
import { SEED_STUDENTS, computeStats, type StudentStat } from '../data/students';
import { SEED_SLOTS } from '../data/timetable';
import { EXTERNAL_SESSIONS, SEED_AUDIT, SEED_CORRECTIONS, seedSessions } from '../data/sessions';
import { fmtDayMonth, hoursBetween, sessionStart } from '../lib/format';

/**
 * In-memory prototype store. Every action here maps to one DRF endpoint
 * (noted per action) and appends to the audit log the same way the server does.
 * Swap the bodies for API calls when wiring the real backend.
 */

const ROLE_KEY = 'ams.role';
const AUDIT_ROLE: Record<Role, AuditRole> = { faculty: 'Faculty', hod: 'HOD', admin: 'Admin' };

/** Today's date (prototype clock) with the real time of day, for new audit stamps. */
function stamp(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, '0');
  return `${TODAY}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

const readRole = (): Role | null => {
  try {
    const r = localStorage.getItem(ROLE_KEY);
    return r === 'faculty' || r === 'hod' || r === 'admin' ? r : null;
  } catch {
    return null;
  }
};

export const sessionLabel = (s: Pick<LectureSession, 'subject' | 'classKey' | 'date' | 'period'> & { batch?: string }) =>
  `${s.subject} · ${CLASSES[s.classKey].label}${s.batch ? ` · ${s.batch}` : ''} · ${fmtDayMonth(s.date)} ${PERIODS[s.period].start}`;

export function markCounts(session: LectureSession, roster: Student[]) {
  let present = 0, absent = 0, unmarked = 0;
  roster.forEach((st) => {
    const m = session.marks[st.prn] ?? 'unmarked';
    if (m === 'present') present++;
    else if (m === 'absent') absent++;
    else unmarked++;
  });
  return { present, absent, unmarked, total: roster.length };
}

export interface CorrectionInput { sessionId: string; prn: string; to: Mark; reason: string }

interface AppValue {
  role: Role | null;
  signIn: (role: Role) => void;
  signOut: () => void;
  students: Student[];
  stats: Record<string, StudentStat>;
  slots: Slot[];
  sessions: LectureSession[];
  externalSessions: typeof EXTERNAL_SESSIONS;
  corrections: Correction[];
  audit: AuditEntry[];
  saveDraft: (id: string, data: { marks: Record<string, Mark>; mode: MarkMode; topic?: string }) => void;
  submitSession: (id: string, data: { marks: Record<string, Mark>; mode: MarkMode; topic?: string }) => 'reviewed' | 'incomplete';
  cancelSession: (id: string, reason: string) => void;
  syncPending: () => number;
  requestCorrection: (input: CorrectionInput) => Correction;
  decideCorrection: (id: string, approve: boolean, note: string) => void;
  setStudentStatus: (prn: string, status: StudentStatus, reason: string) => void;
  importStudents: (rows: Student[], fileName: string) => { added: number; skipped: number };
  addSlot: (slot: Omit<Slot, 'id'>, overrideReason?: string) => string;
  log: (action: string, entity: string, old: string, next: string) => void;
}

const Ctx = createContext<AppValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role | null>(readRole);
  const [students, setStudents] = useState<Student[]>(SEED_STUDENTS);
  const [slots, setSlots] = useState<Slot[]>(SEED_SLOTS);
  const [sessions, setSessions] = useState<LectureSession[]>(() => seedSessions(SEED_STUDENTS));
  const [corrections, setCorrections] = useState<Correction[]>(SEED_CORRECTIONS);
  const [audit, setAudit] = useState<AuditEntry[]>(SEED_AUDIT);

  const stats = useMemo(() => computeStats(students), [students]);

  const actor = role ? ROLE_USER[role].name : 'unknown';
  const actorRole: AuditRole = role ? AUDIT_ROLE[role] : 'Faculty';

  const log = useCallback(
    (action: string, entity: string, old: string, next: string) =>
      setAudit((prev) => [{ id: `aud-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, at: stamp(), actor, role: actorRole, action, entity, old, next }, ...prev]),
    [actor, actorRole],
  );

  const signIn = useCallback((r: Role) => {
    setRole(r);
    try { localStorage.setItem(ROLE_KEY, r); } catch { /* storage unavailable */ }
  }, []);
  const signOut = useCallback(() => {
    setRole(null);
    try { localStorage.removeItem(ROLE_KEY); } catch { /* storage unavailable */ }
  }, []);

  const patchSession = (id: string, patch: (s: LectureSession) => LectureSession) =>
    setSessions((prev) => prev.map((s) => (s.id === id ? patch(s) : s)));

  // PUT /api/v1/attendance/sessions/{id}/draft/  (or queued to /api/v1/sync/attendance/ when offline)
  const saveDraft: AppValue['saveDraft'] = (id, { marks, mode, topic }) => {
    const offline = typeof navigator !== 'undefined' && !navigator.onLine;
    const at = stamp();
    const s = sessions.find((x) => x.id === id);
    patchSession(id, (x) => ({ ...x, marks, mode, topic, record: 'draft', draftSavedAt: at, pendingSync: offline }));
    if (s) log(offline ? 'Draft saved (offline)' : 'Draft saved', sessionLabel(s), '—', `Draft · ${Object.values(marks).filter((m) => m !== 'unmarked').length} marked`);
  };

  // POST /api/v1/attendance/sessions/{id}/submit/
  const submitSession: AppValue['submitSession'] = (id, { marks, mode, topic }) => {
    const s = sessions.find((x) => x.id === id)!;
    const roster = students.filter((st) => st.classKey === s.classKey && st.status === 'Active' && (!s.batch || st.batch === s.batch));
    const unmarked = roster.filter((st) => (marks[st.prn] ?? 'unmarked') === 'unmarked').length;
    const record = unmarked > 0 ? 'incomplete' : 'reviewed';
    patchSession(id, (x) => ({ ...x, marks, mode, topic, record, status: 'conducted', pendingSync: false }));
    log('Attendance submitted', sessionLabel(s), recordLabel(s.record), record === 'incomplete' ? `Incomplete Records (${unmarked} unmarked)` : `Reviewed (${roster.length - unmarked} marked)`);
    return record;
  };

  // POST /api/v1/timetable/sessions/{id}/cancel/
  const cancelSession: AppValue['cancelSession'] = (id, reason) => {
    const s = sessions.find((x) => x.id === id)!;
    patchSession(id, (x) => ({ ...x, status: 'cancelled', cancelReason: reason }));
    log('Session cancelled', sessionLabel(s), 'Scheduled', `Cancelled — ${reason}`);
  };

  // POST /api/v1/sync/attendance/ (idempotent batch)
  const syncPending = () => {
    const n = sessions.filter((s) => s.pendingSync).length;
    if (n) {
      setSessions((prev) => prev.map((s) => (s.pendingSync ? { ...s, pendingSync: false } : s)));
      log('Offline drafts synced', `${n} session${n > 1 ? 's' : ''}`, 'Saved offline', 'Synced');
    }
    return n;
  };

  // POST /api/v1/corrections/
  const requestCorrection: AppValue['requestCorrection'] = ({ sessionId, prn, to, reason }) => {
    const s = sessions.find((x) => x.id === sessionId)!;
    const from = s.marks[prn] ?? 'unmarked';
    const withinWindow = hoursBetween(sessionStart(s.date, s.period), NOW) <= 24 && s.record !== 'finalized';
    const cor: Correction = {
      id: `cor-${Date.now()}`, prn, sessionId, facultyId: 'f-patil', from, to, reason,
      status: withinWindow ? 'auto' : 'pending', requestedAt: stamp(),
    };
    setCorrections((prev) => [cor, ...prev]);
    if (withinWindow) patchSession(sessionId, (x) => ({ ...x, marks: { ...x.marks, [prn]: to } }));
    log(withinWindow ? 'Correction auto-applied' : 'Correction requested', `${prn} · ${s.subject} · ${fmtDayMonth(s.date)} ${PERIODS[s.period].start}`,
      cap(from), withinWindow ? cap(to) : `${cap(to)} (pending HOD)`);
    return cor;
  };

  // POST /api/v1/corrections/{id}/approve/  |  /reject/
  const decideCorrection: AppValue['decideCorrection'] = (id, approve, note) => {
    const cor = corrections.find((c) => c.id === id)!;
    setCorrections((prev) => prev.map((c) => (c.id === id ? { ...c, status: approve ? 'approved' : 'rejected', decidedAt: stamp(), decisionNote: note } : c)));
    if (approve) patchSession(cor.sessionId, (x) => ({ ...x, marks: { ...x.marks, [cor.prn]: cor.to } }));
    const ses = sessions.find((x) => x.id === cor.sessionId) ?? EXTERNAL_SESSIONS.find((x) => x.id === cor.sessionId);
    const entity = ses ? `${cor.prn} · ${ses.subject} · ${fmtDayMonth(ses.date)} ${PERIODS[ses.period].start}` : cor.prn;
    log(approve ? 'Correction approved' : 'Correction rejected', entity, cap(cor.from), approve ? cap(cor.to) : `${cap(cor.from)} (unchanged)`);
  };

  // PATCH /api/v1/students/{prn}/status/
  const setStudentStatus: AppValue['setStudentStatus'] = (prn, status, reason) => {
    const st = students.find((s) => s.prn === prn)!;
    setStudents((prev) => prev.map((s) => (s.prn === prn ? { ...s, status } : s)));
    log('Status changed', `${prn} · ${st.name}`, st.status, `${status} — ${reason}`);
  };

  // POST /api/v1/students/import/
  const importStudents: AppValue['importStudents'] = (rows, fileName) => {
    const existing = new Set(students.map((s) => s.prn));
    const fresh = rows.filter((r) => !existing.has(r.prn));
    setStudents((prev) => [...prev, ...fresh].sort((a, b) => a.prn.localeCompare(b.prn)));
    const res = { added: fresh.length, skipped: rows.length - fresh.length };
    log('Students imported', fileName, '—', `${res.added} rows · ${res.skipped} skipped`);
    return res;
  };

  // POST /api/v1/timetable/slots/
  const addSlot: AppValue['addSlot'] = (slot, overrideReason) => {
    const id = `slot-${Date.now()}`;
    setSlots((prev) => [...prev, { ...slot, id }]);
    const day = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][slot.day];
    log(overrideReason ? 'Slot saved with override' : 'Slot saved',
      `${slot.subject} · ${CLASSES[slot.classKey].label} · ${day} ${PERIODS[slot.period].start}`,
      '—', overrideReason ? `Clash overridden — ${overrideReason}` : `${slot.room} · ${PEOPLE[slot.facultyId].name}`);
    return id;
  };

  const value: AppValue = {
    role, signIn, signOut, students, stats, slots, sessions, externalSessions: EXTERNAL_SESSIONS, corrections, audit,
    saveDraft, submitSession, cancelSession, syncPending, requestCorrection, decideCorrection,
    setStudentStatus, importStudents, addSlot, log,
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

const cap = (m: string) => m.charAt(0).toUpperCase() + m.slice(1);
const recordLabel = (r?: string) => (r ? cap(r) : 'Draft');

export function useApp() {
  const v = useContext(Ctx);
  if (!v) throw new Error('useApp must be used inside <AppProvider>');
  return v;
}

export const subjectName = (code: string) => SUBJECTS[code]?.name ?? code;
