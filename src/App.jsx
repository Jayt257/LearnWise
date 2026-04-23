/**
 * src/App.jsx
 * Main routing configuration. Wraps pages in Sidebar and Auth guards.
 */
import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import AdminRoute from './components/AdminRoute.jsx';
import Sidebar from './components/Sidebar.jsx';

// Auth Pages
import LoginPage from './pages/auth/LoginPage.jsx';
import RegisterPage from './pages/auth/RegisterPage.jsx';
import AdminLoginPage from './pages/admin/AdminLoginPage.jsx';

// Core Pages
import OnboardingPage from './pages/onboarding/OnboardingPage.jsx';
import DashboardPage from './pages/dashboard/DashboardPage.jsx';
import ActivityRouter from './pages/activities/ActivityRouter.jsx';

// Social Pages
import LeaderboardPage from './pages/social/LeaderboardPage.jsx';
import ProfilePage from './pages/social/ProfilePage.jsx';
import SearchFriendsPage from './pages/social/SearchFriendsPage.jsx';

// Admin Page
import AdminDashboard from './pages/admin/AdminDashboard.jsx';

import NebulaWeb from './components/NebulaWeb.jsx';
import { useTheme } from './hooks/useTheme.js';

// Layout component with sidebar
const MainLayout = () => {
  useTheme(); // ensure data-theme is applied on <html>
  return (
    <div className="app-shell">
      <NebulaWeb />
      <Sidebar />
      <main className="main-content">
        <div style={{ maxWidth: 1000, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />

      {/* Protected Routes (requires User role) */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/activity/:pairId/:type" element={<ActivityRouter />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/search" element={<SearchFriendsPage />} />
      </Route>

      {/* Admin Routes (requires Admin role) */}
      <Route element={<AdminRoute><Outlet /></AdminRoute>}>
        <Route path="/admin" element={<AdminDashboard />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
