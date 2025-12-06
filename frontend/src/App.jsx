import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { VerticalProvider } from './context/VerticalContext';
import AppLayout from './layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import AssetsListPage from './pages/AssetsListPage';
import LienDetailPage from './pages/LienDetailPage';
import AddAssetPage from './pages/AddAssetPage';
import NotificationsPage from './pages/NotificationsPage';
import DeadlinesPage from './pages/DeadlinesPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <VerticalProvider>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="assets" element={<AssetsListPage />} />
          <Route path="assets/new" element={<AddAssetPage />} />
          <Route path="assets/:id" element={<LienDetailPage />} />
          <Route path="liens" element={<Navigate to="/assets" replace />} />
          <Route path="deadlines" element={<DeadlinesPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </VerticalProvider>
  );
}

export default App;