import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { Day } from '../../types';
import { CLASSES, DAYS, PERIODS, ROLE_USER, TODAY, WEEK_START } from '../../data/catalog';
import { subjectName, useApp } from '../../store/AppStore';
import { facultyWeek, span, type WeekEntry } from '../../lib/schedule';
import { MobileHero, Page } from '../../components/Shell';
import { Button, Card, PageHeader, Pill } from '../../components/ui';
import { WeekGrid } from '../../components/WeekGrid';
import { addDays, cn, fmtDayMonth, parseDate, weekdayLong } from '../../lib/format';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

const endTime = (e: Pick<WeekEntry, 'period' | 'type'>) => PERIODS[e.period + span(e.type) - 1].end;

export default function FacultyTimetable() {
  const { slots, sessions } = useApp();
  const navigate = useNavigate();
  const [weekStart, setWeekStart] = useState(WEEK_START);
  const todayIdx = Math.round((parseDate(TODAY).getTime() - parseDate(weekStart).getTime()) / 864e5);
  const [selected, setSelected] = useState<Day>(todayIdx >= 0 && todayIdx < 6 ? (todayIdx as Day) : 0);
  const [mobileGrid, setMobileGrid] = useState(false);

  const entries = facultyWeek(slots, sessions, ROLE_USER.faculty.id, weekStart);
  const cancelled = entries.filter((e) => e.cancelledReason).length;
  const rescheduled = entries.filter((e) => e.rescheduledNote).length;
  const end = addDays(weekStart, 5);
  const ws = parseDate(weekStart), we = parseDate(end);
  const weekLabel = `${ws.getDate()} – ${we.getDate()} ${MONTHS[we.getMonth()]} ${we.getFullYear()}`;
  const isThisWeek = weekStart === WEEK_START;

  const open = (e: WeekEntry) => {
    const ses = sessions.find((s) => s.date === e.date && s.period === e.period && s.classKey === e.classKey);
    if (ses) navigate(`/faculty/session/${ses.id}`);
  };

  const gridItems = entries.map((e) => ({
    key: e.key, day: e.day, period: e.period, span: span(e.type),
    node: <GridCard entry={e} today={e.date === TODAY} onOpen={() => open(e)} />,
  }));
  const dayLabels = DAYS.map((d, i) => {
    const date = addDays(weekStart, i);
    return `${d.short} ${parseDate(date).getDate()}${date === TODAY ? ' · Today' : ''}`;
  });

  const dayEntries = entries.filter((e) => e.day === selected);
  const selDate = addDays(weekStart, selected);

  return (
    <>
      <MobileHero
        title="Timetable"
        subtitle={`Week of ${weekLabel.replace(/ \d{4}$/, '')} · Odd semester`}
        action={<Button size="sm" variant="secondary" className="!border-white/40 !bg-transparent !text-white hover:!bg-white/10" onClick={() => setMobileGrid((g) => !g)}>{mobileGrid ? 'Day list' : 'Week grid'}</Button>}
      >
        <div className="grid grid-cols-6 gap-1.5">
          {DAYS.map((d, i) => {
            const date = addDays(weekStart, i);
            return (
              <button
                key={d.day}
                type="button"
                onClick={() => { setSelected(d.day); setMobileGrid(false); }}
                className={cn('flex h-14 flex-col items-center justify-center rounded-md border text-white',
                  selected === d.day && !mobileGrid ? 'border-white bg-white text-navy' : 'border-white/25 hover:bg-white/10')}
              >
                <span className="text-[11px] font-semibold uppercase">{d.short}</span>
                <span className="text-lg font-bold leading-5">{parseDate(date).getDate()}</span>
              </button>
            );
          })}
        </div>
      </MobileHero>

      {/* Phone: one day */}
      <div className="px-4 py-4 md:hidden">
        {mobileGrid ? (
          <WeekGrid items={gridItems} dayLabels={dayLabels} todayIndex={isThisWeek ? todayIdx : undefined} compactTimes minWidth={760} />
        ) : (
          <>
            <div className="mb-3 flex items-baseline justify-between">
              <h2 className="text-base font-semibold text-ink-900">{weekdayLong(selDate)}, {fmtDayMonth(selDate)}{selDate === TODAY && ' · Today'}</h2>
              <span className="text-[13px] text-ink-500">{dayEntries.filter((e) => !e.cancelledReason).length} lectures</span>
            </div>
            <div className="space-y-2.5">
              {dayEntries.map((e) => <DayCard key={e.key} entry={e} onOpen={() => open(e)} />)}
              {dayEntries.length === 0 && <Card className="px-4 py-8 text-center text-sm text-ink-500">No lectures on this day.</Card>}
            </div>
          </>
        )}
      </div>

      {/* Desktop: week grid */}
      <Page className="hidden md:block">
        <PageHeader
          title="My timetable"
          subtitle={`Week of ${weekLabel} · ${entries.length} slots${cancelled ? ` · ${cancelled} cancelled` : ''}${rescheduled ? ` · ${rescheduled} rescheduled` : ''}`}
          actions={<>
            <Button aria-label="Previous week" onClick={() => setWeekStart(addDays(weekStart, -7))}><ChevronLeft className="h-4 w-4" /></Button>
            <Button onClick={() => setWeekStart(WEEK_START)} disabled={isThisWeek}>This week</Button>
            <Button aria-label="Next week" onClick={() => setWeekStart(addDays(weekStart, 7))}><ChevronRight className="h-4 w-4" /></Button>
          </>}
        />
        <div className="mb-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-ink-700">
          <span className="inline-flex items-center gap-2"><span className="h-4 w-4 rounded border border-line bg-white" />Theory · 1 h</span>
          <span className="inline-flex items-center gap-2"><span className="h-4 w-4 rounded border border-navy/40 bg-info-fill" />Lab · 2 h</span>
          <span className="inline-flex items-center gap-2 text-ink-500 line-through"><span className="h-4 w-4 rounded border border-dashed border-ink-400" />Cancelled</span>
          <Pill tone="amber" dot={false}>Rescheduled</Pill>
          <span className="inline-flex items-center gap-2"><span className="h-4 w-4 rounded border-2 border-accent" />Today</span>
        </div>
        <WeekGrid items={gridItems} dayLabels={dayLabels} todayIndex={isThisWeek ? todayIdx : undefined} />
        <p className="mt-4 text-sm text-ink-500">Timetable is set by the department admin. To swap or reschedule a slot, contact your HOD.</p>
      </Page>
    </>
  );
}

function GridCard({ entry: e, today, onOpen }: { entry: WeekEntry; today: boolean; onOpen: () => void }) {
  const cls = CLASSES[e.classKey];
  const canOpen = today && !e.cancelledReason;
  return (
    <button
      type="button"
      onClick={onOpen}
      disabled={!canOpen}
      className={cn('flex h-full w-full flex-col rounded-md border p-2.5 text-left text-[13px] leading-snug',
        e.cancelledReason ? 'border-dashed border-ink-400 bg-white text-ink-500'
          : e.type === 'lab' ? 'border-navy/40 bg-info-fill' : 'border-line bg-white',
        today && !e.cancelledReason && 'border-2 !border-accent',
        canOpen ? 'cursor-pointer hover:shadow-raised' : 'cursor-default')}
    >
      <span className={cn('text-sm font-semibold text-ink-900', e.cancelledReason && 'text-ink-500 line-through')}>{subjectName(e.subject)}</span>
      <span className="mt-0.5 text-ink-700">{e.subject} · {cls.short}{e.batch && ` · ${e.batch}`}</span>
      <span className="text-ink-700">{e.room} · <span className="whitespace-nowrap">{PERIODS[e.period].start}–{endTime(e)}</span></span>
      <span className="mt-1.5 flex flex-wrap gap-1">
        {e.type === 'lab' && <span className="rounded bg-navy px-1.5 py-0.5 text-[11px] font-bold text-white">LAB</span>}
        {e.cancelledReason && <Pill tone="gray">Cancelled</Pill>}
        {e.rescheduledNote && <Pill tone="amber" dot={false}>Rescheduled</Pill>}
      </span>
    </button>
  );
}

function DayCard({ entry: e, onOpen }: { entry: WeekEntry; onOpen: () => void }) {
  const today = e.date === TODAY;
  return (
    <Card className={cn('flex gap-4 p-4', e.cancelledReason && 'border-dashed bg-white/60', e.type === 'lab' && !e.cancelledReason && 'border-navy/30 bg-info-fill')}>
      <div className="w-12 shrink-0 tabular-nums">
        <div className="text-[15px] font-bold text-ink-900">{PERIODS[e.period].start}</div>
        <div className="text-[13px] text-ink-500">{endTime(e)}</div>
      </div>
      <div className="min-w-0 flex-1">
        <div className={cn('text-[15px] font-semibold text-ink-900', e.cancelledReason && 'text-ink-500 line-through')}>
          {subjectName(e.subject)} <span className="font-normal text-ink-500">· {e.subject}</span>
        </div>
        <div className="mt-0.5 text-sm text-ink-700">{CLASSES[e.classKey].label}{e.batch && ` · Batch ${e.batch}`} · {e.room}</div>
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <span className={cn('rounded border px-2 py-0.5 text-[13px] font-medium', e.type === 'lab' ? 'border-navy bg-navy text-white' : 'border-line bg-white text-ink-700')}>
            {e.type === 'lab' ? 'Lab · 2 h' : 'Theory'}
          </span>
          {e.cancelledReason && <Pill tone="gray">Cancelled</Pill>}
          {e.rescheduledNote && <Pill tone="amber" dot={false}>Rescheduled</Pill>}
        </div>
        {e.cancelledReason && <p className="mt-2 text-[13px] text-ink-500">{e.cancelledReason}</p>}
        {e.rescheduledNote && <p className="mt-2 text-[13px] text-ink-500">{e.rescheduledNote}</p>}
        {today && !e.cancelledReason && (
          <Button variant="link" className="mt-2 text-sm" onClick={onOpen}>Open roll call →</Button>
        )}
      </div>
    </Card>
  );
}
