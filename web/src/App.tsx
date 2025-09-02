import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { authService } from '@/services/auth';

// Pages
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import TicketListPage from '@/pages/TicketListPage';
import TicketDetailPage from '@/pages/TicketDetailPage';
import CreateTicketPage from '@/pages/CreateTicketPage';

// Components
import PrivateRoute from '@/components/PrivateRoute';
import MainLayout from '@/components/MainLayout';

const { Content } = Layout;

function App() {
  const isAuthenticated = authService.isAuthenticated();

  return (
    <div className="App">
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
          } 
        />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/tickets" element={<TicketListPage />} />
                  <Route path="/tickets/new" element={<CreateTicketPage />} />
                  <Route path="/tickets/:id" element={<TicketDetailPage />} />
                </Routes>
              </MainLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;