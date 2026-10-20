import { useState } from 'react';
import { Download, Lock } from 'lucide-react';
import type { AuditRole } from '../../types';
import { TODAY } from '../../data/catalog';
import { useApp } from '../../store/AppStore';
import { Page } from '../../components/Shell';
import { Banner, Button, Card, Empty, PageHeader, SearchInput, Select } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { addDays, cn, downloadFile, fmtStamp, toCsv } from '../../lib/format';

const PER_PAGE = 25;
type Range = 'week' | 'month' | 'all';
const RANGE_START: Record<Range, string> = { week: addDays(TODAY, -4), month: addDays(TODAY, -30), all: '0000' };

const ROLE_STYLE: Record<AuditRole, string> = {
  Faculty: 'border-[#C7D3E3] bg-info-fill text-navy',
  HOD: 'border-[#C7D3E3] bg-white text-navy',
  Admin: 'border-[#C7D3E3] bg-white text-navy',
  System: 'border-line bg-mute-fill text-mute-text',
};

export default function AuditLog() {
  const { audit, log } = useApp();
  const toast = useToast();
  const [query, setQuery] = useState('');
  const [role, setRole] = useState<AuditRole | 'all'>('all');
  const [action, setAction] = useState('all');
  const [range, setRange] = useState<Range>('week');
  const [page, setPage] = useState(0);

  const actions = [...new Set(audit.map((a) => a.action))].sort();
  const q = query.trim().toLowerCase();
  const list = [...audit]
    .sort((a, b) => b.at.localeCompare(a.at))
    .filter((a) => (role === 'all' || a.role === role) && (action === 'all' || a.action === action) && a.at >= RANGE_START[range])
    .filter((a) => !q || `${a.actor} ${a.entity} ${a.action}`.toLowerCase().includes(q));
  const pages = Math.max(1, Math.ceil(list.length / PER_PAGE));
  const current = Math.min(page, pages - 1);
  const shown = list.slice(current * PER_PAGE, (current + 1) * PER_PAGE);
  const reset = () => setPage(0);

  const exportCsv = () => {
    downloadFile(`AMS_audit_${TODAY}.csv`, toCsv([
      ['Timestamp', 'Actor', 'Role', 'Action', 'Entity', 'Old', 'New'],
      ...list.map((a) => [a.at.replace('T', ' '), a.actor, a.role, a.action, a.entity, a.old, a.next]),
    ]), 'text/csv;charset=utf-8');
    log('Audit log exported (CSV)', `${list.length} entries`, '—', 'CSV');
    toast(`${list.length} entries exported.`);
  };

  return (
    <Page>
      <PageHeader
        title="Audit log"
        subtitle="Every sign-in, attendance submission, correction, status change and export."
        actions={<Button onClick={exportCsv}><Download className="h-4 w-4" />Export CSV</Button>}
      />
      <div className="mb-5">
        <Banner tone="info" icon={<Lock className="h-4 w-4" />}>
          <span className="font-semibold text-ink-900">Read-only.</span> Audit records cannot be edited or deleted by anyone, including administrators.
        </Banner>
      </div>
      <Card>
        <div className="flex flex-col gap-3 border-b border-line p-4 lg:flex-row lg:items-center">
          <SearchInput value={query} onChange={(v) => { setQuery(v); reset(); }} placeholder="Search actor, entity or PRN" className="lg:w-72" />
          <div className="grid grid-cols-3 gap-2 lg:flex">
            <Select aria-label="Role" value={role} onChange={(e) => { setRole(e.target.value as AuditRole | 'all'); reset(); }} className="lg:w-32">
              <option value="all">All roles</option>
              {(['Faculty', 'HOD', 'Admin', 'System'] as AuditRole[]).map((r) => <option key={r}>{r}</option>)}
            </Select>
            <Select aria-label="Action" value={action} onChange={(e) => { setAction(e.target.value); reset(); }} className="lg:w-44">
              <option value="all">All actions</option>
              {actions.map((a) => <option key={a}>{a}</option>)}
            </Select>
            <Select aria-label="Date range" value={range} onChange={(e) => { setRange(e.target.value as Range); reset(); }} className="lg:w-48">
              <option value="week">16 – 20 Oct 2026</option>
              <option value="month">Last 30 days</option>
              <option value="all">All time</option>
            </Select>
          </div>
          <span className="text-sm text-ink-500 lg:ml-auto">{shown.length} of {list.length} entries</span>
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="bg-surface text-xs font-semibold uppercase tracking-wide text-ink-500">
              <tr>
                <th className="px-4 py-3">Timestamp</th><th className="px-4 py-3">Actor</th><th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Action</th><th className="px-4 py-3">Entity</th><th className="px-4 py-3">Old → New</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {shown.map((a) => (
                <tr key={a.id} className="align-top">
                  <td className="whitespace-nowrap px-4 py-3 tabular-nums text-ink-700">{fmtStamp(a.at)}</td>
                  <td className="px-4 py-3 text-ink-900">{a.actor}</td>
                  <td className="px-4 py-3"><RoleTag role={a.role} /></td>
                  <td className="px-4 py-3 text-ink-900">{a.action}</td>
                  <td className="max-w-[220px] px-4 py-3 text-ink-700">{a.entity}</td>
                  <td className="px-4 py-3"><Change old={a.old} next={a.next} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="divide-y divide-line md:hidden">
          {shown.map((a) => (
            <li key={a.id} className="space-y-1 px-4 py-3 text-sm">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-ink-900">{a.action}</span>
                <RoleTag role={a.role} />
              </div>
              <div className="text-ink-700">{a.entity}</div>
              <Change old={a.old} next={a.next} />
              <div className="text-[13px] text-ink-500">{a.actor} · {fmtStamp(a.at)}</div>
            </li>
          ))}
        </ul>
        {list.length === 0 && <Empty>No entries match these filters.</Empty>}

        <div className="flex items-center justify-between border-t border-line px-4 py-3">
          <span className="text-sm text-ink-500">Page {current + 1} of {pages} · {PER_PAGE} per page</span>
          <div className="flex gap-2">
            <Button disabled={current === 0} onClick={() => setPage(current - 1)}>Previous</Button>
            <Button disabled={current >= pages - 1} onClick={() => setPage(current + 1)}>Next</Button>
          </div>
        </div>
      </Card>
    </Page>
  );
}

const RoleTag = ({ role }: { role: AuditRole }) => (
  <span className={cn('inline-block rounded border px-1.5 py-0.5 text-xs font-semibold', ROLE_STYLE[role])}>{role}</span>
);

const Change = ({ old, next }: { old: string; next: string }) => (
  <span className="text-ink-500">{old} → <span className="font-semibold text-ink-900">{next}</span></span>
);
