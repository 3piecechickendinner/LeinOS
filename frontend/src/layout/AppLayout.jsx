import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Calendar,
  Bell,
  Settings,
  LogOut,
} from 'lucide-react';
import apiClient from '../api/client';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Liens', href: '/liens', icon: FileText },
  { name: 'Deadlines', href: '/deadlines', icon: Calendar },
  { name: 'Notifications', href: '/notifications', icon: Bell, showBadge: true },
];

const bottomNav = [
  { name: 'Settings', href: '/settings', icon: Settings },
];

function SidebarLink({ item, unreadCount }) {
  const showBadge = item.showBadge && unreadCount > 0;

  return (
    <NavLink
      to={item.href}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors
        ${isActive
          ? 'bg-blue-50 text-blue-700'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`
      }
    >
      <item.icon className="h-4 w-4" />
      <span className="flex-1">{item.name}</span>
      {showBadge && (
        <span className="inline-flex items-center justify-center h-5 min-w-[20px] px-1.5 text-xs font-semibold text-white bg-red-500 rounded-full">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </NavLink>
  );
}

export function AppLayout() {
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchUnreadCount();

    // Poll for unread count every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchUnreadCount() {
    try {
      const response = await apiClient.getUnreadNotificationCount();
      setUnreadCount(response?.count || 0);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-56 flex flex-col bg-white border-r border-slate-200">
        {/* Logo */}
        <div className="h-14 flex items-center px-4 border-b border-slate-200">
          <span className="text-lg font-bold text-slate-900">LienOS</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <SidebarLink key={item.name} item={item} unreadCount={unreadCount} />
          ))}
        </nav>

        {/* Bottom navigation */}
        <div className="px-3 py-4 border-t border-slate-200 space-y-1">
          {bottomNav.map((item) => (
            <SidebarLink key={item.name} item={item} unreadCount={0} />
          ))}
          <button
            className="flex items-center gap-3 w-full px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded-md transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-14 flex items-center justify-between px-6 bg-white border-b border-slate-200">
          <h1 className="text-sm font-medium text-slate-900">
            Tax Lien Management
          </h1>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-0.5 right-0.5 h-4 w-4 flex items-center justify-center text-xs font-semibold text-white bg-red-500 rounded-full">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
            <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center">
              <span className="text-xs font-medium text-slate-600">U</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
