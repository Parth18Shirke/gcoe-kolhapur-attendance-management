import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Download } from 'lucide-react';
import type { ClassKey, Student } from '../../types';
import { CLASSES, CLASS_KEYS, COLLEGE, NOW, PEOPLE, REPORTED_SUBJECTS, ROLE_USER, SUBJECT_TEACHER, THRESHOLD } from '../../data/catalog';
import { subjectName, useApp } from '../../store/AppStore';
import { Page } from '../../components/Shell';
import { Button, Card, Field, Input, Logo, PageHeader, Select } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { cn, downloadFile, fmtDate, fmtStamp, toCsv, toIsoDateTime } from '../../lib/format';

type ReportType = 'subject' | 'student' | 'defaulter';
type Year = 'SY' | 'TY' | 'BT';

const TYPES: { value: ReportType; title: string; sub: string }[] = [
  { value: 'subject', title: 'Subject-wise', sub: 'One subject · attended / conducted' },
  { value: 'student', title: 'Student-wise', sub: 'Every subject per student + overall' },
  { value: 'defaulter', title: 'Defaulter list', sub: 'Only students below 75%' },
];
const ROWS_PER_PAGE = 20;

interface Report {
  title: string;
  subtitle: string;
  meta: { label: string; value: string }[];
  head: string[];
  numericFrom: number; // columns from this index are right-aligned
  rows: { cells: string[]; low: boolean }[];
  summary: { label: string; value: string; red?: boolean }[];
  signatures: { name: string; role: string }[];
  fileBase: string;
}

export default function Reports() {
  const { role, students, stats, log } = useApp();
  const toast = useToast();
  const [params] = useSearchParams();
  const initialType = (TYPES.some((t) => t.value === params.get('type')) ? params.get('type') : 'subject') as ReportType;
  const [type, setType] = useState<ReportType>(initialType);
  const [year, setYear] = useState<Year | 'all'>(initialType === 'defaulter' ? 'all' : 'TY');
  const [div, setDiv] = useState<'A' | 'B' | 'all'>(initialType === 'defaulter' ? 'all' : 'A');
  const [subject, setSubject] = useState('CS601');
  const [from, setFrom] = useState(COLLEGE.termStart);
  const [to, setTo] = useState('2026-10-20');
  const [page, setPage] = useState(0);

  // Subject-wise and student-wise reports are per division.
  const needsClass = type !== 'defaulter';
  const effYear: Year = year === 'all' ? 'TY' : year;
  const effDiv = div === 'all' ? 'A' : div;
  useEffect(() => {
    if (!REPORTED_SUBJECTS[effYear].some((s) => s.code === subject)) setSubject(REPORTED_SUBJECTS[effYear][0].code);
  }, [effYear, subject]);
  useEffect(() => { setPage(0); }, [type, year, div, subject]);

  const user = ROLE_USER[role ?? 'hod'];
  const dateError = from > to ? 'From must be on or before To.' : '';
  const period = `${fmtDate(from)} – ${fmtDate(to)}`;

  const report: Report = useMemo(() => {
    const classKey = `${effYear}-${effDiv}` as ClassKey;
    const roster = (k: ClassKey) => students.filter((s) => s.classKey === k && s.status === 'Active' && stats[s.prn]).sort((a, b) => a.prn.localeCompare(b.prn));
    const avg = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
    const common = [
      { name: PEOPLE.hod.name, role: 'Head of Department' },
      { name: '[PRINCIPAL NAME]', role: 'Principal' },
    ];

    if (type === 'subject') {
      const list = roster(classKey);
      const sub = REPORTED_SUBJECTS[effYear].find((s) => s.code === subject) ?? REPORTED_SUBJECTS[effYear][0];
      const pcts = list.map((s) => stats[s.prn].subjects.find((x) => x.code === sub.code)!);
      const below = pcts.filter((p) => p.pct < THRESHOLD).length;
      const teacher = PEOPLE[SUBJECT_TEACHER[sub.code]];
      return {
        title: 'Subject-wise attendance report',
        subtitle: `${subjectName(sub.code)} (${sub.code}) · ${teacher.name}`,
        meta: [
          { label: 'Class', value: CLASSES[classKey].label },
          { label: 'Semester', value: `${CLASSES[classKey].sem} · 2026–27` },
          { label: 'Period', value: period },
          { label: 'Lectures conducted', value: String(sub.conducted) },
        ],
        head: ['Sr', 'PRN', 'Name', 'Attended / Conducted', '%'],
        numericFrom: 3,
        rows: list.map((s, i) => {
          const p = pcts[i];
          return { cells: [String(i + 1), s.prn, s.name, `${p.attended} / ${p.conducted}`, `${p.pct.toFixed(1)}${p.pct < THRESHOLD ? ' *' : ''}`], low: p.pct < THRESHOLD };
        }),
        summary: [
          { label: 'Students', value: String(list.length) },
          { label: 'Class average', value: `${avg(pcts.map((p) => p.pct)).toFixed(1)}%` },
          { label: 'Below 75%', value: String(below), red: below > 0 },
          { label: 'Lowest', value: `${Math.min(...pcts.map((p) => p.pct)).toFixed(1)}%` },
        ],
        signatures: [{ name: teacher.name, role: 'Subject Teacher' }, ...common],
        fileBase: `Subject-wise_${sub.code}_${CLASSES[classKey].short.replace(' ', '')}`,
      };
    }

    if (type === 'student') {
      const list = roster(classKey);
      const subs = REPORTED_SUBJECTS[effYear];
      const below = list.filter((s) => stats[s.prn].pct < THRESHOLD).length;
      return {
        title: 'Student-wise attendance report',
        subtitle: `All theory subjects · ${CLASSES[classKey].label}`,
        meta: [
          { label: 'Class', value: CLASSES[classKey].label },
          { label: 'Semester', value: `${CLASSES[classKey].sem} · 2026–27` },
          { label: 'Period', value: period },
          { label: 'Subjects', value: subs.map((s) => s.code).join(', ') },
        ],
        head: ['Sr', 'PRN', 'Name', ...subs.map((s) => s.code), 'Overall %'],
        numericFrom: 3,
        rows: list.map((s, i) => {
          const st = stats[s.prn];
          return {
            cells: [String(i + 1), s.prn, s.name, ...st.subjects.map((x) => `${x.pct.toFixed(0)}${x.pct < THRESHOLD ? '*' : ''}`), `${st.pct.toFixed(1)}${st.pct < THRESHOLD ? ' *' : ''}`],
            low: st.pct < THRESHOLD,
          };
        }),
        summary: [
          { label: 'Students', value: String(list.length) },
          { label: 'Class average', value: `${avg(list.map((s) => stats[s.prn].pct)).toFixed(1)}%` },
          { label: 'Below 75%', value: String(below), red: below > 0 },
          { label: 'Lowest', value: `${Math.min(...list.map((s) => stats[s.prn].pct)).toFixed(1)}%` },
        ],
        signatures: [{ name: '', role: 'Class Coordinator' }, ...common],
        fileBase: `Student-wise_${CLASSES[classKey].short.replace(' ', '')}`,
      };
    }

    const keys = CLASS_KEYS.filter((k) => (year === 'all' || CLASSES[k].year === year) && (div === 'all' || CLASSES[k].div === div));
    const list: Student[] = keys.flatMap(roster).filter((s) => stats[s.prn].pct < THRESHOLD).sort((a, b) => stats[a.prn].pct - stats[b.prn].pct);
    const total = keys.flatMap(roster).length;
    const scope = year === 'all' ? 'All years' : keys.length === 1 ? CLASSES[keys[0]].label : `${year === 'BT' ? 'BTech' : year} CSE — all divisions`;
    return {
      title: 'Defaulter list — attendance below 75%',
      subtitle: `${scope} · for the Principal's office`,
      meta: [
        { label: 'Scope', value: scope },
        { label: 'Semester', value: 'Odd · 2026–27' },
        { label: 'Period', value: period },
        { label: 'Threshold', value: 'Below 75.00%' },
      ],
      head: ['Sr', 'PRN', 'Name', 'Class', 'Attended / Conducted', 'Overall %'],
      numericFrom: 4,
      rows: list.map((s, i) => {
        const st = stats[s.prn];
        return { cells: [String(i + 1), s.prn, s.name, CLASSES[s.classKey].label, `${st.attended} / ${st.conducted}`, `${st.pct.toFixed(1)} *`], low: true };
      }),
      summary: [
        { label: 'Students in scope', value: String(total) },
        { label: 'Defaulters', value: String(list.length), red: list.length > 0 },
        { label: 'Share', value: `${total ? ((list.length / total) * 100).toFixed(1) : '0.0'}%` },
        { label: 'Lowest', value: list.length ? `${stats[list[0].prn].pct.toFixed(1)}%` : '—' },
      ],
      signatures: [{ name: '', role: 'Class Coordinator' }, ...common],
      fileBase: `Defaulters_${scope.replace(/[^A-Za-z0-9]+/g, '_')}`,
    };
  }, [type, effYear, effDiv, year, div, subject, students, stats, period]);

  const pages = Math.max(1, Math.ceil(report.rows.length / ROWS_PER_PAGE));
  const generated = `Generated by AMS on ${fmtStamp(toIsoDateTime(NOW)).replace(/:\d\d$/, '')} · ${user.name}`;

  const exportCsv = () => {
    downloadFile(`${report.fileBase}.csv`, toCsv([report.head, ...report.rows.map((r) => r.cells)]), 'text/csv;charset=utf-8');
    log('Report exported (CSV)', `${report.title} · ${report.meta[0].value}`, '—', `CSV, ${report.rows.length} rows`);
    toast('CSV downloaded. The export is in the audit trail.');
  };
  const exportPdf = () => {
    log('Report exported (PDF)', `${report.title} · ${report.meta[0].value}`, '—', `PDF, ${report.rows.length} rows`);
    window.print();
  };
  const exportWord = () => {
    downloadFile(`${report.fileBase}.doc`, wordHtml(report, generated), 'application/msword');
    log('Report exported (Word)', `${report.title} · ${report.meta[0].value}`, '—', `Word, ${report.rows.length} rows`);
    toast('Word document downloaded.');
  };

  return (
    <Page>
      <div className="no-print">
        <PageHeader
          title="Reports"
          subtitle="Preview updates as you change filters. Exports are logged in the audit trail."
          actions={<>
            <Button variant="primary" onClick={exportPdf} disabled={!!dateError}><Download className="h-4 w-4" />PDF (A4)</Button>
            <Button onClick={exportWord} disabled={!!dateError}>Word</Button>
            <Button onClick={exportCsv} disabled={!!dateError}>CSV</Button>
          </>}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <Card className="no-print h-fit space-y-5 p-5">
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-ink-900">Report type</legend>
            <div className="space-y-2">
              {TYPES.map((t) => (
                <label key={t.value} className={cn('flex cursor-pointer items-start gap-3 rounded-md border px-3 py-2.5',
                  type === t.value ? 'border-accent bg-accent-soft ring-1 ring-accent' : 'border-line hover:bg-surface')}>
                  <input type="radio" name="rtype" value={t.value} checked={type === t.value} className="mt-1 h-4 w-4 accent-accent"
                    onChange={() => {
                      setType(t.value);
                      if (t.value !== 'defaulter') { if (year === 'all') setYear('TY'); if (div === 'all') setDiv('A'); }
                    }} />
                  <span>
                    <span className="block text-[15px] font-medium text-ink-900">{t.title}</span>
                    <span className="block text-[13px] text-ink-500">{t.sub}</span>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <Field label="Department">
            {(id) => <Select id={id} disabled={role !== 'admin'}><option>{COLLEGE.department}</option></Select>}
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Program">{(id) => <Select id={id}><option>B.Tech</option></Select>}</Field>
            <Field label="Semester">
              {(id) => (
                <Select id={id} value={needsClass ? effYear : year} onChange={(e) => setYear(e.target.value as Year | 'all')}>
                  {!needsClass && <option value="all">All</option>}
                  <option value="SY">III (SY)</option>
                  <option value="TY">V (TY)</option>
                  <option value="BT">VII (BTech)</option>
                </Select>
              )}
            </Field>
          </div>
          <Field label="Division">
            {(id) => (
              <Select id={id} value={needsClass ? effDiv : div} onChange={(e) => setDiv(e.target.value as 'A' | 'B' | 'all')}>
                {!needsClass && <option value="all">All divisions</option>}
                <option value="A">Div A</option>
                <option value="B">Div B</option>
              </Select>
            )}
          </Field>
          {type === 'subject' && (
            <Field label="Subject">
              {(id) => (
                <Select id={id} value={subject} onChange={(e) => setSubject(e.target.value)}>
                  {REPORTED_SUBJECTS[effYear].map((s) => <option key={s.code} value={s.code}>{s.code} · {subjectName(s.code)}</option>)}
                </Select>
              )}
            </Field>
          )}
          <div className="grid grid-cols-2 gap-3">
            <Field label="From" error={dateError}>{(id) => <Input id={id} type="date" value={from} min={COLLEGE.termStart} onChange={(e) => setFrom(e.target.value)} invalid={!!dateError} />}</Field>
            <Field label="To">{(id) => <Input id={id} type="date" value={to} onChange={(e) => setTo(e.target.value)} />}</Field>
          </div>
          <p className="text-[13px] text-ink-500">Full PRNs appear on reports. Students marked Inactive or Archived are excluded unless they attended in the range.</p>
        </Card>

        <div className="min-w-0">
          <div className="no-print mb-3 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wide text-ink-500">Preview · A4 portrait · page {page + 1}</span>
            {pages > 1 && (
              <div className="flex items-center gap-1">
                <Button size="sm" aria-label="Previous page" disabled={page === 0} onClick={() => setPage(page - 1)}><ChevronLeft className="h-4 w-4" /></Button>
                <span className="px-2 text-[13px] tabular-nums text-ink-700">{page + 1} / {pages}</span>
                <Button size="sm" aria-label="Next page" disabled={page === pages - 1} onClick={() => setPage(page + 1)}><ChevronRight className="h-4 w-4" /></Button>
              </div>
            )}
          </div>
          <div className="print-area overflow-x-auto">
            {Array.from({ length: pages }, (_, i) => (
              <A4Page key={i} report={report} index={i} pages={pages} generated={generated} className={i === page ? '' : 'hidden print:block'} />
            ))}
          </div>
        </div>
      </div>
    </Page>
  );
}

function A4Page({ report: r, index, pages, generated, className }: { report: Report; index: number; pages: number; generated: string; className?: string }) {
  const rows = r.rows.slice(index * ROWS_PER_PAGE, (index + 1) * ROWS_PER_PAGE);
  const last = index === pages - 1;
  return (
    <div className={cn('a4-page mx-auto flex min-h-[1000px] w-[720px] flex-col bg-white px-11 py-10 text-ink-900 shadow-raised', className)}>
      <div className="flex items-center gap-6 border-b-2 border-ink-900 pb-4">
        <Logo size={56} />
        <div className="flex-1 text-center">
          <div className="text-[17px] font-semibold text-navy">{COLLEGE.name}</div>
          <div className="text-[11px] text-ink-700">{COLLEGE.affiliationShort}</div>
          <div className="text-[12px] font-semibold">Department of {COLLEGE.department}</div>
        </div>
        <div className="w-14" />
      </div>
      <div className="mt-5 text-center">
        <div className="text-[15px] font-bold uppercase tracking-wide">{r.title}</div>
        <div className="text-[12px] text-ink-700">{r.subtitle}</div>
      </div>
      {index === 0 && (
        <div className="mt-4 grid grid-cols-4 border border-line text-[11px]">
          {r.meta.map((m) => (
            <div key={m.label} className="border-r border-line px-2 py-1.5 last:border-r-0">
              <div className="text-[9px] uppercase tracking-wide text-ink-500">{m.label}</div>
              <div className="font-medium">{m.value}</div>
            </div>
          ))}
        </div>
      )}
      <table className="mt-4 w-full border-collapse text-[11px]">
        <thead>
          <tr className="bg-info-fill">
            {r.head.map((h, i) => <th key={h} className={cn('border border-line px-2 py-1 font-semibold', i >= r.numericFrom ? 'text-right' : 'text-left')}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.cells[0]}>
              {row.cells.map((c, i) => (
                <td key={i} className={cn('border border-line px-2 py-[3px]', i >= r.numericFrom && 'text-right tabular-nums',
                  i === row.cells.length - 1 && 'font-semibold', row.low && i === row.cells.length - 1 && 'text-bad-text')}>{c}</td>
              ))}
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={r.head.length} className="border border-line px-2 py-6 text-center text-ink-500">No students in this report.</td></tr>}
        </tbody>
      </table>
      {!last && <p className="mt-2 text-[10px] text-ink-500">{r.rows.length - (index + 1) * ROWS_PER_PAGE} more rows continue on the next page.</p>}
      {last && (
        <>
          <p className="mt-2 text-[10px] text-ink-500">Percentages below 75% (statutory minimum) are shown in red and marked *.</p>
          <div className="mt-4 grid grid-cols-4 gap-2">
            {r.summary.map((s) => (
              <div key={s.label} className="border border-line px-2.5 py-2">
                <div className="text-[9px] uppercase tracking-wide text-ink-500">{s.label}</div>
                <div className={cn('text-[15px] font-semibold', s.red && 'text-bad-text')}>{s.value}</div>
              </div>
            ))}
          </div>
          <div className="mt-auto grid grid-cols-3 gap-6 pt-16 text-center text-[11px]">
            {r.signatures.map((s) => (
              <div key={s.role} className="border-t border-ink-700 pt-1.5">
                <div className="min-h-[16px] font-semibold">{s.name}</div>
                <div className="text-ink-500">{s.role}</div>
              </div>
            ))}
          </div>
        </>
      )}
      <div className={cn('flex justify-between border-t border-line pt-2 text-[9px] text-ink-500', last ? 'mt-6' : 'mt-auto')}>
        <span>{generated}</span>
        <span>Page {index + 1} of {pages}</span>
      </div>
    </div>
  );
}

/** Word opens HTML documents saved as .doc, keeping tables and the signature block. */
function wordHtml(r: Report, generated: string) {
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return `<html><head><meta charset="utf-8"><style>
body{font-family:Calibri,Arial,sans-serif;font-size:10pt}table{border-collapse:collapse;width:100%}
td,th{border:1px solid #999;padding:2pt 4pt}th{background:#EAF0F8}.low{color:#B42318;font-weight:bold}
h1{font-size:14pt;text-align:center;color:#1E3A5F;margin:0}h2{font-size:12pt;text-align:center;margin:8pt 0 0}
.c{text-align:center}.sig td{border:none;text-align:center;padding-top:40pt}</style></head><body>
<h1>${esc(COLLEGE.name)}</h1><p class="c">${esc(COLLEGE.affiliationShort)}<br><b>Department of ${esc(COLLEGE.department)}</b></p>
<h2>${esc(r.title.toUpperCase())}</h2><p class="c">${esc(r.subtitle)}</p>
<p>${r.meta.map((m) => `<b>${esc(m.label)}:</b> ${esc(m.value)}`).join(' &nbsp; ')}</p>
<table><tr>${r.head.map((h) => `<th>${esc(h)}</th>`).join('')}</tr>
${r.rows.map((row) => `<tr>${row.cells.map((c, i) => `<td${row.low && i === row.cells.length - 1 ? ' class="low"' : ''}>${esc(c)}</td>`).join('')}</tr>`).join('\n')}
</table><p>Percentages below 75% are marked *. ${r.summary.map((s) => `${esc(s.label)}: <b>${esc(s.value)}</b>`).join(' · ')}</p>
<table class="sig"><tr>${r.signatures.map((s) => `<td>______________________<br><b>${esc(s.name)}</b><br>${esc(s.role)}</td>`).join('')}</tr></table>
<p style="font-size:8pt;color:#5B6B80">${esc(generated)}</p></body></html>`;
}
