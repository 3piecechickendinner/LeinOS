import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Calendar,
  Bell,
  Settings,
  LogOut,
  Menu,
  X,
  Layers,
  Home
} from 'lucide-react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { useVertical } from '../context/VerticalContext';

const navigation = [
  { name: 'Dashboard', href: '/app', icon: LayoutDashboard },
  { name: 'Assets', href: '/app/assets', icon: FileText },
  { name: 'Deadlines', href: '/app/deadlines', icon: Calendar },
  { name: 'Notifications', href: '/app/notifications', icon: Bell, showBadge: true },
];

const bottomNav = [
  { name: 'Settings', href: '/app/settings', icon: Settings },
];

function SidebarLink({ item, unreadCount, onClick }) {
  const showBadge = item.showBadge && unreadCount > 0;

  return (
    <NavLink
      to={item.href}
      onClick={onClick}
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
      {showBadge && (
        <span className="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
          {unreadCount}
        </span>
      )}
    </NavLink>
  );
}

export function AppLayout() {
  const navigate = useNavigate();
  const { currentVertical, setCurrentVertical } = useVertical();
  const [unreadCount, setUnreadCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    async function fetchUnreadCount() {
      try {
        const response = await apiClient.getUnreadNotificationCount();
        setUnreadCount(response?.count || 0);
      } catch (error) {
        console.error('Failed to fetch unread count:', error);
      }
    }
    fetchUnreadCount();

    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Mobile menu overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 z-40 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Desktop: always visible, Mobile: slide-out */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-64 md:w-56 flex flex-col bg-white border-r border-slate-200
          transform transition-transform duration-300 ease-in-out
          ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
          <Link to="/" className="text-lg font-bold text-slate-900 hover:text-indigo-600 transition-colors">
            AssetOS
          </Link>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="md:hidden p-2 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => (
            <SidebarLink
              key={item.name}
              item={item}
              unreadCount={unreadCount}
              onClick={() => setMobileMenuOpen(false)}
            />
          ))}
        </nav>

        {/* Bottom navigation */}
        <div className="px-3 py-4 border-t border-slate-200 space-y-1">
          <SidebarLink
            item={{ name: 'Back to Home', href: '/', icon: Home }}
            unreadCount={0}
            onClick={() => setMobileMenuOpen(false)}
          />
          {bottomNav.map((item) => (
            <SidebarLink
              key={item.name}
              item={item}
              unreadCount={0}
              onClick={() => setMobileMenuOpen(false)}
            />
          ))}
          <button
            className="flex items-center gap-3 w-full px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded-md transition-colors min-h-[44px]"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden w-full md:w-auto">
        {/* Header */}
        <header className="h-14 flex items-center justify-between px-4 md:px-6 bg-white border-b border-slate-200">
          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="md:hidden p-2 -ml-2 text-slate-600 hover:text-slate-900 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
          >
            <Menu className="h-6 w-6" />
          </button>

          {/* Vertical Selector */}
          <div className="flex items-center gap-3">
            <Layers className="h-5 w-5 text-slate-500 hidden sm:block" />
            <select
              value={currentVertical}
              onChange={(e) => setCurrentVertical(e.target.value)}
              className="bg-slate-50 border-none text-sm font-semibold text-slate-900 focus:ring-0 cursor-pointer py-1 pl-2 pr-8 rounded-md hover:bg-slate-100 transition-colors block w-full sm:w-auto"
            >
              <option value="tax_lien">Tax Liens</option>
              <option value="civil_judgment">Civil Judgments</option>
              <option value="probate">Probate</option>
              <option value="mineral_rights">Mineral Rights</option>
              <option value="surplus_funds">Surplus Funds</option>
            </select>
          </div>

          <div className="flex items-center gap-2 md:gap-4">
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
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
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;