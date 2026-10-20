import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, CloudOff, MapPin, MoreVertical } from 'lucide-react';
import type { LectureSession } from '../../types';
import { CLASSES, COLLEGE, NOW, PERIODS, ROLE_USER, TODAY } from '../../data/catalog';
import { rosterFor } from '../../data/sessions';
import { markCounts, subjectName, useApp } from '../../store/AppStore';
import { AccountMenu, NotificationBell, Page } from '../../components/Shell';
import { AmsMark, Banner, Button, ButtonLink, Card, Dialog, Field, Pill, SessionPill, Textarea } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { cn, fmtLongDate } from '../../lib/format';

export default function Today() {
  const { sessions, syncPending } = useApp();
  const toast = useToast();
  const [syncing, setSyncing] = useState(false);
  const me = ROLE_USER.faculty;

  const today = sessions.filter((s) => s.date === TODAY && s.facultyId === me.id).sort((a, b) => a.period - b.period);
  const cancelled = today.filter((s) => s.status === 'cancelled').length;
  const incomplete = sessions.filter((s) => s.facultyId === me.id && s.record === 'incomplete').length;
  const pendingSync = sessions.filter((s) => s.pendingSync).length;
  const hour = NOW.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const retry = () => {
    setSyncing(true);
    setTimeout(() => {
      const n = syncPending();
      setSyncing(false);
      toast(`${n} session${n === 1 ? '' : 's'} synced to the server.`);
    }, 900);
  };

  return (
    <>
      {/* Phone app bar */}
      <div className="flex items-center gap-3 bg-navy px-4 py-3 text-white md:hidden">
        <AmsMark />
        <div className="min-w-0 flex-1">
          <div className="text-[15px] font-semibold leading-5">{COLLEGE.short}</div>
          <div className="truncate text-[13px] text-white/75">Faculty · {COLLEGE.departmentShort}</div>
        </div>
        <NotificationBell role="faculty" dark />
        <AccountMenu role="faculty" compact dark />
      </div>

      <Page className="!max-w-[1000px] !px-4 !pt-5 sm:!px-8">
        <div className="text-[13px] font-medium text-ink-500">{fmtLongDate(TODAY)}</div>
        <h1 className="mt-1 text-2xl font-bold tracking-tight text-ink-900 sm:text-[28px]">{greeting}, {me.name}</h1>
        <p className="mt-1 text-[15px] text-ink-700">
          {today.length - cancelled} lectures today{cancelled > 0 && ` · ${cancelled} cancelled`}
        </p>

        <div className="mt-5 space-y-2.5">
          {incomplete > 0 && (
            <Banner tone="amber" icon={<AlertTriangle className="h-5 w-5" />}
              action={<Link to="/faculty/history?filter=incomplete" className="font-semibold underline underline-offset-2">Review</Link>}>
              <span className="font-semibold">{incomplete} sessions have incomplete records</span>
              <span className="hidden sm:inline">. Mark the remaining students.</span>
            </Banner>
          )}
          {pendingSync > 0 && (
            <Banner tone="amber" icon={<CloudOff className="h-5 w-5" />}
              action={<Button size="sm" onClick={retry} disabled={syncing}>{syncing ? 'Syncing…' : 'Retry'}</Button>}>
              <span className="font-semibold">Offline</span> — {pendingSync} session{pendingSync > 1 ? 's' : ''} waiting to sync
            </Banner>
          )}
        </div>

        <h2 className="mb-3 mt-7 text-lg font-semibold text-ink-900">Today's lectures</h2>
        <div className="grid gap-3 lg:grid-cols-2">
          {today.map((s) => <LectureCard key={s.id} session={s} />)}
        </div>
      </Page>
    </>
  );
}

function LectureCard({ session: s }: { session: LectureSession }) {
  const { students, cancelSession } = useApp();
  const toast = useToast();
  const [menu, setMenu] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const roster = rosterFor(students, s.classKey, s.batch);
  const c = markCounts(s, roster);
  const cancelled = s.status === 'cancelled';
  const hasDraft = s.record === 'draft' && s.status === 'scheduled';

  const confirmCancel = () => {
    if (reason.trim().length < 5) { setError('Enter a reason — it is saved to the audit log.'); return; }
    cancelSession(s.id, reason.trim());
    setCancelOpen(false);
    toast(`${subjectName(s.subject)} cancelled. Students and the HOD will see the reason.`);
  };

  return (
    <Card className={cn('p-4', cancelled && 'border-dashed bg-white/60')}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-[15px] font-bold tabular-nums text-ink-900">{PERIODS[s.period].start} – {s.type === 'lab' ? PERIODS[s.period + 1].end : PERIODS[s.period].end}</span>
        <div className="flex items-center gap-1">
          <SessionPill status={s.status} />
          {s.status === 'scheduled' && (
            <div className="relative">
              <button type="button" onClick={() => setMenu((m) => !m)} className="rounded p-1.5 text-ink-500 hover:bg-mute-fill" aria-label="More actions">
                <MoreVertical className="h-4 w-4" />
              </button>
              {menu && (
                <div className="absolute right-0 z-20 mt-1 w-48 rounded-md border border-line bg-white py-1 shadow-overlay" onMouseLeave={() => setMenu(false)}>
                  <button type="button" className="block w-full px-4 py-2.5 text-left text-sm text-bad-text hover:bg-bad-fill" onClick={() => { setMenu(false); setCancelOpen(true); }}>
                    Cancel session…
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <div className={cn('mt-2 text-[17px] font-semibold text-ink-900', cancelled && 'text-ink-500 line-through')}>
        {subjectName(s.subject)} <span className="font-normal text-ink-500">· {s.subject}</span>
      </div>
      <div className="mt-0.5 text-sm text-ink-700">{CLASSES[s.classKey].label}{s.batch && ` · Batch ${s.batch}`}</div>
      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-ink-700">
        <span className={cn('rounded border px-2 py-0.5 text-[13px] font-medium', s.type === 'lab' ? 'border-navy bg-navy text-white' : 'border-line')}>
          {s.type === 'lab' ? 'Lab · 2 h' : 'Theory'}
        </span>
        <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{s.room}</span>
        {s.status === 'conducted' && <span className="tabular-nums">{c.present} / {c.total} present</span>}
        {hasDraft && <span>Draft · <span className="font-medium text-warn-text">{c.unmarked} unmarked</span></span>}
        {s.pendingSync && <Pill tone="amber">Saved offline</Pill>}
      </div>
      {cancelled ? (
        <p className="mt-3 text-[13px] text-ink-500">{s.cancelReason}</p>
      ) : (
        <ButtonLink
          to={`/faculty/session/${s.id}`}
          variant={s.status === 'conducted' ? 'secondary' : 'primary'}
          size="lg"
          block
          className="mt-4"
        >
          {s.status === 'conducted' ? 'View' : hasDraft ? 'Continue draft' : 'Take attendance'}
        </ButtonLink>
      )}

      <Dialog
        open={cancelOpen}
        onClose={() => setCancelOpen(false)}
        title="Cancel this session?"
        footer={<>
          <Button onClick={() => setCancelOpen(false)}>Keep session</Button>
          <Button variant="danger" onClick={confirmCancel}>Cancel session</Button>
        </>}
      >
        <p className="text-sm text-ink-700">
          {subjectName(s.subject)} · {CLASSES[s.classKey].label} · {PERIODS[s.period].start}. Cancelled sessions are excluded from attendance percentages. Nothing is deleted.
        </p>
        <Field label="Reason" required error={error} className="mt-4">
          {(id) => <Textarea id={id} value={reason} invalid={!!error} onChange={(e) => { setReason(e.target.value); setError(''); }} placeholder="e.g. Official duty — DBATU paper-setting meeting" />}
        </Field>
      </Dialog>
    </Card>
  );
}
