import { Link, useSearchParams } from 'react-router-dom';
import type { RecordState } from '../../types';
import { CLASSES, COLLEGE, PERIODS, ROLE_USER } from '../../data/catalog';
import { rosterFor } from '../../data/sessions';
import { markCounts, subjectName, useApp } from '../../store/AppStore';
import { MobileHero, Page } from '../../components/Shell';
import { Card, Empty, PageHeader, RecordPill } from '../../components/ui';
import { cn, fmtDayShort } from '../../lib/format';

type Filter = 'all' | RecordState;
const FILTERS: { value: Filter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'incomplete', label: 'Incomplete' },
  { value: 'draft', label: 'Draft' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'finalized', label: 'Finalized' },
];

export default function History() {
  const { sessions, students } = useApp();
  const [params, setParams] = useSearchParams();
  const filter = (FILTERS.some((f) => f.value === params.get('filter')) ? params.get('filter') : 'all') as Filter;
  const setFilter = (f: Filter) => setParams(f === 'all' ? {} : { filter: f }, { replace: true });

  const mine = sessions
    .filter((s) => s.facultyId === ROLE_USER.faculty.id && s.record)
    .sort((a, b) => b.date.localeCompare(a.date) || b.period - a.period);
  const list = mine.filter((s) => filter === 'all' || s.record === filter);

  const tabs = (dark: boolean) => (
    <div className="no-scrollbar -mx-4 overflow-x-auto px-4 md:mx-0 md:px-0">
      <div className="flex w-max gap-1.5">
        {FILTERS.map((f) => {
          const n = f.value === 'all' ? mine.length : mine.filter((s) => s.record === f.value).length;
          const on = filter === f.value;
          return (
            <button
              key={f.value}
              type="button"
              onClick={() => setFilter(f.value)}
              className={cn('h-9 shrink-0 rounded-md border px-3 text-[13px] font-semibold',
                dark ? (on ? 'border-white bg-white text-navy' : 'border-white/30 text-white hover:bg-white/10')
                  : (on ? 'border-navy bg-navy text-white' : 'border-line bg-white text-ink-700 hover:bg-surface'))}
            >
              {f.label} <span className="font-normal opacity-75">{n}</span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      <MobileHero title="History" subtitle={`Your past sessions · ${COLLEGE.term}`}>{tabs(true)}</MobileHero>
      <Page className="!pt-4 md:!pt-8">
        <PageHeader className="hidden md:flex" title="History" subtitle={`Your past sessions · ${COLLEGE.term}. Open a session to finish marking or request a correction.`} />
        <div className="mb-4 hidden md:block">{tabs(false)}</div>
        <div className="mb-3 text-[13px] text-ink-500">{list.length} session{list.length === 1 ? '' : 's'}</div>
        <div className="grid gap-3 lg:grid-cols-2">
          {list.map((s) => {
            const c = markCounts(s, rosterFor(students, s.classKey, s.batch));
            return (
              <Link key={s.id} to={`/faculty/session/${s.id}`} className="block rounded-card focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent">
                <Card className="p-4 transition-shadow hover:shadow-raised">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[13px] font-semibold text-ink-700">{fmtDayShort(s.date)} · {PERIODS[s.period].start}</span>
                    <RecordPill state={s.record!} />
                  </div>
                  <div className="mt-1.5 text-[17px] font-semibold text-ink-900">
                    {subjectName(s.subject)} <span className="font-normal text-ink-500">· {s.subject}</span>
                  </div>
                  <div className="mt-1 flex flex-wrap items-baseline justify-between gap-x-3 text-sm">
                    <span className="text-ink-700">{CLASSES[s.classKey].label}{s.batch && ` · ${s.batch}`}</span>
                    <span className="font-semibold tabular-nums text-ink-900">
                      {c.present} / {c.total} present{c.unmarked > 0 && <span className="text-warn-text"> · {c.unmarked} unmarked</span>}
                    </span>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
        {list.length === 0 && <Card><Empty>No sessions in this state.</Empty></Card>}
      </Page>
    </>
  );
}

