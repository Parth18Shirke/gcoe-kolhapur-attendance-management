import { useRef, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ClassKey } from '../../types';
import { CLASSES, CLASS_KEYS, COLLEGE, NOW, PEOPLE, THRESHOLD } from '../../data/catalog';
import { useApp } from '../../store/AppStore';
import { Page } from '../../components/Shell';
import { Button, Card, Dialog, Empty, KpiCard, PageHeader, PctPill, Pill, SearchInput, Select } from '../../components/ui';
import { AttendanceChart } from '../../components/AttendanceChart';
import { useToast } from '../../components/Toast';
import { cn, fmtDayMonth, hoursBetween, parseDate } from '../../lib/format';

type Year = 'all' | 'SY' | 'TY' | 'BT';

/** Incomplete sessions held by other faculty (their sessions are not loaded in the prototype). */
const OTHER_INCOMPLETE = [{ facultyId: 'f-jadhav', count: 3 }];

export default function Dashboard() {
  const { students, stats, corrections, sessions, log } = useApp();
  const navigate = useNavigate();
  const toast = useToast();
  const [year, setYear] = useState<Year>('all');
  const [classFilter, setClassFilter] = useState<ClassKey | null>(null);
  const [query, setQuery] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [reminded, setReminded] = useState(false);
  const [ttOpen, setTtOpen] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);

  const active = students.filter((s) => s.status === 'Active' && stats[s.prn]);
  const sum = (list: typeof active) => {
    const a = list.reduce((x, s) => x + stats[s.prn].attended, 0);
    const c = list.reduce((x, s) => x + stats[s.prn].conducted, 0);
    return c ? (a / c) * 100 : 0;
  };
  const deptPct = sum(active);
  const defaulters = active.filter((s) => stats[s.prn].pct < THRESHOLD);

  const classBars = CLASS_KEYS
    .filter((k) => year === 'all' || CLASSES[k].year === year)
    .map((k) => {
      const list = active.filter((s) => s.classKey === k);
      const below = list.filter((s) => stats[s.prn].pct < THRESHOLD).length;
      return { key: k, label: CLASSES[k].short, pct: sum(list), detail: `${list.length} students · ${below} below 75%`, below };
    });

  const pending = corrections.filter((c) => c.status === 'pending').sort((a, b) => a.requestedAt.localeCompare(b.requestedAt));
  const oldestDays = pending.length ? Math.floor(hoursBetween(parseDate(pending[0].requestedAt), NOW) / 24) : 0;

  const patilIncomplete = sessions.filter((s) => s.record === 'incomplete').length;
  const incompleteBy = [...OTHER_INCOMPLETE, ...(patilIncomplete ? [{ facultyId: 'f-patil', count: patilIncomplete }] : [])];
  const incompleteTotal = incompleteBy.reduce((a, b) => a + b.count, 0);

  const worst = [...classBars].sort((a, b) => a.pct - b.pct)[0];

  const q = query.trim().toLowerCase();
  const tableRows = defaulters
    .filter((s) => (year === 'all' || CLASSES[s.classKey].year === year) && (!classFilter || s.classKey === classFilter))
    .filter((s) => !q || s.name.toLowerCase().includes(q) || s.prn.toLowerCase().includes(q))
    .sort((a, b) => stats[a.prn].pct - stats[b.prn].pct);
  const shown = showAll ? tableRows : tableRows.slice(0, 12);

  const viewClass = (k: ClassKey) => {
    setClassFilter(k);
    setShowAll(true);
    setTimeout(() => tableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0);
  };

  const sendReminder = () => {
    log('Reminder sent', 'Incomplete Records', '—', incompleteBy.map((x) => `${PEOPLE[x.facultyId].name} (${x.count})`).join(' · '));
    setReminded(true);
    toast('Reminder emailed to faculty with incomplete sessions.');
  };

  return (
    <Page>
      <PageHeader
        title="Department dashboard"
        subtitle={`${COLLEGE.department} · ${COLLEGE.term} · 1 Aug – ${fmtDayMonth('2026-10-20')} · updated 11:00`}
        actions={<>
          <Select aria-label="Year" value={year} onChange={(e) => { setYear(e.target.value as Year); setClassFilter(null); }} className="w-36">
            <option value="all">All years</option>
            <option value="SY">SY</option>
            <option value="TY">TY</option>
            <option value="BT">BTech</option>
          </Select>
          <Button variant="primary" onClick={() => navigate('/hod/reports?type=defaulter')}>Generate report</Button>
        </>}
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Department attendance" value={`${deptPct.toFixed(1)}%`} valueTone={deptPct < THRESHOLD ? 'red' : undefined}>
          <Pill tone={deptPct < THRESHOLD ? 'red' : 'green'}>{deptPct < THRESHOLD ? 'Below 75%' : 'Above 75%'} · −1.2 pts this month</Pill>
        </KpiCard>
        <KpiCard label="Students below 75%" value={defaulters.length} valueTone="red" suffix={`of ${active.length}`}>
          <button type="button" className="text-left text-[13px] text-ink-500 hover:text-accent" onClick={() => { setClassFilter(null); setShowAll(true); tableRef.current?.scrollIntoView({ behavior: 'smooth' }); }}>
            Email alerts sent Mon 19 Oct · view list ↓
          </button>
        </KpiCard>
        <KpiCard label="Incomplete sessions" value={incompleteTotal} valueTone="amber">
          <Pill tone="amber">Incomplete Records · {incompleteBy.length} faculty</Pill>
        </KpiCard>
        <KpiCard label="Pending corrections" value={pending.length}>
          {pending.length > 0 ? <Pill tone="amber">Pending · oldest {oldestDays} day{oldestDays === 1 ? '' : 's'}</Pill> : <Pill tone="green">All reviewed</Pill>}
        </KpiCard>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1.75fr)_minmax(0,1.2fr)]">
        <Card className="p-5">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-base font-semibold text-ink-900">Attendance by class &amp; division</h2>
            <span className="text-[13px] text-ink-500">{classFilter ? <button type="button" className="text-accent hover:underline" onClick={() => setClassFilter(null)}>Clear filter: {CLASSES[classFilter].short}</button> : 'Click a bar to filter defaulters'}</span>
          </div>
          <AttendanceChart bars={classBars} selected={classFilter} onSelect={(k) => (classFilter === k ? setClassFilter(null) : viewClass(k as ClassKey))} />
        </Card>

        <Card>
          <h2 className="border-b border-line px-5 py-4 text-base font-semibold text-ink-900">Needs your attention</h2>
          <ul className="divide-y divide-line">
            {pending.length > 0 && (
              <Attention dot="amber" title={`${pending.length} corrections awaiting approval`}
                detail={`Oldest from ${PEOPLE[pending[0].facultyId].name}, ${oldestDays} days ago`}
                action={<Button size="sm" onClick={() => navigate('/hod/approvals')}>Review</Button>} />
            )}
            {worst && worst.pct < THRESHOLD && (
              <Attention dot="red" title={`${CLASSES[worst.key as ClassKey].label} is below 75%`}
                detail={`${worst.pct.toFixed(1)}% overall · ${worst.below} defaulters`}
                action={<Button size="sm" onClick={() => viewClass(worst.key as ClassKey)}>View list</Button>} />
            )}
            {incompleteTotal > 0 && (
              <Attention dot="amber" title={`${incompleteTotal} sessions with Incomplete Records`}
                detail={incompleteBy.map((x) => `${PEOPLE[x.facultyId].name} (${x.count})`).join(' · ')}
                action={<Button size="sm" onClick={sendReminder} disabled={reminded}>{reminded ? 'Reminder sent' : 'Send reminder'}</Button>} />
            )}
            <Attention dot="gray" title="Cloud Computing cancelled twice this month"
              detail="BTech CSE — Div A · 1 make-up scheduled"
              action={<Button size="sm" onClick={() => setTtOpen(true)}>Timetable</Button>} />
            <Attention dot="navy" title="October defaulter list due" detail="To Principal's office by 31 Oct"
              action={<Button size="sm" onClick={() => navigate('/hod/reports?type=defaulter')}>Generate</Button>} />
          </ul>
        </Card>
      </div>

      <div ref={tableRef} className="scroll-mt-20">
        <Card className="mt-6">
          <div className="flex flex-col gap-3 border-b border-line px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-base font-semibold text-ink-900">
              Defaulters (below 75%){classFilter && <span className="font-normal text-ink-500"> · {CLASSES[classFilter].label}</span>}
            </h2>
            <div className="flex items-center gap-3">
              <SearchInput value={query} onChange={setQuery} placeholder="Search name or PRN" className="w-full sm:w-64" />
              <button type="button" onClick={() => setShowAll((s) => !s)} className="shrink-0 text-sm text-ink-500 hover:text-accent">
                {showAll || tableRows.length <= 12 ? `All ${tableRows.length}` : `Lowest 12 of ${tableRows.length}`}
              </button>
            </div>
          </div>

          {/* Desktop table */}
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full text-left text-[15px]">
              <thead className="bg-surface text-xs font-semibold uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="px-5 py-3">Name</th><th className="px-4 py-3">PRN</th><th className="px-4 py-3">Class</th>
                  <th className="px-4 py-3">Subject-wise %</th><th className="px-5 py-3">Overall</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {shown.map((s) => (
                  <tr key={s.prn} className="hover:bg-surface/60">
                    <td className="px-5 py-3 text-ink-900">{s.name}</td>
                    <td className="px-4 py-3 tabular-nums text-ink-700">{s.prn}</td>
                    <td className="px-4 py-3 text-ink-700">{CLASSES[s.classKey].label}</td>
                    <td className="px-4 py-3"><SubjectPills prn={s.prn} /></td>
                    <td className="px-5 py-3"><PctPill pct={stats[s.prn].pct} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Phone cards */}
          <ul className="divide-y divide-line md:hidden">
            {shown.map((s) => (
              <li key={s.prn} className="px-4 py-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-medium text-ink-900">{s.name}</div>
                    <div className="text-[13px] text-ink-500">{s.prn} · {CLASSES[s.classKey].short}</div>
                  </div>
                  <PctPill pct={stats[s.prn].pct} />
                </div>
                <div className="mt-2"><SubjectPills prn={s.prn} /></div>
              </li>
            ))}
          </ul>
          {shown.length === 0 && <Empty>No defaulters match.</Empty>}
        </Card>
      </div>

      <Dialog open={ttOpen} onClose={() => setTtOpen(false)} title="Cloud Computing · BTech CSE — Div A">
        <ul className="space-y-3 text-sm">
          <li className="flex items-start justify-between gap-3"><span><span className="font-medium text-ink-900">Tue 20 Oct, 14:15</span><br /><span className="text-ink-500">Official duty — DBATU paper-setting meeting</span></span><Pill tone="gray">Cancelled</Pill></li>
          <li className="flex items-start justify-between gap-3"><span><span className="font-medium text-ink-900">Thu 8 Oct, 14:15</span><br /><span className="text-ink-500">Faculty on medical leave</span></span><Pill tone="gray">Cancelled</Pill></li>
          <li className="flex items-start justify-between gap-3"><span><span className="font-medium text-ink-900">Fri 23 Oct, 11:30 · Room 302</span><br /><span className="text-ink-500">Make-up for Tue 20 Oct</span></span><Pill tone="amber" dot={false}>Rescheduled</Pill></li>
        </ul>
        <p className="mt-4 text-[13px] text-ink-500">Timetable changes are made by the department admin. Cancelled sessions are excluded from attendance percentages.</p>
      </Dialog>
    </Page>
  );
}

function Attention({ dot, title, detail, action }: { dot: 'amber' | 'red' | 'gray' | 'navy'; title: string; detail: string; action: ReactNode }) {
  return (
    <li className="flex items-center gap-3 px-5 py-3.5">
      <span className={cn('h-2 w-2 shrink-0 rounded-full', { amber: 'bg-warn-dot', red: 'bg-bad-dot', gray: 'bg-mute-dot', navy: 'bg-navy' }[dot])} />
      <div className="min-w-0 flex-1">
        <div className="text-[15px] font-medium text-ink-900">{title}</div>
        <div className="text-[13px] text-ink-500">{detail}</div>
      </div>
      <div className="shrink-0">{action}</div>
    </li>
  );
}

function SubjectPills({ prn }: { prn: string }) {
  const { stats } = useApp();
  return (
    <div className="flex flex-wrap gap-1.5">
      {stats[prn].subjects.map((s) => (
        <Pill key={s.code} tone={s.pct < THRESHOLD ? 'red' : 'green'} dot={false} className="rounded-md tabular-nums">
          {s.code} · {Math.round(s.pct)}%
        </Pill>
      ))}
    </div>
  );
}
