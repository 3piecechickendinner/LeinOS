import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AppLayout from './layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import LiensListPage from './pages/LiensListPage';
import LienDetailPage from './pages/LienDetailPage';
import NotificationsPage from './pages/NotificationsPage';
import DeadlinesPage from './pages/DeadlinesPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="liens" element={<LiensListPage />} />
        <Route path="liens/:id" element={<LienDetailPage />} />
        <Route path="deadlines" element={<DeadlinesPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="settings" element={<PlaceholderPage title="Settings" />} />
      </Route>
    </Routes>
  );
}

function PlaceholderPage({ title }) {
  return (
    <div className="flex items-center justify-center h-full">
      <p className="text-slate-500">{title} page coming soon</p>
    </div>
  );
}

export default App;
