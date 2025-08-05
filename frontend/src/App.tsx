import React from 'react';
import { Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import NewOrderPage from './pages/NewOrderPage';
import CheckoutPage from './pages/CheckoutPage';
import Dashboard from './pages/Dashboard';
import OrderDetailPage from './pages/OrderDetailPage';
import BlogPage from './pages/BlogPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ProfilePage from './pages/ProfilePage';
import AppLayout from './pages/AppLayout';
import { useAuthStore } from './store/useAuthStore';
import { ReactNode } from 'react';

interface ProtectedRouteProps {
  children?: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = useAuthStore((state) => state.token);
  const location = useLocation();

  if (!token) {
    const redirectUrl = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${redirectUrl}`} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
}


export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/cadastro" element={<RegisterPage />} />
      <Route path="/esqueci-senha" element={<ForgotPasswordPage />} />
      <Route path="/redefinir-senha/:token" element={<ResetPasswordPage />} />
      <Route path="/novo-pedido" element={<ProtectedRoute><NewOrderPage /></ProtectedRoute>} />
      <Route path="/checkout/:orderId" element={<ProtectedRoute><CheckoutPage /></ProtectedRoute>} />
      <Route path="/blog" element={<BlogPage />} />
      <Route path="/app" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="pedidos/:orderId" element={<OrderDetailPage />} />
        <Route path="perfil" element={<ProfilePage />} />
      </Route>
    </Routes>
  );
}
