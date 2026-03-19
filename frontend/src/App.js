import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Result, Button } from 'antd';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Inventory from './pages/Inventory';
import Customers from './pages/Customers';
import Forecast from './pages/Forecast';
import Anomaly from './pages/Anomaly';
import Chatbot from './pages/Chatbot';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import Settings from './pages/Settings';
import { useAuthStore } from './store/authStore';

function RoleGuard({ children, allowedRoles }) {
  const { user } = useAuthStore();
  if (!allowedRoles.includes(user?.role)) {
    return (
      <Result
        status="403"
        title="Access Denied"
        subTitle="You do not have permission to view this page."
        extra={
          <Button type="primary" onClick={() => window.history.back()}>
            Go Back
          </Button>
        }
      />
    );
  }
  return children;
}

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
        },
      }}
    >
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {isAuthenticated ? (
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" />} />

            {/* All roles */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/sales"     element={<Sales />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/chatbot"   element={<Chatbot />} />

            {/* Admin + Analyst only */}
            <Route path="/customers" element={
              <RoleGuard allowedRoles={['admin', 'analyst']}>
                <Customers />
              </RoleGuard>
            } />
            <Route path="/forecast" element={
              <RoleGuard allowedRoles={['admin', 'analyst']}>
                <Forecast />
              </RoleGuard>
            } />
            <Route path="/anomaly" element={
              <RoleGuard allowedRoles={['admin', 'analyst']}>
                <Anomaly />
              </RoleGuard>
            } />

            {/* Admin only */}
            <Route path="/settings" element={
              <RoleGuard allowedRoles={['admin']}>
                <Settings />
              </RoleGuard>
            } />

            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" />} />
        )}
      </Routes>
    </ConfigProvider>
  );
}

export default App;