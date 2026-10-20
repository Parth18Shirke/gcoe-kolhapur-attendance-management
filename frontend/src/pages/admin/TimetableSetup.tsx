import { useState } from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import type { ClassKey, Day, Slot, SlotType } from '../../types';
import { CLASSES, CLASS_KEYS, COLLEGE, DAYS, FACULTY_IDS, LAB_START_PERIODS, PEOPLE, PERIODS, ROOMS, SUBJECTS } from '../../data/catalog';
import { subjectName, useApp } from '../../store/AppStore';
import { findClashes, span, type Clash } from '../../lib/schedule';
import { Page } from '../../components/Shell';
import { Banner, Button, Card, Field, PageHeader, Select, Textarea } from '../../components/ui';
import { WeekGrid } from '../../components/WeekGrid';
import { useToast } from '../../components/Toast';
import { cn } from '../../lib/format';

const isLabSubject = (code: string) => /Lab$/.test(SUBJECTS[code]?.name ?? '');

export default function TimetableSetup() {
  const { slots, addSlot } = useApp();
  const toast = useToast();
  const [viewing, setViewing] = useState<ClassKey>('TY-A');
  const [draft, setDraft] = useState<Omit<Slot, 'id'>>({
    subject: 'CS603', facultyId: 'f-patil', classKey: 'TY-A', room: 'Room 206', day: 1, period: 0, type: 'theory',
  });
  const [clashes, setClashes] = useState<Clash[] | null>(null);
  const [override, setOverride] = useState('');
  const [overrideError, setOverrideError] = useState('');
  const [lastAdded, setLastAdded] = useState<string | null>(null);

  const set = (patch: Partial<Omit<Slot, 'id'>>) => { setDraft((d) => ({ ...d, ...patch })); setClashes(null); };
  const year = CLASSES[draft.classKey].year;
  const subjects = Object.values(SUBJECTS).filter((s) => s.classYear === year);
  const startOptions = draft.type === 'lab' ? LAB_START_PERIODS : PERIODS.map((_, i) => i);

  const classSlots = slots.filter((s) => s.classKey === viewing);
  const items = classSlots.map((s) => ({
    key: s.id, day: s.day, period: s.period, span: span(s.type),
    node: (
      <div className={cn('h-full rounded-md border p-2.5 text-[13px] leading-snug',
        s.type === 'lab' ? 'border-navy/40 bg-info-fill' : 'border-line bg-white',
        s.id === lastAdded && 'ring-2 ring-accent')}>
        <div className="text-sm font-semibold text-ink-900">{subjectName(s.subject).replace(/ Lab$/, '')}</div>
        <div className="text-ink-700">{PEOPLE[s.facultyId].name}</div>
        <div className="text-ink-700">{s.room}{s.batch && ` · ${s.batch}`}</div>
      </div>
    ),
  }));

  const check = () => {
    const found = findClashes(slots, draft);
    if (found.length === 0) save();
    else setClashes(found);
  };
  const save = (reason?: string) => {
    setLastAdded(addSlot(draft, reason));
    setViewing(draft.classKey);
    setClashes(null);
    setOverride('');
    toast(reason ? 'Slot saved with override. Logged with your reason.' : 'Slot saved. No clashes.');
  };
  const saveOverride = () => {
    if (override.trim().length < 5) { setOverrideError('Enter a reason — overrides are logged.'); return; }
    save(override.trim());
  };

  return (
    <Page>
      <PageHeader
        title="Timetable setup"
        subtitle={`Recurring weekly slots · ${COLLEGE.term} · every save is checked for faculty, room and class clashes`}
        actions={
          <label className="flex flex-col text-[13px] text-ink-500">
            Viewing class
            <Select value={viewing} onChange={(e) => setViewing(e.target.value as ClassKey)} className="mt-1 w-48">
              {CLASS_KEYS.map((k) => <option key={k} value={k}>{CLASSES[k].label}</option>)}
            </Select>
          </label>
        }
      />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <WeekGrid items={items} compactTimes minWidth={820} />

        <Card className="h-fit p-5">
          <h2 className="mb-4 text-lg font-semibold text-ink-900">New recurring slot</h2>
          <div className="space-y-4">
            <Field label="Subject">
              {(id) => (
                <Select id={id} value={draft.subject} onChange={(e) => {
                  const lab = isLabSubject(e.target.value);
                  set({ subject: e.target.value, type: lab ? 'lab' : 'theory', ...(lab ? { period: LAB_START_PERIODS.includes(draft.period) ? draft.period : 0, batch: `${CLASSES[draft.classKey].div}1` } : { batch: undefined }) });
                }}>
                  {subjects.map((s) => <option key={s.code} value={s.code}>{s.code} · {s.name}</option>)}
                </Select>
              )}
            </Field>
            <Field label="Faculty">
              {(id) => <Select id={id} value={draft.facultyId} onChange={(e) => set({ facultyId: e.target.value })}>{FACULTY_IDS.map((f) => <option key={f} value={f}>{PEOPLE[f].name}</option>)}</Select>}
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Class">
                {(id) => (
                  <Select id={id} value={draft.classKey} onChange={(e) => {
                    const k = e.target.value as ClassKey;
                    const sameYear = CLASSES[k].year === year;
                    set({ classKey: k, subject: sameYear ? draft.subject : Object.values(SUBJECTS).find((s) => s.classYear === CLASSES[k].year)!.code, batch: draft.type === 'lab' ? `${CLASSES[k].div}1` : undefined });
                  }}>
                    {CLASS_KEYS.map((k) => <option key={k} value={k}>{CLASSES[k].label}</option>)}
                  </Select>
                )}
              </Field>
              <Field label="Room">
                {(id) => <Select id={id} value={draft.room} onChange={(e) => set({ room: e.target.value })}>{ROOMS.map((r) => <option key={r}>{r}</option>)}</Select>}
              </Field>
              <Field label="Day">
                {(id) => <Select id={id} value={draft.day} onChange={(e) => set({ day: Number(e.target.value) as Day })}>{DAYS.map((d) => <option key={d.day} value={d.day}>{d.long}</option>)}</Select>}
              </Field>
              <Field label="Start">
                {(id) => <Select id={id} value={draft.period} onChange={(e) => set({ period: Number(e.target.value) })}>{startOptions.map((p) => <option key={p} value={p}>{PERIODS[p].start}</option>)}</Select>}
              </Field>
            </div>
            <div>
              <div className="mb-1.5 text-sm font-medium text-ink-900">Type</div>
              <div className="grid grid-cols-2 gap-2">
                {(['theory', 'lab'] as SlotType[]).map((t) => (
                  <button key={t} type="button" onClick={() => set({ type: t, period: t === 'lab' && !LAB_START_PERIODS.includes(draft.period) ? draft.period - 1 : draft.period, batch: t === 'lab' ? `${CLASSES[draft.classKey].div}1` : undefined })}
                    className={cn('h-10 rounded-md border text-sm font-semibold', draft.type === t ? 'border-accent bg-accent-soft text-accent ring-1 ring-accent' : 'border-line text-ink-700 hover:bg-surface')}>
                    {t === 'theory' ? 'Theory · 1 h' : 'Lab · 2 h'}
                  </button>
                ))}
              </div>
            </div>
            {draft.type === 'lab' && (
              <Field label="Batch">
                {(id) => (
                  <Select id={id} value={draft.batch} onChange={(e) => set({ batch: e.target.value })}>
                    {[1, 2].map((n) => <option key={n}>{CLASSES[draft.classKey].div}{n}</option>)}
                  </Select>
                )}
              </Field>
            )}

            {clashes && clashes.length > 0 ? (
              <div className="space-y-3">
                <Banner tone="red" icon={<AlertCircle className="h-4 w-4" />}>
                  <div className="font-semibold">{clashes.length} clash{clashes.length > 1 ? 'es' : ''} found</div>
                  <ul className="mt-1 space-y-1 text-[13px]">
                    {clashes.map((c, i) => (
                      <li key={i}>
                        <span className="font-semibold capitalize">{c.kind}:</span>{' '}
                        {c.kind === 'faculty' ? PEOPLE[c.slot.facultyId].name : c.kind === 'room' ? c.slot.room : CLASSES[c.slot.classKey].label} already has {c.slot.subject} · {CLASSES[c.slot.classKey].short} · {DAYS[c.slot.day].short} {PERIODS[c.slot.period].start}
                      </li>
                    ))}
                  </ul>
                </Banner>
                <Field label="Override reason" required error={overrideError}>
                  {(id) => <Textarea id={id} value={override} invalid={!!overrideError} onChange={(e) => { setOverride(e.target.value); setOverrideError(''); }} placeholder="e.g. Shared room agreed with Prof. More for this semester" />}
                </Field>
                <div className="grid grid-cols-2 gap-2">
                  <Button onClick={() => setClashes(null)}>Change slot</Button>
                  <Button variant="danger" onClick={saveOverride}>Save with override</Button>
                </div>
              </div>
            ) : (
              <Button variant="primary" size="lg" block onClick={check}><CheckCircle2 className="h-4 w-4" />Check &amp; save slot</Button>
            )}
            <p className="text-[13px] text-ink-500">Slots repeat weekly from 26 Oct. Changing a slot later never alters past sessions.</p>
          </div>
        </Card>
      </div>
    </Page>
  );
}
