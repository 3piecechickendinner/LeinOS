import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import {
  Bell,
  DollarSign,
  AlertTriangle,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Filter
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import apiClient from '../api/client';

export function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [typeFilter, setTypeFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  async function fetchNotifications() {
    setLoading(true);
    try {
      const params = {};
      if (filter === 'unread') {
        params.unread_only = true;
      }
      if (typeFilter !== 'all') {
        params.notification_type = typeFilter;
      }

      const response = await apiClient.getNotifications(params);
      const notifList = response?.notifications || response || [];
      setNotifications(Array.isArray(notifList) ? notifList : []);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleMarkAsRead(notificationId) {
    try {
      await apiClient.markNotificationRead(notificationId);

      // Update local state
      setNotifications(prev =>
        prev.map(n =>
          n.notification_id === notificationId ? { ...n, read: true } : n
        )
      );
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'unread' && notif.read) return false;
    if (filter === 'read' && !notif.read) return false;
    if (typeFilter !== 'all' && notif.notification_type !== typeFilter) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-slate-900">Notifications</h1>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="h-4 w-4 mr-1" />
          Filters
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="py-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Select
                label="Status"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Notifications' },
                  { value: 'unread', label: 'Unread Only' },
                  { value: 'read', label: 'Read Only' },
                ]}
              />
              <Select
                label="Type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Types' },
                  { value: 'deadline_approaching', label: 'Deadlines' },
                  { value: 'payment_received', label: 'Payments' },
                  { value: 'lien_created', label: 'Lien Updates' },
                ]}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick filter tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            filter === 'all'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            filter === 'unread'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          Unread
        </button>
        <button
          onClick={() => setFilter('read')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            filter === 'read'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          Read
        </button>
      </div>

      {/* Notifications list */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center text-sm text-slate-500">
              Loading notifications...
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="p-8 text-center">
              <Bell className="h-12 w-12 mx-auto text-slate-300 mb-3" />
              <p className="text-sm text-slate-500">No notifications found</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filteredNotifications.map((notification) => (
                <NotificationItem
                  key={notification.notification_id}
                  notification={notification}
                  onMarkAsRead={handleMarkAsRead}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary */}
      {!loading && filteredNotifications.length > 0 && (
        <div className="text-xs text-slate-500">
          Showing {filteredNotifications.length} of {notifications.length} notifications
        </div>
      )}
    </div>
  );
}

function NotificationItem({ notification, onMarkAsRead }) {
  const icon = getNotificationIcon(notification.notification_type);
  const isUnread = !notification.read;

  return (
    <div
      className={`p-4 hover:bg-slate-50 transition-colors ${
        isUnread ? 'bg-blue-50/30' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            notification.priority === 'high'
              ? 'bg-red-100 text-red-600'
              : 'bg-slate-100 text-slate-600'
          }`}
        >
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="text-sm font-medium text-slate-900">
              {notification.title || 'Notification'}
              {isUnread && (
                <span className="inline-block w-2 h-2 bg-blue-600 rounded-full ml-2" />
              )}
            </h3>
            <div className="flex items-center gap-2">
              {notification.priority === 'high' && (
                <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded bg-red-100 text-red-700">
                  High Priority
                </span>
              )}
              <span className="text-xs text-slate-500 whitespace-nowrap">
                {formatDistanceToNow(new Date(notification.created_at), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>

          <p className="text-sm text-slate-600 mb-2">{notification.message}</p>

          <div className="flex items-center gap-3">
            {notification.lien_id && (
              <Link
                to={`/liens/${notification.lien_id}`}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                View Lien →
              </Link>
            )}
            {isUnread && (
              <button
                onClick={() => onMarkAsRead(notification.notification_id)}
                className="text-xs text-slate-600 hover:text-slate-900"
              >
                Mark as read
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function getNotificationIcon(type) {
  switch (type) {
    case 'deadline_approaching':
      return <Clock className="h-5 w-5" />;
    case 'payment_received':
      return <DollarSign className="h-5 w-5" />;
    case 'lien_created':
    case 'lien_updated':
      return <FileText className="h-5 w-5" />;
    case 'alert':
      return <AlertTriangle className="h-5 w-5" />;
    case 'success':
      return <CheckCircle className="h-5 w-5" />;
    case 'error':
      return <XCircle className="h-5 w-5" />;
    default:
      return <Bell className="h-5 w-5" />;
  }
}

export default NotificationsPage;
