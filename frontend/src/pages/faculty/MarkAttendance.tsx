import { useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Check, ChevronLeft, CloudOff, Loader, Lock, X } from 'lucide-react';
import type { Mark, MarkMode } from '../../types';
import { CLASSES, PERIODS } from '../../data/catalog';
import { rosterFor } from '../../data/sessions';
import { subjectName, useApp } from '../../store/AppStore';
import { Banner, Button, ButtonLink, Card, Chips, Dialog, Empty, Pill, RecordPill, SearchInput } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { cn, fmtDayShort, fmtTime, prn4 } from '../../lib/format';

type Filter = 'all' | 'unmarked' | 'absent' | 'present';

export default function MarkAttendance() {
  const { id } = useParams();
  const { sessions, students, saveDraft, submitSession } = useApp();
  const session = sessions.find((s) => s.id === id);
  const navigate = useNavigate();
  const toast = useToast();

  const roster = useMemo(() => (session ? rosterFor(students, session.classKey, session.batch) : []), [session, students]);
  const [marks, setMarks] = useState<Record<string, Mark>>(() => ({ ...(session?.marks ?? {}) }));
  const [undo, setUndo] = useState<Record<string, Mark>>({});
  const [mode, setMode] = useState<MarkMode>(session?.mode ?? 'mode1');
  const [topic, setTopic] = useState(session?.topic ?? '');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<Filter>('all');
  const [confirmOpen, setConfirmOpen] = useState(false);

  if (!session) {
    return <div className="p-8"><Empty>Session not found. <Link className="text-accent underline" to="/faculty">Back to today</Link></Empty></div>;
  }

  const readOnly = session.record === 'reviewed' || session.record === 'finalized' || session.status === 'cancelled';
  const markOf = (prn: string): Mark => marks[prn] ?? 'unmarked';
  const counts = roster.reduce((acc, s) => { acc[markOf(s.prn)]++; return acc; }, { present: 0, absent: 0, unmarked: 0 } as Record<Mark, number>);
  const target: Mark = mode === 'mode1' ? 'absent' : 'present';
  const baseline: Mark = mode === 'mode1' ? 'present' : 'absent';

  const tap = (prn: string) => {
    if (readOnly) return;
    const cur = markOf(prn);
    if (cur === target) {
      const prev = undo[prn] ?? baseline;
      setMarks((m) => ({ ...m, [prn]: prev }));
      setUndo((u) => { const n = { ...u }; delete n[prn]; return n; });
    } else {
      setUndo((u) => ({ ...u, [prn]: cur }));
      setMarks((m) => ({ ...m, [prn]: target }));
    }
  };

  const markRemaining = () => {
    setMarks((m) => {
      const next = { ...m };
      roster.forEach((s) => { if ((next[s.prn] ?? 'unmarked') === 'unmarked') next[s.prn] = baseline; });
      return next;
    });
    toast(`${counts.unmarked} students marked ${baseline === 'present' ? 'Present' : 'Absent'}.`);
  };

  const q = query.trim().toLowerCase();
  const visible = roster.filter((s) =>
    (filter === 'all' || markOf(s.prn) === filter) &&
    (!q || s.name.toLowerCase().includes(q) || prn4(s.prn).includes(q)));

  const doSave = () => {
    saveDraft(session.id, { marks, mode, topic });
    toast(navigator.onLine ? 'Draft saved and synced.' : 'Draft saved on this phone. It will sync when you are back online.', navigator.onLine ? 'success' : 'warning');
  };
  const doSubmit = () => {
    const result = submitSession(session.id, { marks, mode, topic });
    setConfirmOpen(false);
    toast(result === 'incomplete'
      ? `Submitted with ${counts.unmarked} unmarked — flagged as Incomplete Records.`
      : 'Attendance submitted.', result === 'incomplete' ? 'warning' : 'success');
    navigate('/faculty');
  };

  const time = `${PERIODS[session.period].start}–${session.type === 'lab' ? PERIODS[session.period + 1].end : PERIODS[session.period].end}`;
  const syncPill = session.pendingSync
    ? <Pill tone="amber" icon={<CloudOff className="h-3.5 w-3.5" />} size="md">Saved offline</Pill>
    : session.draftSavedAt ? <Pill tone="green" size="md">Synced</Pill> : null;

  return (
    <div className="flex min-h-[calc(100vh-2.25rem)] flex-col md:min-h-0">
      {/* Session header */}
      <div className="bg-navy px-3 py-3 text-white md:mx-auto md:mt-8 md:w-full md:max-w-3xl md:rounded-t-lg md:px-5">
        <div className="flex items-start gap-2">
          <Link to="/faculty" className="-ml-1 rounded p-1 hover:bg-white/10" aria-label="Back"><ChevronLeft className="h-6 w-6" /></Link>
          <div className="min-w-0 flex-1">
            <h1 className="text-lg font-bold leading-6">{subjectName(session.subject)}</h1>
            <div className="text-[13px] text-white/80">{session.subject} · {session.type === 'lab' ? 'Lab' : 'Theory'}</div>
            <div className="mt-1 text-[13px] text-white/90">
              {CLASSES[session.classKey].label}{session.batch && ` · ${session.batch}`} · {fmtDayShort(session.date)} · {time} · {session.room}
            </div>
          </div>
          {syncPill}
        </div>
      </div>

      <div className="flex-1 bg-surface md:mx-auto md:w-full md:max-w-3xl md:border-x md:border-line md:bg-white">
        <div className="space-y-3 px-3 pt-3 md:px-5 md:pt-5">
          {readOnly ? (
            <Banner tone="info" icon={<Lock className="h-4 w-4" />}
              action={session.status !== 'cancelled' && <ButtonLink size="sm" to={`/faculty/corrections?new=${session.id}`}>Request correction</ButtonLink>}>
              <span className="mr-2"><RecordPill state={session.record!} /></span>
              Submitted attendance can only change through a correction request.
            </Banner>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-1 rounded-lg bg-mute-fill p-1" role="radiogroup" aria-label="Marking mode">
                {([['mode1', 'Mode 1: All present', 'Tap absentees'], ['mode2', 'Mode 2: All absent', "Tap who's present"]] as const).map(([m, t, sub]) => (
                  <button
                    key={m}
                    type="button"
                    role="radio"
                    aria-checked={mode === m}
                    onClick={() => { setMode(m); setUndo({}); }}
                    className={cn('rounded-md px-2 py-2 text-center', mode === m ? 'border border-line bg-white shadow-sm' : 'text-ink-700')}
                  >
                    <div className="text-sm font-semibold text-ink-900">{t}</div>
                    <div className="text-[13px] text-ink-500">{sub}</div>
                  </button>
                ))}
              </div>
              <Button block size="lg" className="text-navy" onClick={markRemaining} disabled={counts.unmarked === 0}>
                {counts.unmarked === 0 ? 'Everyone is marked' : `Mark the ${counts.unmarked} unmarked as ${baseline === 'present' ? 'Present' : 'Absent'}`}
              </Button>
              <p className="text-[13px] text-ink-500">
                {session.draftSavedAt ? `Draft saved ${fmtTime(session.draftSavedAt)} on this phone. ` : ''}Unmarked students are never guessed.
              </p>
            </>
          )}

          <SearchInput value={query} onChange={setQuery} placeholder="Name or last 4 digits" />
          <Chips<Filter>
            value={filter}
            onChange={setFilter}
            options={[
              { value: 'all', label: `All ${roster.length}` },
              { value: 'unmarked', label: `Unmarked ${counts.unmarked}` },
              { value: 'absent', label: `Absent ${counts.absent}` },
              { value: 'present', label: `Present ${counts.present}` },
            ]}
          />
          {!readOnly && (
            <p className="text-[13px] text-ink-500">Tap a row to mark it {target === 'present' ? 'Present' : 'Absent'} · tap again to undo</p>
          )}
        </div>

        <ul className="space-y-2 px-3 pb-4 pt-2 md:px-5">
          {visible.map((s) => {
            const m = markOf(s.prn);
            return (
              <li key={s.prn}>
                <button
                  type="button"
                  onClick={() => tap(s.prn)}
                  disabled={readOnly}
                  aria-pressed={m === target}
                  className={cn('flex min-h-[60px] w-full items-center justify-between gap-3 rounded-md border px-4 text-left transition-colors',
                    m === 'present' && 'border-[#CBE7D3] bg-ok-fill',
                    m === 'absent' && 'border-[#F5C6C6] bg-bad-fill',
                    m === 'unmarked' && 'border-dashed border-ink-400 bg-white',
                    readOnly && 'cursor-default')}
                >
                  <span className="text-[15px] text-ink-900"><span className="font-bold tabular-nums">{prn4(s.prn)}</span> — {s.name}</span>
                  <span className={cn('inline-flex shrink-0 items-center gap-1 text-[13px] font-semibold',
                    m === 'present' ? 'text-ok-text' : m === 'absent' ? 'text-bad-text' : 'text-ink-500')}>
                    {m === 'present' && <Check className="h-4 w-4" />}
                    {m === 'absent' && <X className="h-4 w-4" />}
                    {m === 'present' ? 'Present' : m === 'absent' ? 'Absent' : 'Unmarked'}
                  </span>
                </button>
              </li>
            );
          })}
          {visible.length === 0 && <Card><Empty>No students match.</Empty></Card>}
        </ul>
      </div>

      {/* Action bar */}
      <div className="sticky bottom-0 z-20 border-t border-line bg-white px-3 pb-[max(12px,env(safe-area-inset-bottom))] pt-3 shadow-[0_-2px_8px_rgba(15,23,42,.06)] md:mx-auto md:mb-8 md:w-full md:max-w-3xl md:rounded-b-lg md:border-x md:px-5">
        <div className="flex items-center justify-center gap-3 text-sm font-semibold tabular-nums">
          <span className="inline-flex items-center gap-1.5 text-ok-text"><span className="h-2 w-2 rounded-full bg-ok-dot" />Present {counts.present}</span>
          <span className="text-ink-400">·</span>
          <span className="inline-flex items-center gap-1.5 text-bad-text"><span className="h-2 w-2 rounded-full bg-bad-dot" />Absent {counts.absent}</span>
          <span className="text-ink-400">·</span>
          <span className="inline-flex items-center gap-1.5 text-ink-700"><Loader className="h-3.5 w-3.5" />Unmarked {counts.unmarked}</span>
        </div>
        {!readOnly && (
          <>
            <label className="mt-3 flex items-center gap-3">
              <span className="shrink-0 text-sm font-medium text-ink-900">Topic covered</span>
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Optional — e.g. SVM kernels"
                className="h-11 w-full rounded-md border border-line px-3 text-[15px] placeholder:text-ink-400 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
              />
            </label>
            <div className="mt-3 grid grid-cols-[1fr_1.4fr] gap-2">
              <Button size="lg" onClick={doSave}>Save draft</Button>
              <Button size="lg" variant="primary" onClick={() => (counts.unmarked > 0 ? setConfirmOpen(true) : doSubmit())}>Submit</Button>
            </div>
          </>
        )}
        {readOnly && topic && <p className="mt-2 text-center text-[13px] text-ink-500">Topic: {topic}</p>}
      </div>

      <Dialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        title={`${counts.unmarked} students are still unmarked`}
        footer={<>
          <Button onClick={() => setConfirmOpen(false)}>Keep marking</Button>
          <Button variant="primary" onClick={doSubmit}>Submit anyway</Button>
        </>}
      >
        <p className="text-sm text-ink-700">
          The session will be saved as <Pill tone="amber">Incomplete Records</Pill>. Unmarked students are never guessed as present or absent — you can mark them later from History.
        </p>
      </Dialog>
    </div>
  );
}
