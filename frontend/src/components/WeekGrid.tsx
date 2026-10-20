import type { ReactNode } from 'react';
import { BREAKS, DAYS, PERIODS } from '../data/catalog';
import { cn } from '../lib/format';

/** Grid row for a period: header is row 1, Break sits after period 1, Lunch after period 3. */
export const periodRow = (p: number) => p + 2 + BREAKS.filter((b) => p > b.after).length;

export interface GridItem {
  key: string;
  day: number;
  period: number;
  span: number;
  node: ReactNode;
}

export function WeekGrid({
  items, dayLabels, todayIndex, compactTimes, minWidth = 960,
}: { items: GridItem[]; dayLabels?: string[]; todayIndex?: number; compactTimes?: boolean; minWidth?: number }) {
  const rows = PERIODS.length + BREAKS.length;
  const breakRows = BREAKS.map((b) => ({ ...b, row: periodRow(b.after) + 1 }));
  return (
    <div className="overflow-x-auto rounded-card border border-line bg-white">
      <div
        className="grid"
        style={{
          minWidth,
          gridTemplateColumns: '88px repeat(6, minmax(0, 1fr))',
          gridTemplateRows: `44px ${Array.from({ length: rows }, (_, i) => (breakRows.some((b) => b.row === i + 2) ? '30px' : 'minmax(84px, auto)')).join(' ')}`,
        }}
      >
        {/* Header */}
        <div className="flex items-center border-b border-r border-line bg-surface px-4 text-xs font-semibold uppercase tracking-wide text-ink-500" style={{ gridRow: 1, gridColumn: 1 }}>Time</div>
        {DAYS.map((d, i) => (
          <div
            key={d.day}
            className={cn('flex items-center border-b border-r border-line px-3 text-xs font-semibold uppercase tracking-wide last:border-r-0',
              todayIndex === i ? 'bg-accent-soft text-accent' : 'bg-surface text-ink-500')}
            style={{ gridRow: 1, gridColumn: i + 2 }}
          >
            {dayLabels?.[i] ?? d.short}
          </div>
        ))}

        {/* Time column + empty cells */}
        {PERIODS.map((p, i) => (
          <div key={p.start} className="border-b border-r border-line px-4 py-3 text-[13px] font-semibold leading-tight text-ink-700" style={{ gridRow: periodRow(i), gridColumn: 1 }}>
            {p.start}{!compactTimes && <><span className="font-normal"> –</span><br />{p.end}</>}
          </div>
        ))}
        {PERIODS.flatMap((_, pi) => DAYS.map((d, di) => (
          <div key={`${pi}-${d.day}`} className={cn('border-b border-r border-line last:border-r-0', todayIndex === di && 'bg-accent-soft/30')} style={{ gridRow: periodRow(pi), gridColumn: di + 2 }} />
        )))}
        {breakRows.map((b) => (
          <div key={b.label} className="flex items-center justify-center border-b border-line bg-surface text-[13px] text-ink-500" style={{ gridRow: b.row, gridColumn: '1 / -1' }}>
            {b.label}{!compactTimes && ` · ${b.start} – ${b.end}`}
          </div>
        ))}

        {/* Entries */}
        {items.map((it) => (
          <div key={it.key} className="relative z-10 p-1.5" style={{ gridColumn: it.day + 2, gridRow: `${periodRow(it.period)} / span ${it.span}` }}>
            {it.node}
          </div>
        ))}
      </div>
    </div>
  );
}
