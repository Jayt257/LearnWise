/
  src/App.jsx
  Main routing configuration.
  Now includes: ThemeProvider init, StarField background,
  constellation cursor-trail (dark mode only), scroll-progress bar.
  Zero routing / logic changes.
 /
import React, { useEffect, useRef, useCallback } from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import AdminRoute    from './components/AdminRoute.jsx';
import Sidebar       from './components/Sidebar.jsx';
import NebulaWeb     from './components/NebulaWeb.jsx';
import { useTheme }  from './hooks/useTheme.js';

// Auth Pages
import LoginPage      from './pages/auth/LoginPage.jsx';
import RegisterPage   from './pages/auth/RegisterPage.jsx';
import AdminLoginPage from './pages/admin/AdminLoginPage.jsx';

// Core Pages
import OnboardingPage from './pages/onboarding/OnboardingPage.jsx';
import DashboardPage  from './pages/dashboard/DashboardPage.jsx';
import ActivityRouter from './pages/activities/ActivityRouter.jsx';

// Social Pages
import LeaderboardPage   from './pages/social/LeaderboardPage.jsx';
import ProfilePage       from './pages/social/ProfilePage.jsx';
import SearchFriendsPage from './pages/social/SearchFriendsPage.jsx';

// Admin Page
import AdminDashboard from './pages/admin/AdminDashboard.jsx';

/ ── Scroll progress bar ───────────────────────────────────── /
function ScrollProgressBar() {
  const barRef = useRef(null);

  useEffect(() => {
    const onScroll = () => {
      const doc   = document.documentElement;
      const total = doc.scrollHeight - doc.clientHeight;
      const pct   = total >  ? (window.scrollY / total)   : ;
      if (barRef.current) barRef.current.style.width = `${pct}%`;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return <div ref={barRef} className="scroll-progress" aria-hidden="true" />;
}

/ ── Layout with sidebar ───────────────────────────────────── /
const MainLayout = () => (
  <div className="app-shell">
    <Sidebar />
    <main className="main-content">
      <div style={{ maxWidth: , margin: ' auto', width: '%' }}>
        <Outlet />
      </div>
    </main>
  </div>
);

/ ── Root App ──────────────────────────────────────────────── /
export default function App() {
  const { isDark } = useTheme();

  return (
    <>
      {/ Global backgrounds /}
      {isDark && <NebulaWeb />}
      <ScrollProgressBar />

      <Routes>
        {/ Public Routes /}
        <Route path="/"              element={<Navigate to="/login" replace />} />
        <Route path="/login"         element={<LoginPage />} />
        <Route path="/register"      element={<RegisterPage />} />
        <Route path="/admin/login"   element={<AdminLoginPage />} />

        {/ Protected Routes (requires User role) /}
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/onboarding"              element={<OnboardingPage />} />
          <Route path="/dashboard"               element={<DashboardPage />} />
          <Route path="/activity/:pairId/:type"  element={<ActivityRouter />} />
          <Route path="/leaderboard"             element={<LeaderboardPage />} />
          <Route path="/profile"                 element={<ProfilePage />} />
          <Route path="/search"                  element={<SearchFriendsPage />} />
        </Route>

        {/ Admin Routes /}
        <Route element={<AdminRoute><Outlet /></AdminRoute>}>
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>

        {/ Fallback /}
        <Route path="" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  );
}
