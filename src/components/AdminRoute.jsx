/**
 * src/components/AdminRoute.jsx
 * Only allows admin users; redirects others to /dashboard.
 */
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

export default function AdminRoute({ children }) {
  const { isAuthenticated, user } = useSelector(s => s.auth);
  if (!isAuthenticated) return <Navigate to="/admin/login" replace />;
  if (user?.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
}
