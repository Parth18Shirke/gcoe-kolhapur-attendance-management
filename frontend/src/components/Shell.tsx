import { useEffect, useRef, useState, type ComponentType, type ReactNode } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Bell, CalendarDays, CheckCircle2, Clock, FileText, Home, LayoutGrid, LogOut, Menu, Pencil, Shield, Users, X,
} from 'lucide-react';
import type { Role } from '../types';
import { COLLEGE, ROLE_USER } from '../data/catalog';
import { useApp } from '../store/AppStore';
import { cn, fmtDayMonth } from '../lib/format';
import { Avatar, Logo } from './ui';

interface NavItem { to: string; label: string; icon: ComponentType<{ className?: string }>; end?: boolean; badge?: number }

export const ROLE_HOME: Record<Role, string> = { faculty: '/faculty', hod: '/hod', admin: '/admin' };

function useNav(role: Role): NavItem[] {
  const { corrections } = useApp();
  const pending = corrections.filter((c) => c.status === 'pending').length;
  if (role === 'faculty') {
    return [
      { to: '/faculty', label: 'Today', icon: Home, end: true },
      { to: '/faculty/timetable', label: 'Timetable', icon: CalendarDays },
      { to: '/faculty/history', label: 'History', icon: Clock },
      { to: '/faculty/corrections', label: 'Corrections', icon: Pencil },
    ];
  }
  if (role === 'hod') {
    return [
      { to: '/hod', label: 'Dashboard', icon: LayoutGrid, end: true },
      { to: '/hod/approvals', label: 'Correction approvals', icon: CheckCircle2, badge: pending },
      { to: '/hod/reports', label: 'Reports', icon: FileText },
    ];
  }
  return [
    { to: '/admin', label: 'Students', icon: Users, end: true },
    { to: '/admin/timetable', label: 'Timetable setup', icon: CalendarDays },
    { to: '/admin/reports', label: 'Reports', icon: FileText },
    { to: '/admin/audit', label: 'Audit log', icon: Shield },
  ];
}

// ---------------------------------------------------------------------------
// Prototype role switcher
// ---------------------------------------------------------------------------

export function PreviewBar() {
  const { role, signIn } = useApp();
  const navigate = useNavigate();
  return (
    <div data-preview-bar className="flex h-9 items-center justify-between gap-3 bg-navy-900 px-3 text-[13px] text-white/80 sm:justify-end sm:px-4">
      <span><span className="hidden sm:inline">Prototype · </span>preview as</span>
      <div className="flex gap-1">
        {(['faculty', 'hod', 'admin'] as Role[]).map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => { signIn(r); navigate(ROLE_HOME[r]); }}
            className={cn('h-7 rounded px-3 font-semibold', role === r ? 'bg-white text-ink-900' : 'text-white hover:bg-white/10')}
          >
            {r === 'faculty' ? 'Faculty' : r === 'hod' ? 'HOD' : 'Admin'}
          </button>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

interface Note { id: string; title: string; detail: string; to?: string }

function useNotes(role: Role): Note[] {
  const { corrections, sessions } = useApp();
  if (role === 'hod') {
    const pending = corrections.filter((c) => c.status === 'pending');
    return [
      ...pending.slice(0, 4).map((c) => ({ id: c.id, title: `Correction awaiting approval · ${c.prn}`, detail: `Requested ${fmtDayMonth(c.requestedAt)}`, to: '/hod/approvals' })),
      { id: 'due', title: 'October defaulter list due', detail: "To Principal's office by 31 Oct", to: '/hod/reports?type=defaulter' },
    ];
  }
  if (role === 'faculty') {
    const decided = corrections.filter((c) => c.facultyId === 'f-patil' && (c.status === 'approved' || c.status === 'rejected'));
    const incomplete = sessions.filter((s) => s.record === 'incomplete').length;
    return [
      ...(incomplete ? [{ id: 'inc', title: `${incomplete} sessions have incomplete records`, detail: 'Mark the remaining students', to: '/faculty/history?filter=incomplete' }] : []),
      ...decided.map((c) => ({ id: c.id, title: `HOD ${c.status} correction · ${c.prn.slice(-4)}`, detail: c.decisionNote ?? '', to: '/faculty/corrections' })),
    ];
  }
  return [
    { id: 'imp', title: 'Import finished · TY_CSE_DivB_2026-27.xlsx', detail: '212 rows · 4 skipped', to: '/admin/audit' },
    { id: 'clash', title: 'Room clash overridden', detail: 'CS604 · TY CSE — Div B · Thu 14:15', to: '/admin/timetable' },
  ];
}

export function NotificationBell({ role, dark }: { role: Role; dark?: boolean }) {
  const notes = useNotes(role);
  const [open, setOpen] = useState(false);
  const [seen, setSeen] = useState(role === 'admin');
  const navigate = useNavigate();
  const ref = useClickOutside<HTMLDivElement>(() => setOpen(false));
  const count = seen ? 0 : notes.length;
  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => { setOpen((o) => !o); setSeen(true); }}
        className={cn('relative rounded-full p-2', dark ? 'text-white hover:bg-white/10' : 'text-ink-700 hover:bg-mute-fill')}
        aria-label={`Notifications${count ? ` (${count} unread)` : ''}`}
      >
        <Bell className="h-5 w-5" />
        {count > 0 && (
          <span className="absolute right-0.5 top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-bad-dot px-1 text-[11px] font-bold text-white ring-2 ring-white">
            {count}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 max-w-[calc(100vw-24px)] overflow-hidden rounded-lg border border-line bg-white text-left shadow-overlay">
          <div className="border-b border-line px-4 py-3 text-sm font-semibold text-ink-900">Notifications</div>
          {notes.length === 0 && <div className="px-4 py-6 text-center text-sm text-ink-500">You're all caught up.</div>}
          {notes.map((n) => (
            <button
              key={n.id}
              type="button"
              onClick={() => { setOpen(false); if (n.to) navigate(n.to); }}
              className="block w-full border-b border-line px-4 py-3 text-left last:border-0 hover:bg-surface"
            >
              <div className="text-sm font-medium text-ink-900">{n.title}</div>
              {n.detail && <div className="mt-0.5 text-[13px] text-ink-500">{n.detail}</div>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function useClickOutside<T extends HTMLElement>(onOutside: () => void) {
  const ref = useRef<T>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => ref.current && !ref.current.contains(e.target as Node) && onOutside();
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [onOutside]);
  return ref;
}

const roleBadge = (role: Role) =>
  role === 'hod' ? 'HOD · CSE' : role === 'admin' ? 'ADMIN' : 'FACULTY';

export function AccountMenu({ role, compact, dark }: { role: Role; compact?: boolean; dark?: boolean }) {
  const user = ROLE_USER[role];
  const { signOut } = useApp();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useClickOutside<HTMLDivElement>(() => setOpen(false));
  return (
    <div className="relative" ref={ref}>
      <button type="button" onClick={() => setOpen((o) => !o)} className="flex items-center gap-2.5 rounded-md p-1 text-left" aria-label="Account menu">
        <Avatar initials={user.initials} className={dark ? 'bg-white/90' : undefined} />
        {!compact && (
          <span className="hidden sm:block">
            <span className="block text-[15px] font-semibold leading-5 text-ink-900">{user.name}</span>
            <span className={cn('mt-0.5 inline-block rounded px-1.5 text-[11px] font-bold leading-4',
              role === 'faculty' ? 'border border-[#C7D3E3] bg-info-fill text-navy' : 'bg-navy text-white')}>
              {roleBadge(role)}
            </span>
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 z-40 mt-2 w-64 overflow-hidden rounded-lg border border-line bg-white shadow-overlay">
          <div className="border-b border-line px-4 py-3">
            <div className="text-sm font-semibold text-ink-900">{user.name}</div>
            <div className="text-[13px] text-ink-500">{user.email}</div>
          </div>
          <button
            type="button"
            onClick={() => { signOut(); navigate('/login'); }}
            className="flex w-full items-center gap-2 px-4 py-3 text-sm text-ink-700 hover:bg-surface"
          >
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

function SideNav({ items, onNavigate }: { items: NavItem[]; onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1 p-3" aria-label="Main">
      {items.map(({ to, label, icon: Icon, end, badge }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) => cn('flex min-h-[44px] items-center gap-3 rounded-md px-3 py-2 text-[15px] font-semibold leading-5 text-white',
            isActive ? 'bg-white/15' : 'text-white/90 hover:bg-white/5')}
        >
          <Icon className="h-5 w-5 shrink-0" />
          <span className="flex-1">{label}</span>
          {!!badge && <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-warn-fill px-1.5 text-xs font-bold text-warn-text">{badge}</span>}
        </NavLink>
      ))}
    </nav>
  );
}

function BottomNav({ items }: { items: NavItem[] }) {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-4 border-t border-line bg-white pb-[env(safe-area-inset-bottom)] md:hidden" aria-label="Main">
      {items.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) => cn('flex h-16 flex-col items-center justify-center gap-1 text-[13px]',
            isActive ? 'font-semibold text-navy' : 'text-ink-500')}
        >
          <Icon className="h-5 w-5" />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

export function AppLayout({ role }: { role: Role }) {
  const items = useNav(role);
  const [collapsed, setCollapsed] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const { pathname } = useLocation();
  const isFaculty = role === 'faculty';
  // The roll-call screen is full-height on phones with its own action bar.
  const isRollCall = pathname.startsWith('/faculty/session/');

  useEffect(() => { setDrawer(false); }, [pathname]);
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);

  const subtitle = `Attendance Management System · ${role === 'admin' ? 'Administration' : COLLEGE.department}`;

  return (
    <div className="min-h-screen bg-surface">
      <PreviewBar />
      {/* Desktop header (and phone header for HOD/Admin) */}
      <header className={cn('sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-line bg-white px-3 sm:px-5', isFaculty && 'hidden md:flex')}>
        <button
          type="button"
          onClick={() => (window.matchMedia('(min-width: 768px)').matches ? setCollapsed((c) => !c) : setDrawer(true))}
          className="rounded-md p-2 text-ink-700 hover:bg-mute-fill"
          aria-label="Toggle navigation"
        >
          <Menu className="h-5 w-5" />
        </button>
        <Logo size={40} />
        <div className="min-w-0 flex-1">
          <div className="truncate text-[15px] font-semibold text-ink-900 sm:text-base"><span className="sm:hidden">{COLLEGE.short}</span><span className="hidden sm:inline">{COLLEGE.name}</span></div>
          <div className="hidden truncate text-[13px] text-ink-500 sm:block">{subtitle}</div>
        </div>
        <NotificationBell role={role} />
        <AccountMenu role={role} />
      </header>

      <div className="flex">
        {/* Desktop sidebar */}
        <aside className={cn('sticky top-16 hidden h-[calc(100vh-4rem)] shrink-0 overflow-y-auto bg-navy transition-[width] md:block', collapsed ? 'w-0' : 'w-60')}>
          <SideNav items={items} />
        </aside>

        {/* Phone drawer (HOD/Admin) */}
        {drawer && (
          <div className="fixed inset-0 z-50 md:hidden">
            <div className="absolute inset-0 bg-ink-900/40" onClick={() => setDrawer(false)} />
            <aside className="absolute inset-y-0 left-0 w-72 bg-navy shadow-overlay">
              <div className="flex items-center justify-between px-4 py-4">
                <div className="flex items-center gap-3 text-white">
                  <Logo size={36} light />
                  <span className="text-[15px] font-semibold">{COLLEGE.short}</span>
                </div>
                <button type="button" onClick={() => setDrawer(false)} className="rounded p-1 text-white/80 hover:bg-white/10" aria-label="Close navigation">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <SideNav items={items} onNavigate={() => setDrawer(false)} />
            </aside>
          </div>
        )}

        <main className={cn('min-w-0 flex-1', isFaculty && !isRollCall && 'pb-20 md:pb-0')}>
          <Outlet />
        </main>
      </div>

      {isFaculty && !isRollCall && <BottomNav items={items} />}
    </div>
  );
}

/** Page body padding used by every desktop page. */
export function Page({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('w-full max-w-[1480px] px-4 py-6 sm:px-8 sm:py-8', className)}>{children}</div>;
}

/** Navy header block used by faculty pages on phones. */
export function MobileHero({ title, subtitle, action, children }: { title: ReactNode; subtitle?: ReactNode; action?: ReactNode; children?: ReactNode }) {
  return (
    <div className="bg-navy px-4 pb-3 pt-3 text-white md:hidden">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl font-bold leading-7">{title}</h1>
          {subtitle && <p className="mt-0.5 text-[13px] text-white/75">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children && <div className="mt-3">{children}</div>}
    </div>
  );
}
