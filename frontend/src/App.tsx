import type { ReactNode } from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import type { Role } from './types';
import { AppProvider, useApp } from './store/AppStore';
import { ToastProvider } from './components/Toast';
import { AppLayout, ROLE_HOME } from './components/Shell';
import Login from './pages/auth/Login';
import Today from './pages/faculty/Today';
import FacultyTimetable from './pages/faculty/Timetable';
import History from './pages/faculty/History';
import Corrections from './pages/faculty/Corrections';
import MarkAttendance from './pages/faculty/MarkAttendance';
import Dashboard from './pages/hod/Dashboard';
import Approvals from './pages/hod/Approvals';
import Reports from './pages/shared/Reports';
import Students from './pages/admin/Students';
import TimetableSetup from './pages/admin/TimetableSetup';
import AuditLog from './pages/admin/AuditLog';

/** Signed-out users go to /login; a signed-in user on another role's URL goes to their own home. */
function RequireRole({ role, children }: { role: Role; children: ReactNode }) {
  const { role: current } = useApp();
  if (!current) return <Navigate to="/login" replace />;
  if (current !== role) return <Navigate to={ROLE_HOME[current]} replace />;
  return <>{children}</>;
}

function Home() {
  const { role } = useApp();
  return <Navigate to={role ? ROLE_HOME[role] : '/login'} replace />;
}

export default function App() {
  return (
    // Hash routing works on any static host (Apache/PHP shared hosting) with no rewrite rules.
    <HashRouter>
      <AppProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/faculty" element={<RequireRole role="faculty"><AppLayout key="faculty" role="faculty" /></RequireRole>}>
              <Route index element={<Today />} />
              <Route path="timetable" element={<FacultyTimetable />} />
              <Route path="history" element={<History />} />
              <Route path="corrections" element={<Corrections />} />
              <Route path="session/:id" element={<MarkAttendance />} />
            </Route>
            <Route path="/hod" element={<RequireRole role="hod"><AppLayout key="hod" role="hod" /></RequireRole>}>
              <Route index element={<Dashboard />} />
              <Route path="approvals" element={<Approvals />} />
              <Route path="reports" element={<Reports />} />
            </Route>
            <Route path="/admin" element={<RequireRole role="admin"><AppLayout key="admin" role="admin" /></RequireRole>}>
              <Route index element={<Students />} />
              <Route path="timetable" element={<TimetableSetup />} />
              <Route path="reports" element={<Reports />} />
              <Route path="audit" element={<AuditLog />} />
            </Route>
            <Route path="*" element={<Home />} />
          </Routes>
        </ToastProvider>
      </AppProvider>
    </HashRouter>
  );
}
