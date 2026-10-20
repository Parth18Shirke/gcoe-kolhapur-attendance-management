import { useState, type ChangeEvent } from 'react';
import { FileUp, Upload } from 'lucide-react';
import type { ClassKey, Student, StudentStatus } from '../../types';
import { CLASSES, CLASS_KEYS, COLLEGE } from '../../data/catalog';
import { useApp } from '../../store/AppStore';
import { Page } from '../../components/Shell';
import { Banner, Button, Card, Chips, Dialog, Empty, Field, PageHeader, Pill, SearchInput, Select, Textarea } from '../../components/ui';
import { useToast } from '../../components/Toast';

type StatusFilter = 'all' | StudentStatus;
const PAGE = 50;

const StatusPill = ({ status }: { status: StudentStatus }) =>
  status === 'Active' ? <Pill tone="green">Active</Pill> : <Pill tone="gray">{status}</Pill>;

export default function Students() {
  const { students } = useApp();
  const [query, setQuery] = useState('');
  const [cls, setCls] = useState<ClassKey | 'all'>('all');
  const [status, setStatus] = useState<StatusFilter>('all');
  const [limit, setLimit] = useState(PAGE);
  const [editing, setEditing] = useState<Student | null>(null);
  const [importOpen, setImportOpen] = useState(false);

  const q = query.trim().toLowerCase();
  const list = students.filter((s) =>
    (cls === 'all' || s.classKey === cls) &&
    (status === 'all' || s.status === status) &&
    (!q || s.prn.toLowerCase().includes(q) || s.name.toLowerCase().includes(q) || s.email.includes(q)));
  const shown = list.slice(0, limit);
  const count = (st: StudentStatus) => students.filter((s) => (cls === 'all' || s.classKey === cls) && s.status === st).length;

  return (
    <Page>
      <PageHeader
        title="Students"
        subtitle={`${students.length} students in CSE · Records are never deleted — change status to Inactive or Archived instead.`}
        actions={<Button variant="primary" onClick={() => setImportOpen(true)}><Upload className="h-4 w-4" />Import Excel / CSV</Button>}
      />
      <Card>
        <div className="flex flex-col gap-3 border-b border-line p-4 lg:flex-row lg:items-center">
          <SearchInput value={query} onChange={(v) => { setQuery(v); setLimit(PAGE); }} placeholder="Search PRN, name or email" className="lg:w-80" />
          <Select aria-label="Class" value={cls} onChange={(e) => { setCls(e.target.value as ClassKey | 'all'); setLimit(PAGE); }} className="lg:w-48">
            <option value="all">All classes</option>
            {CLASS_KEYS.map((k) => <option key={k} value={k}>{CLASSES[k].label}</option>)}
          </Select>
          <Chips<StatusFilter>
            value={status}
            onChange={(v) => { setStatus(v); setLimit(PAGE); }}
            options={[
              { value: 'all', label: 'All' },
              { value: 'Active', label: `Active ${count('Active')}` },
              { value: 'Inactive', label: `Inactive ${count('Inactive')}` },
              { value: 'Archived', label: `Archived ${count('Archived')}` },
            ]}
          />
          <span className="text-sm text-ink-500 lg:ml-auto">{list.length} shown</span>
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="w-full text-left text-[15px]">
            <thead className="bg-surface text-xs font-semibold uppercase tracking-wide text-ink-500">
              <tr>
                <th className="px-4 py-3">PRN</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Program</th>
                <th className="px-4 py-3">Sem</th><th className="px-4 py-3">Div</th><th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Status</th><th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {shown.map((s) => (
                <tr key={s.prn} className="hover:bg-surface/60">
                  <td className="px-4 py-3 tabular-nums text-ink-900">{s.prn}</td>
                  <td className="px-4 py-3 text-ink-900">{s.name}</td>
                  <td className="px-4 py-3 text-ink-700">B.Tech CSE</td>
                  <td className="px-4 py-3 text-ink-700">{CLASSES[s.classKey].sem}</td>
                  <td className="px-4 py-3 text-ink-700">{CLASSES[s.classKey].div}</td>
                  <td className="px-4 py-3 text-ink-700">{s.email}</td>
                  <td className="px-4 py-3"><StatusPill status={s.status} /></td>
                  <td className="px-4 py-3 text-right"><Button size="sm" onClick={() => setEditing(s)}>Change status</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="divide-y divide-line md:hidden">
          {shown.map((s) => (
            <li key={s.prn} className="flex items-center gap-3 px-4 py-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2"><span className="font-medium text-ink-900">{s.name}</span><StatusPill status={s.status} /></div>
                <div className="text-[13px] text-ink-500">{s.prn} · {CLASSES[s.classKey].short}</div>
                <div className="truncate text-[13px] text-ink-500">{s.email}</div>
              </div>
              <Button size="sm" onClick={() => setEditing(s)}>Change</Button>
            </li>
          ))}
        </ul>
        {list.length === 0 && <Empty>No students match these filters.</Empty>}
        {list.length > limit && (
          <div className="border-t border-line p-3 text-center">
            <Button variant="ghost" onClick={() => setLimit(limit + PAGE)}>Show {Math.min(PAGE, list.length - limit)} more</Button>
          </div>
        )}
      </Card>

      {editing && <StatusDialog student={editing} onClose={() => setEditing(null)} />}
      {importOpen && <ImportDialog onClose={() => setImportOpen(false)} />}
    </Page>
  );
}

function StatusDialog({ student, onClose }: { student: Student; onClose: () => void }) {
  const { setStudentStatus } = useApp();
  const toast = useToast();
  const options = (['Active', 'Inactive', 'Archived'] as StudentStatus[]).filter((s) => s !== student.status);
  const [next, setNext] = useState<StudentStatus>(options[0]);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const save = () => {
    if (reason.trim().length < 4) { setError('Enter a reason — it is saved to the audit log.'); return; }
    setStudentStatus(student.prn, next, reason.trim());
    toast(`${student.name} is now ${next}.`);
    onClose();
  };
  return (
    <Dialog open onClose={onClose} title="Change status"
      footer={<><Button onClick={onClose}>Cancel</Button><Button variant="primary" onClick={save}>Save status</Button></>}>
      <p className="text-sm text-ink-700"><span className="font-semibold text-ink-900">{student.name}</span> · {student.prn} · {CLASSES[student.classKey].label}</p>
      <p className="mt-1 text-sm text-ink-700">Current status: <StatusPill status={student.status} /></p>
      <Field label="New status" className="mt-4">
        {(id) => <Select id={id} value={next} onChange={(e) => setNext(e.target.value as StudentStatus)}>{options.map((o) => <option key={o}>{o}</option>)}</Select>}
      </Field>
      <Field label="Reason" required error={error} className="mt-4">
        {(id) => <Textarea id={id} value={reason} invalid={!!error} onChange={(e) => { setReason(e.target.value); setError(''); }} placeholder="e.g. Left college — TC issued" />}
      </Field>
      <p className="mt-3 text-[13px] text-ink-500">Inactive and Archived students leave classroom rosters but their attendance history is kept.</p>
    </Dialog>
  );
}

/** Expected columns: PRN, Name, Class (e.g. "TY-A" or "TY CSE — Div A"), Email (optional). */
function parseCsv(text: string): { rows: Student[]; errors: string[] } {
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const rows: Student[] = [];
  const errors: string[] = [];
  const start = /prn/i.test(lines[0] ?? '') ? 1 : 0;
  lines.slice(start).forEach((line, i) => {
    const [prn, name, cls, email] = line.split(',').map((c) => c.replace(/^"|"$/g, '').trim());
    const classKey = CLASS_KEYS.find((k) => k === cls?.toUpperCase() || CLASSES[k].label === cls || CLASSES[k].short === cls);
    if (!/^\d{4}BCS\d{4}$/i.test(prn ?? '')) { errors.push(`Row ${i + start + 1}: invalid PRN "${prn ?? ''}"`); return; }
    if (!name) { errors.push(`Row ${i + start + 1}: missing name`); return; }
    if (!classKey) { errors.push(`Row ${i + start + 1}: unknown class "${cls ?? ''}"`); return; }
    const p = prn.toUpperCase();
    rows.push({ prn: p, name, classKey, email: email || `${p.toLowerCase()}@${COLLEGE.emailDomain}`, status: 'Active', batch: `${CLASSES[classKey].div}1` });
  });
  return { rows, errors };
}

function ImportDialog({ onClose }: { onClose: () => void }) {
  const { importStudents, students } = useApp();
  const toast = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<{ rows: Student[]; errors: string[] } | null>(null);
  const [excel, setExcel] = useState(false);
  const existing = new Set(students.map((s) => s.prn));

  const onFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    const isExcel = /\.xlsx?$/i.test(f.name);
    setExcel(isExcel);
    setParsed(isExcel ? null : parseCsv(await f.text()));
  };

  const dupes = parsed ? parsed.rows.filter((r) => existing.has(r.prn)).length : 0;
  const confirm = () => {
    if (!parsed || !file) return;
    const res = importStudents(parsed.rows, file.name);
    toast(`${res.added} students imported · ${res.skipped + parsed.errors.length} skipped.`);
    onClose();
  };

  return (
    <Dialog open onClose={onClose} title="Import students" wide
      footer={<><Button onClick={onClose}>Cancel</Button><Button variant="primary" disabled={!parsed || parsed.rows.length - dupes === 0} onClick={confirm}>
        Import {parsed ? parsed.rows.length - dupes : ''} students
      </Button></>}>
      <label className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed border-line px-4 py-8 text-center hover:bg-surface">
        <FileUp className="h-8 w-8 text-ink-500" />
        <span className="text-[15px] font-medium text-ink-900">{file ? file.name : 'Choose an Excel or CSV file'}</span>
        <span className="text-[13px] text-ink-500">Columns: PRN, Name, Class (e.g. TY-A), Email (optional)</span>
        <input type="file" accept=".csv,.xlsx,.xls" className="sr-only" onChange={onFile} />
      </label>
      {excel && (
        <div className="mt-4"><Banner tone="info">Excel files are validated by the server when the API is connected. In this prototype, save the sheet as CSV to preview it here.</Banner></div>
      )}
      {parsed && (
        <div className="mt-4 space-y-3">
          <div className="flex flex-wrap gap-2 text-sm">
            <Pill tone="green">{parsed.rows.length - dupes} new</Pill>
            {dupes > 0 && <Pill tone="gray">{dupes} already exist — skipped</Pill>}
            {parsed.errors.length > 0 && <Pill tone="red">{parsed.errors.length} invalid</Pill>}
          </div>
          {parsed.errors.length > 0 && (
            <ul className="max-h-28 overflow-y-auto rounded-md bg-bad-fill px-3 py-2 text-[13px] text-bad-text">
              {parsed.errors.map((e) => <li key={e}>{e}</li>)}
            </ul>
          )}
          {parsed.rows.length > 0 && (
            <div className="max-h-56 overflow-auto rounded-md border border-line">
              <table className="w-full text-left text-[13px]">
                <thead className="sticky top-0 bg-surface text-ink-500"><tr><th className="px-3 py-2">PRN</th><th className="px-3 py-2">Name</th><th className="px-3 py-2">Class</th><th className="px-3 py-2">Email</th></tr></thead>
                <tbody className="divide-y divide-line">
                  {parsed.rows.slice(0, 50).map((r) => (
                    <tr key={r.prn} className={existing.has(r.prn) ? 'text-ink-400 line-through' : ''}>
                      <td className="px-3 py-1.5 tabular-nums">{r.prn}</td><td className="px-3 py-1.5">{r.name}</td>
                      <td className="px-3 py-1.5">{CLASSES[r.classKey].short}</td><td className="px-3 py-1.5">{r.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </Dialog>
  );
}
