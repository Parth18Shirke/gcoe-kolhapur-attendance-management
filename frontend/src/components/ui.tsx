import { useEffect, useId, useRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from 'react';
import { Link } from 'react-router-dom';
import { Lock, Search, X } from 'lucide-react';
import { cn } from '../lib/format';
import type { CorrectionStatus, Mark, RecordState, SessionStatus, Tone } from '../types';

// ---------------------------------------------------------------------------
// Status pill — status is always colour plus a written label, never colour alone.
// ---------------------------------------------------------------------------

const TONE: Record<Tone, { pill: string; dot: string }> = {
  green: { pill: 'bg-ok-fill text-ok-text ring-[#CBE7D3]', dot: 'bg-ok-dot' },
  red: { pill: 'bg-bad-fill text-bad-text ring-[#F7CFCF]', dot: 'bg-bad-dot' },
  amber: { pill: 'bg-warn-fill text-warn-text ring-[#F6DDB0]', dot: 'bg-warn-dot' },
  gray: { pill: 'bg-mute-fill text-mute-text ring-line', dot: 'bg-mute-dot' },
  info: { pill: 'bg-info-fill text-info-text ring-[#D3DDEB]', dot: 'bg-info-dot' },
};

export function Pill({
  tone, children, dot = true, dashed = false, icon, className, size = 'sm',
}: { tone: Tone; children: ReactNode; dot?: boolean; dashed?: boolean; icon?: ReactNode; className?: string; size?: 'sm' | 'md' }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 whitespace-nowrap rounded-full font-semibold ring-1 ring-inset',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-[13px]',
        dashed ? 'border border-dashed border-mute-dot bg-white text-mute-text ring-0' : TONE[tone].pill,
        className,
      )}
    >
      {icon ?? (dot && <span className={cn('h-1.5 w-1.5 shrink-0 rounded-full', dashed ? 'border border-mute-dot bg-white' : TONE[tone].dot)} />)}
      {children}
    </span>
  );
}

export const RecordPill = ({ state }: { state: RecordState }) => {
  switch (state) {
    case 'draft': return <Pill tone="gray">Draft</Pill>;
    case 'incomplete': return <Pill tone="amber">Incomplete Records</Pill>;
    case 'reviewed': return <Pill tone="info">Reviewed</Pill>;
    case 'finalized': return <Pill tone="info" icon={<Lock className="h-3 w-3" />}>Finalized</Pill>;
  }
};

export const SessionPill = ({ status }: { status: SessionStatus }) =>
  status === 'conducted' ? <Pill tone="green">Conducted</Pill>
    : status === 'cancelled' ? <Pill tone="gray">Cancelled</Pill>
      : <Pill tone="info">Scheduled</Pill>;

export const MarkPill = ({ mark, size }: { mark: Mark; size?: 'sm' | 'md' }) =>
  mark === 'present' ? <Pill tone="green" dot={false} size={size}>Present</Pill>
    : mark === 'absent' ? <Pill tone="red" dot={false} size={size}>Absent</Pill>
      : <Pill tone="gray" dashed dot={false} size={size}>Unmarked</Pill>;

export const CorrectionPill = ({ status }: { status: CorrectionStatus }) =>
  status === 'auto' ? <Pill tone="green">Auto-applied</Pill>
    : status === 'pending' ? <Pill tone="amber">Pending</Pill>
      : status === 'approved' ? <Pill tone="green">Approved</Pill>
        : <Pill tone="red">Rejected</Pill>;

/** Attendance percentage pill measured against the 75% statutory line. */
export const PctPill = ({ pct, label }: { pct: number; label?: string }) => (
  <Pill tone={pct < 75 ? 'red' : 'green'} className="tabular-nums">{label ? `${label} ` : ''}{pct.toFixed(1)}%</Pill>
);

// ---------------------------------------------------------------------------
// Buttons
// ---------------------------------------------------------------------------

type Variant = 'primary' | 'secondary' | 'danger' | 'link' | 'ghost' | 'navy';
type Size = 'sm' | 'md' | 'lg';

const VARIANT: Record<Variant, string> = {
  primary: 'bg-accent text-white hover:bg-accent-hover shadow-sm disabled:bg-mute-fill disabled:text-ink-400 disabled:shadow-none',
  secondary: 'bg-white text-ink-900 border border-line hover:bg-surface disabled:text-ink-400',
  danger: 'bg-white text-bad-text border border-[#E8A3A3] hover:bg-bad-fill disabled:text-ink-400 disabled:border-line',
  link: 'text-accent hover:underline px-0 h-auto',
  ghost: 'text-ink-700 hover:bg-mute-fill',
  navy: 'bg-navy text-white hover:bg-navy-800',
};
const SIZE: Record<Size, string> = {
  sm: 'h-9 px-3 text-[13px]',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-5 text-[15px]',
};

const btnClass = (variant: Variant, size: Size, block?: boolean, className?: string) =>
  cn(
    'inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-colors',
    'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed',
    VARIANT[variant], variant !== 'link' && SIZE[size], block && 'w-full', className,
  );

export function Button({
  variant = 'secondary', size = 'md', block, className, ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size; block?: boolean }) {
  return <button type="button" className={btnClass(variant, size, block, className)} {...rest} />;
}

export function ButtonLink({
  to, variant = 'secondary', size = 'md', block, className, children,
}: { to: string; variant?: Variant; size?: Size; block?: boolean; className?: string; children: ReactNode }) {
  return <Link to={to} className={btnClass(variant, size, block, className)}>{children}</Link>;
}

// ---------------------------------------------------------------------------
// Layout primitives
// ---------------------------------------------------------------------------

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('rounded-card border border-line bg-white', className)}>{children}</div>;
}

export function PageHeader({ title, subtitle, actions, className }: { title: ReactNode; subtitle?: ReactNode; actions?: ReactNode; className?: string }) {
  return (
    <div className={cn('mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between', className)}>
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900 sm:text-[28px] sm:leading-9">{title}</h1>
        {subtitle && <p className="mt-1 text-[15px] text-ink-700">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export function KpiCard({ label, value, valueTone, suffix, children }: { label: string; value: ReactNode; valueTone?: 'red' | 'amber'; suffix?: ReactNode; children?: ReactNode }) {
  return (
    <Card className="p-5">
      <div className="text-sm text-ink-700">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className={cn('text-[28px] font-bold leading-9 tabular-nums tracking-tight', valueTone === 'red' ? 'text-bad-text' : valueTone === 'amber' ? 'text-warn-text' : 'text-ink-900')}>{value}</span>
        {suffix && <span className="text-[15px] text-ink-500">{suffix}</span>}
      </div>
      {children && <div className="mt-2">{children}</div>}
    </Card>
  );
}

export function Logo({ size = 40, light = false }: { size?: number; light?: boolean }) {
  return (
    <div
      className={cn('flex shrink-0 items-center justify-center rounded-full border border-dashed font-semibold tracking-wide',
        light ? 'border-white/50 text-white/90' : 'border-ink-400 text-ink-700')}
      style={{ width: size, height: size, fontSize: Math.max(8, size / 5.5) }}
      aria-label="College logo placeholder"
    >
      LOGO
    </div>
  );
}

export function AmsMark({ className }: { className?: string }) {
  return <div className={cn('flex h-9 w-9 items-center justify-center rounded-md bg-white text-[11px] font-bold text-navy', className)}>AMS</div>;
}

export function Avatar({ initials, className }: { initials: string; className?: string }) {
  return <div className={cn('flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-info-fill text-[13px] font-semibold text-navy', className)}>{initials}</div>;
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="px-4 py-10 text-center text-sm text-ink-500">{children}</div>;
}

// ---------------------------------------------------------------------------
// Form controls — desktop 40px, mobile 48px
// ---------------------------------------------------------------------------

const control = 'w-full rounded-md border border-line bg-white px-3 text-[15px] text-ink-900 placeholder:text-ink-400 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 disabled:bg-surface';

export function Field({ label, required, error, hint, children, className }: { label: string; required?: boolean; error?: string; hint?: string; children: (id: string) => ReactNode; className?: string }) {
  const id = useId();
  return (
    <div className={className}>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-ink-900">
        {label}{required && <span className="font-normal text-bad-text"> (required)</span>}
      </label>
      {children(id)}
      {error ? <p className="mt-1.5 text-[13px] text-bad-text">{error}</p> : hint ? <p className="mt-1.5 text-[13px] text-ink-500">{hint}</p> : null}
    </div>
  );
}

export function Input({ className, invalid, ...rest }: InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean }) {
  return <input className={cn(control, 'h-12 sm:h-10', invalid && 'border-bad-dot focus:border-bad-dot focus:ring-bad-dot/20', className)} {...rest} />;
}

export function Textarea({ className, invalid, ...rest }: TextareaHTMLAttributes<HTMLTextAreaElement> & { invalid?: boolean }) {
  return <textarea className={cn(control, 'min-h-[84px] py-2.5', invalid && 'border-bad-dot focus:border-bad-dot focus:ring-bad-dot/20', className)} {...rest} />;
}

export function Select({ className, children, ...rest }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(control, 'h-12 cursor-pointer pr-8 sm:h-10', className)} {...rest}>
      {children}
    </select>
  );
}

export function SearchInput({ value, onChange, placeholder, className }: { value: string; onChange: (v: string) => void; placeholder: string; className?: string }) {
  return (
    <div className={cn('relative', className)}>
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500" />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className={cn(control, 'h-12 pl-9 sm:h-10')}
      />
    </div>
  );
}

/** Segmented filter chips (All / Active / Inactive …). */
export function Chips<T extends string>({ value, onChange, options, className }: { value: T; onChange: (v: T) => void; options: { value: T; label: ReactNode }[]; className?: string }) {
  return (
    <div className={cn('flex flex-wrap gap-1.5', className)} role="tablist">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="tab"
          aria-selected={value === o.value}
          onClick={() => onChange(o.value)}
          className={cn('h-9 rounded-md border px-3 text-[13px] font-semibold transition-colors',
            value === o.value ? 'border-navy bg-navy text-white' : 'border-line bg-white text-ink-700 hover:bg-surface')}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/** Underlined tabs with counts (Correction approvals). */
export function Tabs<T extends string>({ value, onChange, options }: { value: T; onChange: (v: T) => void; options: { value: T; label: string; count?: number; tone?: Tone }[] }) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-line px-2" role="tablist">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="tab"
          aria-selected={value === o.value}
          onClick={() => onChange(o.value)}
          className={cn('-mb-px flex shrink-0 items-center gap-2 border-b-2 px-4 py-3.5 text-[15px] font-medium',
            value === o.value ? 'border-accent text-ink-900' : 'border-transparent text-ink-500 hover:text-ink-900')}
        >
          {o.label}
          {o.count !== undefined && (
            <span className={cn('rounded-full px-1.5 text-xs font-semibold tabular-nums', TONE[o.tone ?? 'gray'].pill)}>{o.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Dialog — centred on desktop, bottom sheet on phones
// ---------------------------------------------------------------------------

export function Dialog({ open, onClose, title, children, footer, wide }: { open: boolean; onClose: () => void; title: ReactNode; children: ReactNode; footer?: ReactNode; wide?: boolean }) {
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    // Focus the first field, or the panel itself.
    setTimeout(() => (panel.current?.querySelector<HTMLElement>('input, textarea, select') ?? panel.current)?.focus(), 0);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink-900/40 sm:items-center sm:p-4" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div
        ref={panel}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        className={cn('flex max-h-[92vh] w-full flex-col rounded-t-xl bg-white shadow-overlay outline-none sm:rounded-lg', wide ? 'sm:max-w-2xl' : 'sm:max-w-lg')}
      >
        <div className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
          <h2 className="text-lg font-semibold text-ink-900">{title}</h2>
          <button type="button" onClick={onClose} className="-mr-1 rounded p-1 text-ink-500 hover:bg-mute-fill" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="overflow-y-auto px-5 py-4">{children}</div>
        {footer && <div className="flex flex-wrap justify-end gap-2 border-t border-line px-5 py-3">{footer}</div>}
      </div>
    </div>
  );
}

/** Alert banner (warning / offline / error). */
export function Banner({ tone, icon, children, action }: { tone: 'amber' | 'red' | 'info' | 'green'; icon?: ReactNode; children: ReactNode; action?: ReactNode }) {
  const cls = {
    amber: 'bg-warn-fill border-[#F3D9A6] text-warn-text',
    red: 'bg-bad-fill border-[#F5C6C6] text-bad-text',
    info: 'bg-info-fill border-[#D3DDEB] text-ink-700',
    green: 'bg-ok-fill border-[#CBE7D3] text-ok-text',
  }[tone];
  return (
    <div className={cn('flex items-center gap-3 rounded-md border px-4 py-3 text-sm', cls)}>
      {icon && <span className="shrink-0">{icon}</span>}
      <div className="min-w-0 flex-1">{children}</div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
