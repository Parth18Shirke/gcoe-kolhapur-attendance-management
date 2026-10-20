import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import type { Correction } from '../../types';
import { CLASSES, PEOPLE, PERIODS } from '../../data/catalog';
import { subjectName, useApp } from '../../store/AppStore';
import { Page } from '../../components/Shell';
import { Button, Card, Dialog, Empty, Field, MarkPill, PageHeader, Tabs, Textarea } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { fmtDayShort, fmtDayTime, hoursBetween, parseDate, sessionStart } from '../../lib/format';

type Tab = 'pending' | 'approved' | 'rejected';

function useSessionInfo() {
  const { sessions, externalSessions } = useApp();
  return (c: Correction) => sessions.find((s) => s.id === c.sessionId) ?? externalSessions.find((s) => s.id === c.sessionId);
}

export default function Approvals() {
  const { corrections, students } = useApp();
  const [tab, setTab] = useState<Tab>('pending');
  const [reviewing, setReviewing] = useState<Correction | null>(null);
  const info = useSessionInfo();

  const list = corrections
    .filter((c) => c.status === tab)
    .sort((a, b) => (tab === 'pending' ? b.requestedAt.localeCompare(a.requestedAt) : (b.decidedAt ?? '').localeCompare(a.decidedAt ?? '')));
  const count = (t: Tab) => corrections.filter((c) => c.status === t).length;
  const student = (prn: string) => students.find((s) => s.prn === prn);

  return (
    <Page>
      <PageHeader
        title="Correction approvals"
        subtitle="Corrections made more than 24 h after a lecture, or on locked sessions, wait here. Corrections inside 24 h apply instantly and appear in the audit log."
      />
      <Card>
        <Tabs<Tab>
          value={tab}
          onChange={setTab}
          options={[
            { value: 'pending', label: 'Pending', count: count('pending'), tone: 'amber' },
            { value: 'approved', label: 'Approved', count: count('approved'), tone: 'green' },
            { value: 'rejected', label: 'Rejected', count: count('rejected'), tone: 'red' },
          ]}
        />

        {/* Desktop table */}
        <div className="hidden overflow-x-auto lg:block">
          <table className="w-full text-left text-[15px]">
            <thead className="bg-surface text-xs font-semibold uppercase tracking-wide text-ink-500">
              <tr>
                <th className="px-4 py-3">Faculty</th><th className="px-4 py-3">Student</th><th className="px-4 py-3">Session</th>
                <th className="px-4 py-3">Change</th><th className="px-4 py-3">Reason</th>
                <th className="px-4 py-3">{tab === 'pending' ? 'Requested' : 'Decided'}</th><th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {list.map((c) => {
                const s = info(c);
                const st = student(c.prn);
                return (
                  <tr key={c.id} className="align-middle">
                    <td className="px-4 py-4 text-ink-700">{PEOPLE[c.facultyId].name}</td>
                    <td className="px-4 py-4">
                      <div className="font-semibold text-ink-900">{st?.name}</div>
                      <div className="text-[13px] tabular-nums text-ink-500">{c.prn}</div>
                    </td>
                    <td className="px-4 py-4">
                      {s && <>
                        <div className="text-ink-900">{subjectName(s.subject)} ({s.subject})</div>
                        <div className="text-[13px] text-ink-500">{fmtDayShort(s.date)}, {PERIODS[s.period].start}</div>
                      </>}
                    </td>
                    <td className="px-4 py-4"><div className="flex items-center gap-1.5"><MarkPill mark={c.from} /><ArrowRight className="h-3.5 w-3.5 text-ink-500" /><MarkPill mark={c.to} /></div></td>
                    <td className="max-w-[260px] px-4 py-4 text-sm text-ink-700"><p className="line-clamp-3">{c.reason}</p></td>
                    <td className="whitespace-nowrap px-4 py-4 text-ink-700">
                      {tab === 'pending' ? fmtDayTime(c.requestedAt) : <>
                        {fmtDayTime(c.decidedAt!)}
                        {c.decisionNote && <div className="max-w-[200px] whitespace-normal text-[13px] text-ink-500">{c.decisionNote}</div>}
                      </>}
                    </td>
                    <td className="px-4 py-4 text-right">{tab === 'pending' && <Button onClick={() => setReviewing(c)}>Review</Button>}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Phone / tablet cards */}
        <ul className="divide-y divide-line lg:hidden">
          {list.map((c) => {
            const s = info(c);
            return (
              <li key={c.id} className="space-y-2 px-4 py-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-ink-900">{student(c.prn)?.name}</div>
                    <div className="text-[13px] text-ink-500">{c.prn} · {PEOPLE[c.facultyId].name}</div>
                  </div>
                  {tab === 'pending' && <Button size="sm" onClick={() => setReviewing(c)}>Review</Button>}
                </div>
                {s && <div className="text-sm text-ink-700">{subjectName(s.subject)} ({s.subject}) · {fmtDayShort(s.date)}, {PERIODS[s.period].start}</div>}
                <div className="flex items-center gap-1.5"><MarkPill mark={c.from} /><ArrowRight className="h-3.5 w-3.5 text-ink-500" /><MarkPill mark={c.to} /></div>
                <p className="text-sm text-ink-700">{c.reason}</p>
                <p className="text-[13px] text-ink-500">{tab === 'pending' ? `Requested ${fmtDayTime(c.requestedAt)}` : `Decided ${fmtDayTime(c.decidedAt!)}${c.decisionNote ? ` · ${c.decisionNote}` : ''}`}</p>
              </li>
            );
          })}
        </ul>
        {list.length === 0 && <Empty>{tab === 'pending' ? 'Nothing waiting. All corrections are reviewed.' : `No ${tab} corrections.`}</Empty>}
      </Card>

      {reviewing && <ReviewDialog correction={reviewing} onClose={() => setReviewing(null)} />}
    </Page>
  );
}

function ReviewDialog({ correction: c, onClose }: { correction: Correction; onClose: () => void }) {
  const { students, decideCorrection } = useApp();
  const toast = useToast();
  const info = useSessionInfo();
  const s = info(c);
  const st = students.find((x) => x.prn === c.prn);
  const [note, setNote] = useState('');
  const [error, setError] = useState('');
  const lateBy = s ? Math.round(hoursBetween(sessionStart(s.date, s.period), parseDate(c.requestedAt))) : null;

  const decide = (approve: boolean) => {
    if (!approve && note.trim().length < 5) { setError('A reason is required to reject — it is sent to the faculty and logged.'); return; }
    decideCorrection(c.id, approve, note.trim());
    toast(approve ? `Approved — ${st?.name} is now ${c.to === 'present' ? 'Present' : 'Absent'}.` : 'Correction rejected. The original mark stays.');
    onClose();
  };

  return (
    <Dialog
      open
      onClose={onClose}
      title="Review correction"
      footer={<>
        <Button variant="danger" onClick={() => decide(false)}>Reject</Button>
        <Button variant="primary" onClick={() => decide(true)}>Approve</Button>
      </>}
    >
      <dl className="grid grid-cols-[110px_1fr] gap-x-4 gap-y-2.5 text-sm">
        <dt className="text-ink-500">Student</dt><dd className="text-ink-900"><span className="font-semibold">{st?.name}</span> · {c.prn}</dd>
        <dt className="text-ink-500">Session</dt>
        <dd className="text-ink-900">{s ? `${subjectName(s.subject)} (${s.subject}) · ${CLASSES[s.classKey].label} · ${fmtDayShort(s.date)}, ${PERIODS[s.period].start}` : '—'}</dd>
        <dt className="text-ink-500">Faculty</dt><dd className="text-ink-900">{PEOPLE[c.facultyId].name}</dd>
        <dt className="text-ink-500">Change</dt><dd className="flex items-center gap-1.5"><MarkPill mark={c.from} /><ArrowRight className="h-3.5 w-3.5 text-ink-500" /><MarkPill mark={c.to} /></dd>
        <dt className="text-ink-500">Requested</dt><dd className="text-ink-900">{fmtDayTime(c.requestedAt)}{lateBy !== null && <span className="text-ink-500"> · {lateBy} h after the lecture</span>}</dd>
        <dt className="text-ink-500">Reason</dt><dd className="text-ink-900">{c.reason}</dd>
      </dl>
      <Field label="Note to faculty" hint="Optional when approving. Required to reject." error={error} className="mt-5">
        {(id) => <Textarea id={id} value={note} invalid={!!error} onChange={(e) => { setNote(e.target.value); setError(''); }} placeholder="e.g. OD letter verified." />}
      </Field>
    </Dialog>
  );
}
