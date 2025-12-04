import React, { useState } from 'react';
import { Download, ExternalLink, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import apiClient from '../api/client';

export function SettingsPage() {
  const [notificationPrefs, setNotificationPrefs] = useState({
    emailEnabled: true,
    deadlineAlerts: {
      days90: true,
      days60: true,
      days30: true,
      days14: true,
      days7: true,
    },
  });

  const [displayPrefs, setDisplayPrefs] = useState({
    dateFormat: 'MM/DD/YYYY',
  });

  const [notifSaved, setNotifSaved] = useState(false);
  const [displaySaved, setDisplaySaved] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleEmailToggle = () => {
    setNotificationPrefs(prev => ({
      ...prev,
      emailEnabled: !prev.emailEnabled,
    }));
  };

  const handleDeadlineAlertChange = (key) => {
    setNotificationPrefs(prev => ({
      ...prev,
      deadlineAlerts: {
        ...prev.deadlineAlerts,
        [key]: !prev.deadlineAlerts[key],
      },
    }));
  };

  const handleSaveNotifications = () => {
    // Save to localStorage for now (can be API call later)
    localStorage.setItem('notificationPrefs', JSON.stringify(notificationPrefs));
    setNotifSaved(true);
    setTimeout(() => setNotifSaved(false), 2000);
  };

  const handleDateFormatChange = (e) => {
    setDisplayPrefs({ dateFormat: e.target.value });
  };

  const handleSaveDisplay = () => {
    // Save to localStorage for now (can be API call later)
    localStorage.setItem('displayPrefs', JSON.stringify(displayPrefs));
    setDisplaySaved(true);
    setTimeout(() => setDisplaySaved(false), 2000);
  };

  const handleExportData = async () => {
    setExporting(true);
    try {
      const liens = await apiClient.getLiens({});
      const dataStr = JSON.stringify(liens, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `lienos-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export data:', error);
      alert('Failed to export data. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6 max-w-4xl">
      <h1 className="text-lg md:text-xl font-semibold text-slate-900">Settings</h1>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-slate-600">Tenant ID</p>
              <p className="mt-0.5 text-sm text-slate-900 font-mono">demo-user</p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600">Plan</p>
              <p className="mt-0.5 text-sm text-slate-900">Free Tier</p>
            </div>
            <div className="sm:col-span-2">
              <p className="text-xs font-medium text-slate-600">API Endpoint</p>
              <p className="mt-0.5 text-sm text-slate-900 font-mono truncate">
                {import.meta.env.VITE_API_URL || 'https://lien-os-api.onrender.com'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Email toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-900">Email Notifications</p>
              <p className="text-xs text-slate-500">Receive email alerts for important events</p>
            </div>
            <button
              onClick={handleEmailToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors min-h-[44px] min-w-[44px] ${
                notificationPrefs.emailEnabled ? 'bg-blue-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  notificationPrefs.emailEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Deadline alerts */}
          <div>
            <p className="text-sm font-medium text-slate-900 mb-2">Deadline Alerts</p>
            <p className="text-xs text-slate-500 mb-3">Get notified before redemption deadlines</p>
            <div className="space-y-2">
              {[
                { key: 'days90', label: '90 days before' },
                { key: 'days60', label: '60 days before' },
                { key: 'days30', label: '30 days before' },
                { key: 'days14', label: '14 days before' },
                { key: 'days7', label: '7 days before' },
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationPrefs.deadlineAlerts[key]}
                    onChange={() => handleDeadlineAlertChange(key)}
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 min-h-[44px] min-w-[44px]"
                  />
                  <span className="text-sm text-slate-700">{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Save button */}
          <div className="pt-2 border-t border-slate-200">
            <Button
              size="sm"
              onClick={handleSaveNotifications}
              className="min-h-[44px]"
            >
              {notifSaved ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Saved!
                </>
              ) : (
                'Save Preferences'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Display Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Display Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Select
              label="Date Format"
              value={displayPrefs.dateFormat}
              onChange={handleDateFormatChange}
              options={[
                { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (US)' },
                { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (International)' },
                { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (ISO)' },
              ]}
            />
            <p className="text-xs text-slate-500 mt-1">
              Example: {displayPrefs.dateFormat === 'MM/DD/YYYY' ? '12/31/2024' :
                       displayPrefs.dateFormat === 'DD/MM/YYYY' ? '31/12/2024' : '2024-12-31'}
            </p>
          </div>

          {/* Save button */}
          <div className="pt-2 border-t border-slate-200">
            <Button
              size="sm"
              onClick={handleSaveDisplay}
              className="min-h-[44px]"
            >
              {displaySaved ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Saved!
                </>
              ) : (
                'Save Preferences'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium text-slate-900 mb-1">Export Data</p>
            <p className="text-xs text-slate-500 mb-3">
              Download all your lien data as a JSON file for backup or analysis
            </p>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleExportData}
              disabled={exporting}
              className="min-h-[44px]"
            >
              <Download className="h-4 w-4 mr-2" />
              {exporting ? 'Exporting...' : 'Export All Liens'}
            </Button>
          </div>

          <div className="pt-2 border-t border-slate-200">
            <p className="text-sm font-medium text-slate-900 mb-1">Documentation</p>
            <p className="text-xs text-slate-500 mb-3">
              Learn more about using LienOS and managing tax lien certificates
            </p>
            <a
              href="https://github.com/yourusername/lien-os#readme"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 hover:underline"
            >
              View Documentation
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default SettingsPage;
