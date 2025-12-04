import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AppLayout from './layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import LiensListPage from './pages/LiensListPage';
import LienDetailPage from './pages/LienDetailPage';
import AddLienPage from './pages/AddLienPage';
import NotificationsPage from './pages/NotificationsPage';
import DeadlinesPage from './pages/DeadlinesPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="liens" element={<LiensListPage />} />
        <Route path="liens/new" element={<AddLienPage />} />
        <Route path="liens/:id" element={<LienDetailPage />} />
        <Route path="deadlines" element={<DeadlinesPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
