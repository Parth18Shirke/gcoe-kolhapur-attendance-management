import { useState } from 'react';
import { THRESHOLD } from '../data/catalog';
import { cn } from '../lib/format';

export interface Bar { key: string; label: string; pct: number; detail?: string }

/**
 * Bar chart measured against the 75% statutory line. Bars below the line turn
 * red and carry a red label, so the breach is never signalled by colour alone.
 */
export function AttendanceChart({ bars, selected, onSelect }: { bars: Bar[]; selected?: string | null; onSelect?: (key: string) => void }) {
  const [hover, setHover] = useState<string | null>(null);
  const W = 640, H = 300, L = 40, R = 12, T = 28, B = 36;
  const plotW = W - L - R, plotH = H - T - B;
  const y = (v: number) => T + plotH * (1 - v / 100);
  const slot = plotW / Math.max(bars.length, 1);
  const bw = Math.min(84, slot - 18);
  const hovered = bars.find((b) => b.key === hover);

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Attendance by class and division against the 75% minimum">
        {[0, 25, 50, 75, 100].map((t) => (
          <g key={t}>
            <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="#E2E8F0" strokeWidth={1} />
            <text x={L - 8} y={y(t) + 4} textAnchor="end" className="fill-ink-500 text-[11px]">{t === 0 ? '0' : `${t}%`}</text>
          </g>
        ))}
        {bars.map((b, i) => {
          const x = L + slot * i + (slot - bw) / 2;
          const low = b.pct < THRESHOLD;
          const dim = selected && selected !== b.key;
          const top = y(b.pct), r = 4;
          const h = y(0) - top;
          // Rounded data-end (top), square at the baseline.
          const d = `M${x},${y(0)} V${top + r} Q${x},${top} ${x + r},${top} H${x + bw - r} Q${x + bw},${top} ${x + bw},${top + r} V${y(0)} Z`;
          return (
            <g
              key={b.key}
              onMouseEnter={() => setHover(b.key)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onSelect?.(b.key)}
              className={cn(onSelect && 'cursor-pointer')}
              opacity={dim ? 0.35 : 1}
            >
              {/* Hit target wider and taller than the mark */}
              <rect x={L + slot * i} y={T} width={slot} height={plotH + B} fill="transparent" />
              {h > 0 && <path d={d} fill={low ? '#DC2626' : '#1E3A5F'} />}
              <text x={x + bw / 2} y={top - 8} textAnchor="middle" className={cn('text-[12px] font-semibold', low ? 'fill-bad-text' : 'fill-ink-900')}>{b.pct.toFixed(1)}%</text>
              <text x={x + bw / 2} y={H - 14} textAnchor="middle" className={cn('text-[12px]', low ? 'fill-bad-text font-semibold' : 'fill-ink-700')}>{b.label}</text>
            </g>
          );
        })}
        <line x1={L} x2={W - R} y1={y(THRESHOLD)} y2={y(THRESHOLD)} stroke="#DC2626" strokeWidth={1.5} strokeDasharray="5 4" pointerEvents="none" />
        <g pointerEvents="none">
          <rect x={L + 2} y={y(THRESHOLD) - 18} width={124} height={15} rx={2} fill="#FFFFFF" fillOpacity={0.9} />
          <text x={L + 6} y={y(THRESHOLD) - 7} className="fill-bad-text text-[11px] font-semibold">75% statutory minimum</text>
        </g>
      </svg>
      {hovered && (
        <div
          className="pointer-events-none absolute z-10 -translate-x-1/2 rounded-md bg-ink-900 px-3 py-2 text-[13px] text-white shadow-overlay"
          style={{ left: `${((L + slot * bars.indexOf(hovered) + slot / 2) / W) * 100}%`, top: 0 }}
        >
          <div className="font-semibold">{hovered.label} · {hovered.pct.toFixed(1)}%</div>
          {hovered.detail && <div className="text-white/80">{hovered.detail}</div>}
          <div className="text-white/80">{hovered.pct < THRESHOLD ? 'Below 75% minimum' : 'Compliant'}</div>
        </div>
      )}
      <table className="sr-only">
        <caption>Attendance by class and division</caption>
        <thead><tr><th>Class</th><th>Attendance</th></tr></thead>
        <tbody>{bars.map((b) => <tr key={b.key}><td>{b.label}</td><td>{b.pct.toFixed(1)}%</td></tr>)}</tbody>
      </table>
    </div>
  );
}
