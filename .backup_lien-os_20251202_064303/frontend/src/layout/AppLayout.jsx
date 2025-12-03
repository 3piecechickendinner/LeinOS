import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Calendar,
  Bell,
  Settings,
  LogOut,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Liens', href: '/liens', icon: FileText },
  { name: 'Deadlines', href: '/deadlines', icon: Calendar },
  { name: 'Notifications', href: '/notifications', icon: Bell },
];

const bottomNav = [
  { name: 'Settings', href: '/settings', icon: Settings },
];

function SidebarLink({ item }) {
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
      {item.name}
    </NavLink>
  );
}

export function AppLayout() {
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
            <SidebarLink key={item.name} item={item} />
          ))}
        </nav>

        {/* Bottom navigation */}
        <div className="px-3 py-4 border-t border-slate-200 space-y-1">
          {bottomNav.map((item) => (
            <SidebarLink key={item.name} item={item} />
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
            <button className="relative p-2 text-slate-400 hover:text-slate-600">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
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
