import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ArrowRight, Plus } from 'lucide-react';
import type { Correction, CorrectionStatus, Mark } from '../../types';
import { CLASSES, COLLEGE, NOW, PERIODS, ROLE_USER } from '../../data/catalog';
import { rosterFor } from '../../data/sessions';
import { subjectName, useApp } from '../../store/AppStore';
import { MobileHero, Page } from '../../components/Shell';
import { Banner, Button, Card, CorrectionPill, Dialog, Empty, Field, MarkPill, PageHeader, Select, Textarea } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { cn, fmtDayShort, fmtDayTime, hoursBetween, parseDate, prn4, sessionStart } from '../../lib/format';

type Filter = 'all' | CorrectionStatus;
const FILTERS: { value: Filter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'auto', label: 'Auto-applied' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
];

export default function Corrections() {
  const { corrections, sessions } = useApp();
  const [params, setParams] = useSearchParams();
  const [filter, setFilter] = useState<Filter>('all');
  const newFor = params.get('new');
  const [open, setOpen] = useState(!!newFor);

  const mine = corrections
    .filter((c) => c.facultyId === ROLE_USER.faculty.id)
    .sort((a, b) => b.requestedAt.localeCompare(a.requestedAt));
  const list = mine.filter((c) => filter === 'all' || c.status === filter);

  const closeDialog = () => {
    setOpen(false);
    if (newFor) setParams({}, { replace: true });
  };

  const tabs = (dark: boolean) => (
    <div className="no-scrollbar -mx-4 overflow-x-auto px-4 md:mx-0 md:px-0">
      <div className="flex w-max gap-1.5">
        {FILTERS.map((f) => {
          const n = f.value === 'all' ? mine.length : mine.filter((c) => c.status === f.value).length;
          const on = filter === f.value;
          return (
            <button key={f.value} type="button" onClick={() => setFilter(f.value)}
              className={cn('h-9 shrink-0 rounded-md border px-3 text-[13px] font-semibold',
                dark ? (on ? 'border-white bg-white text-navy' : 'border-white/30 text-white hover:bg-white/10')
                  : (on ? 'border-navy bg-navy text-white' : 'border-line bg-white text-ink-700 hover:bg-surface'))}>
              {f.label} <span className="font-normal opacity-75">{n}</span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      <MobileHero
        title="My corrections"
        subtitle="Requested from History · newest first"
        action={<Button size="sm" className="!border-white/40 !bg-transparent !text-white hover:!bg-white/10" onClick={() => setOpen(true)}>New</Button>}
      >
        {tabs(true)}
      </MobileHero>
      <Page className="!pt-4 md:!pt-8">
        <PageHeader
          className="hidden md:flex"
          title="My corrections"
          subtitle="Within 24 h of a lecture, corrections apply instantly. Later ones, or locked sessions, go to the HOD."
          actions={<Button variant="primary" onClick={() => setOpen(true)}><Plus className="h-4 w-4" />New correction</Button>}
        />
        <div className="mb-4 hidden md:block">{tabs(false)}</div>
        <div className="grid gap-3 lg:grid-cols-2">
          {list.map((c) => <CorrectionCard key={c.id} c={c} sessions={sessions} />)}
        </div>
        {list.length === 0 && <Card><Empty>No corrections here.</Empty></Card>}
      </Page>
      <NewCorrection open={open} onClose={closeDialog} initialSession={newFor} />
    </>
  );
}

function CorrectionCard({ c, sessions }: { c: Correction; sessions: ReturnType<typeof useApp>['sessions'] }) {
  const { students } = useApp();
  const s = sessions.find((x) => x.id === c.sessionId);
  const st = students.find((x) => x.prn === c.prn);
  const afterHours = s ? Math.round(hoursBetween(sessionStart(s.date, s.period), parseDate(c.requestedAt))) : 0;
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="text-[17px] font-semibold text-ink-900"><span className="tabular-nums">{prn4(c.prn)}</span> — {st?.name}</div>
        <CorrectionPill status={c.status} />
      </div>
      {s && (
        <div className="mt-1 text-sm text-ink-700">
          {subjectName(s.subject)} · {fmtDayShort(s.date)}, {PERIODS[s.period].start} · {CLASSES[s.classKey].label}{s.batch && ` · ${s.batch}`}
        </div>
      )}
      <div className="mt-3 flex items-center gap-2">
        <MarkPill mark={c.from} size="md" /><ArrowRight className="h-4 w-4 text-ink-500" /><MarkPill mark={c.to} size="md" />
      </div>
      <p className="mt-3 text-sm text-ink-700"><span className="font-semibold text-ink-900">Reason</span> · {c.reason}</p>
      <p className="mt-2 text-[13px] text-ink-500">
        {c.status === 'auto' && `Applied ${fmtDayTime(c.requestedAt)} · within 24 h · logged`}
        {c.status === 'pending' && `Requested ${fmtDayTime(c.requestedAt)} · ${afterHours} h after lecture · waiting for HOD`}
        {c.status === 'approved' && `Approved by HOD ${fmtDayTime(c.decidedAt!)}${c.decisionNote ? ` · ${c.decisionNote}` : ''}`}
        {c.status === 'rejected' && <span className="text-bad-text">Rejected by HOD {fmtDayTime(c.decidedAt!)}{c.decisionNote ? ` · ${c.decisionNote}` : ''}</span>}
      </p>
    </Card>
  );
}

function NewCorrection({ open, onClose, initialSession }: { open: boolean; onClose: () => void; initialSession: string | null }) {
  const { sessions, students, requestCorrection } = useApp();
  const toast = useToast();
  const eligible = sessions
    .filter((s) => s.facultyId === ROLE_USER.faculty.id && s.record && s.record !== 'draft')
    .sort((a, b) => b.date.localeCompare(a.date) || b.period - a.period);
  const [sessionId, setSessionId] = useState(initialSession && eligible.some((s) => s.id === initialSession) ? initialSession : eligible[0]?.id ?? '');
  const session = eligible.find((s) => s.id === sessionId);
  const roster = useMemo(() => (session ? rosterFor(students, session.classKey, session.batch) : []), [session, students]);
  const [prn, setPrn] = useState('');
  const [to, setTo] = useState<Mark>('present');
  const [reason, setReason] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const current: Mark = session && prn ? session.marks[prn] ?? 'unmarked' : 'unmarked';
  const hours = session ? hoursBetween(sessionStart(session.date, session.period), NOW) : 0;
  const instant = session && hours <= 24 && session.record !== 'finalized';

  const submit = () => {
    const e: Record<string, string> = {};
    if (!prn) e.prn = 'Choose a student.';
    else if (current === to) e.to = `Already marked ${to === 'present' ? 'Present' : 'Absent'}.`;
    if (reason.trim().length < 10) e.reason = 'Enter a reason — it is saved to the audit log.';
    setErrors(e);
    if (Object.keys(e).length || !session) return;
    const cor = requestCorrection({ sessionId: session.id, prn, to, reason: reason.trim() });
    toast(cor.status === 'auto' ? 'Correction applied and logged.' : 'Sent to the HOD for approval.');
    setPrn(''); setReason(''); setErrors({});
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="New correction"
      footer={<><Button onClick={onClose}>Cancel</Button><Button variant="primary" onClick={submit}>{instant ? 'Apply correction' : 'Send to HOD'}</Button></>}
    >
      <div className="space-y-4">
        <Field label="Session">
          {(id) => (
            <Select id={id} value={sessionId} onChange={(e) => { setSessionId(e.target.value); setPrn(''); }}>
              {eligible.map((s) => (
                <option key={s.id} value={s.id}>
                  {fmtDayShort(s.date)} {PERIODS[s.period].start} · {subjectName(s.subject)} · {CLASSES[s.classKey].short}{s.batch ? ` ${s.batch}` : ''}
                </option>
              ))}
            </Select>
          )}
        </Field>
        <Field label="Student" error={errors.prn}>
          {(id) => (
            <Select id={id} value={prn} onChange={(e) => {
              setPrn(e.target.value);
              const m = session?.marks[e.target.value] ?? 'unmarked';
              setTo(m === 'present' ? 'absent' : 'present');
              setErrors({});
            }}>
              <option value="">Choose a student…</option>
              {roster.map((s) => {
                const m = session?.marks[s.prn] ?? 'unmarked';
                return <option key={s.prn} value={s.prn}>{prn4(s.prn)} — {s.name} · {m === 'present' ? 'Present' : m === 'absent' ? 'Absent' : 'Unmarked'}</option>;
              })}
            </Select>
          )}
        </Field>
        <div>
          <div className="mb-1.5 text-sm font-medium text-ink-900">Change</div>
          <div className="flex items-center gap-3">
            <MarkPill mark={current} size="md" />
            <ArrowRight className="h-4 w-4 text-ink-500" />
            <div className="grid flex-1 grid-cols-2 gap-1 rounded-md bg-mute-fill p-1">
              {(['present', 'absent'] as Mark[]).map((m) => (
                <button key={m} type="button" onClick={() => setTo(m)}
                  className={cn('h-9 rounded text-sm font-semibold', to === m ? (m === 'present' ? 'bg-ok-fill text-ok-text ring-1 ring-[#CBE7D3]' : 'bg-bad-fill text-bad-text ring-1 ring-[#F5C6C6]') : 'text-ink-700')}>
                  {m === 'present' ? 'Present' : 'Absent'}
                </button>
              ))}
            </div>
          </div>
          {errors.to && <p className="mt-1.5 text-[13px] text-bad-text">{errors.to}</p>}
        </div>
        <Field label="Reason" required error={errors.reason}>
          {(id) => <Textarea id={id} value={reason} invalid={!!errors.reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. On NSS duty; OD letter submitted to the department office." />}
        </Field>
        {session && (
          <Banner tone={instant ? 'green' : 'amber'}>
            {instant
              ? 'Within 24 h of the lecture — applies instantly and appears in the audit log.'
              : session.record === 'finalized'
                ? 'This session is finalized (locked) — the HOD must approve the change.'
                : `${Math.round(hours)} h after the lecture — the HOD must approve the change.`}
          </Banner>
        )}
        <p className="text-[13px] text-ink-500">Corrections never delete the original mark. {COLLEGE.short} keeps both in the audit trail.</p>
      </div>
    </Dialog>
  );
}
