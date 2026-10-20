import { useEffect, useRef, useState, type ClipboardEvent, type FormEvent, type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Check } from 'lucide-react';
import type { Role } from '../../types';
import { COLLEGE, PEOPLE } from '../../data/catalog';
import { useApp } from '../../store/AppStore';
import { ROLE_HOME } from '../../components/Shell';
import { Banner, Button, Field, Input, Logo } from '../../components/ui';
import { cn } from '../../lib/format';

type Step = 'email' | 'otp' | 'done';

export default function Login() {
  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('s.patil@gcoek.ac.in');
  const [emailError, setEmailError] = useState('');
  const [digits, setDigits] = useState<string[]>(Array(6).fill(''));
  const [attempts, setAttempts] = useState(3);
  const [otpError, setOtpError] = useState('');
  const [resendIn, setResendIn] = useState(0);
  const boxes = useRef<(HTMLInputElement | null)[]>([]);
  const { signIn } = useApp();
  const navigate = useNavigate();

  const person = Object.values(PEOPLE).find((p) => p.email === email.trim().toLowerCase());
  const displayName = person?.name ?? email.split('@')[0];

  useEffect(() => {
    if (resendIn <= 0) return;
    const t = setTimeout(() => setResendIn((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [resendIn]);

  const sendCode = (e: FormEvent) => {
    e.preventDefault();
    const v = email.trim().toLowerCase();
    if (!/^[^@\s]+@gcoek\.ac\.in$/.test(v)) {
      setEmailError(`Use your @${COLLEGE.emailDomain} college email.`);
      return;
    }
    setEmailError('');
    setDigits(Array(6).fill(''));
    setOtpError('');
    setAttempts(3);
    setResendIn(42);
    setStep('otp');
    setTimeout(() => boxes.current[0]?.focus(), 0);
  };

  const verify = (e?: FormEvent) => {
    e?.preventDefault();
    const code = digits.join('');
    if (code.length < 6) {
      setOtpError('Enter all 6 digits.');
      return;
    }
    // Prototype: any code except 000000 is accepted. The server checks a salted hash, 10-minute expiry, 3 attempts.
    if (code === '000000') {
      const left = attempts - 1;
      setAttempts(left);
      setDigits(Array(6).fill(''));
      boxes.current[0]?.focus();
      setOtpError(left > 0 ? `Incorrect code. ${left} attempt${left > 1 ? 's' : ''} left.` : 'Too many wrong codes. Sign-in locked for 15 minutes.');
      return;
    }
    setStep('done');
  };

  const setDigit = (i: number, v: string) => {
    const d = v.replace(/\D/g, '').slice(-1);
    setDigits((prev) => prev.map((x, j) => (j === i ? d : x)));
    setOtpError('');
    if (d && i < 5) boxes.current[i + 1]?.focus();
  };
  const onKey = (i: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[i] && i > 0) boxes.current[i - 1]?.focus();
    if (e.key === 'ArrowLeft' && i > 0) boxes.current[i - 1]?.focus();
    if (e.key === 'ArrowRight' && i < 5) boxes.current[i + 1]?.focus();
  };
  const onPaste = (e: ClipboardEvent) => {
    const code = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!code) return;
    e.preventDefault();
    setDigits(Array.from({ length: 6 }, (_, i) => code[i] ?? ''));
    boxes.current[Math.min(code.length, 5)]?.focus();
  };

  const go = (role: Role) => {
    signIn(role);
    navigate(ROLE_HOME[role]);
  };
  const locked = attempts <= 0;
  const defaultRole: Role = person?.role ?? 'faculty';
  const others = (['faculty', 'hod', 'admin'] as Role[]).filter((r) => r !== defaultRole);
  const label = (r: Role) => (r === 'faculty' ? 'Faculty' : r === 'hod' ? 'HOD' : 'Admin');

  return (
    <div className="flex min-h-screen flex-col bg-surface md:flex-row">
      {/* Brand panel */}
      <section className="flex flex-col justify-between bg-navy px-6 py-6 text-white md:w-1/2 md:px-12 md:py-12">
        <div className="flex items-center gap-4">
          <Logo size={56} light />
          <div>
            <div className="text-[15px] font-semibold sm:text-base">{COLLEGE.name}</div>
            <div className="text-[13px] text-white/80">{COLLEGE.affiliation}</div>
          </div>
        </div>
        <div className="mt-8 max-w-md md:mt-0">
          <h1 className="text-[28px] font-bold leading-tight md:text-[40px] md:leading-[1.15]">Attendance Management System</h1>
          <p className="mt-4 hidden text-base text-white/85 md:block">
            For faculty, Heads of Department and administrators. Students receive attendance alerts by email and do not sign in.
          </p>
        </div>
        <p className="hidden text-[13px] text-white/75 md:block">Every sign-in is recorded in the audit log.</p>
      </section>

      {/* Form panel */}
      <section className="flex flex-1 items-start justify-center px-4 py-8 md:items-center md:py-12">
        <div className="w-full max-w-[400px] rounded-lg border border-line bg-white p-6 sm:p-8">
          {step === 'email' && (
            <form onSubmit={sendCode} noValidate>
              <h2 className="text-xl font-semibold text-ink-900">Sign in</h2>
              <p className="mt-1 text-sm text-ink-700">We'll email a 6-digit code to your college address.</p>
              <Field label="College email" error={emailError} className="mt-6">
                {(id) => (
                  <Input id={id} type="email" autoComplete="email" inputMode="email" value={email} invalid={!!emailError}
                    onChange={(e) => setEmail(e.target.value)} placeholder={`name@${COLLEGE.emailDomain}`} />
                )}
              </Field>
              <Button type="submit" variant="primary" size="lg" block className="mt-5">Send code</Button>
              <p className="mt-4 text-[13px] text-ink-500">Students don't sign in — they get attendance alerts by email.</p>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={verify} noValidate>
              <h2 className="text-xl font-semibold text-ink-900">Enter the code</h2>
              <p className="mt-1 text-sm text-ink-700">Sent to <span className="font-medium text-ink-900">{email}</span> · expires in 10 min</p>
              <div className="mt-6 flex gap-2" onPaste={onPaste}>
                {digits.map((d, i) => (
                  <input
                    key={i}
                    ref={(el) => (boxes.current[i] = el)}
                    value={d}
                    disabled={locked}
                    onChange={(e) => setDigit(i, e.target.value)}
                    onKeyDown={(e) => onKey(i, e)}
                    inputMode="numeric"
                    autoComplete={i === 0 ? 'one-time-code' : 'off'}
                    aria-label={`Digit ${i + 1}`}
                    className={cn('h-14 w-full min-w-0 rounded-md border bg-white text-center text-xl font-semibold text-ink-900 focus:outline-none focus:ring-2',
                      otpError ? 'border-bad-dot focus:ring-bad-dot/20' : 'border-line focus:border-accent focus:ring-accent/20')}
                  />
                ))}
              </div>
              {otpError && (
                <div className="mt-4">
                  <Banner tone="red" icon={<AlertCircle className="h-4 w-4" />}>{otpError}</Banner>
                </div>
              )}
              <Button type="submit" variant="primary" size="lg" block className="mt-5" disabled={locked}>Verify and sign in</Button>
              <div className="mt-4 flex items-center justify-between">
                <Button variant="link" onClick={() => setStep('email')}>Use a different email</Button>
                <Button size="sm" variant={resendIn > 0 ? 'ghost' : 'secondary'} disabled={resendIn > 0 || locked}
                  onClick={() => { setResendIn(42); setDigits(Array(6).fill('')); }}>
                  {resendIn > 0 ? `Resend in 0:${String(resendIn).padStart(2, '0')}` : 'Resend code'}
                </Button>
              </div>
              <p className="mt-4 rounded bg-surface px-3 py-2 text-[13px] text-ink-500">Prototype: any 6 digits sign you in. 000000 shows the wrong-code state.</p>
            </form>
          )}

          {step === 'done' && (
            <div>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-ok-fill text-ok-text"><Check className="h-6 w-6" /></div>
              <h2 className="mt-5 text-xl font-semibold text-ink-900">Signed in</h2>
              <p className="mt-1 text-sm text-ink-700">Welcome, {displayName}. Choose a role to preview.</p>
              <Button variant="primary" size="lg" block className="mt-6" onClick={() => go(defaultRole)}>Continue as {label(defaultRole)}</Button>
              <div className="mt-3 grid grid-cols-2 gap-2">
                {others.map((r) => <Button key={r} size="lg" onClick={() => go(r)}>As {label(r)}</Button>)}
              </div>
            </div>
          )}
        </div>
      </section>
      <p className="px-4 pb-6 text-center text-[13px] text-ink-500 md:hidden">Every sign-in is recorded in the audit log.</p>
    </div>
  );
}
