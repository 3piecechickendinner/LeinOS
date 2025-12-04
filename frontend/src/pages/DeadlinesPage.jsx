import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format, formatDistanceToNow, differenceInDays } from 'date-fns';
import {
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  MapPin,
  FileText,
  Filter
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import apiClient from '../api/client';

export function DeadlinesPage() {
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('pending');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchDeadlines();
  }, []);

  async function fetchDeadlines() {
    setLoading(true);
    try {
      const response = await apiClient.getUpcomingDeadlines(90);
      const deadlineList = Array.isArray(response) ? response : response?.deadlines || [];
      setDeadlines(deadlineList);
    } catch (error) {
      console.error('Failed to fetch deadlines:', error);
      setDeadlines([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleMarkCompleted(deadlineId) {
    try {
      await apiClient.markDeadlineCompleted(deadlineId);

      // Update local state
      setDeadlines(prev =>
        prev.map(d =>
          d.deadline_id === deadlineId ? { ...d, status: 'completed' } : d
        )
      );
    } catch (error) {
      console.error('Failed to mark deadline as completed:', error);
    }
  }

  const filteredDeadlines = deadlines.filter(deadline => {
    if (typeFilter !== 'all' && deadline.deadline_type !== typeFilter) return false;
    if (statusFilter !== 'all' && deadline.status !== statusFilter) return false;
    return true;
  });

  // Sort by nearest deadline first
  const sortedDeadlines = [...filteredDeadlines].sort((a, b) => {
    return a.days_remaining - b.days_remaining;
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <h1 className="text-lg md:text-xl font-semibold text-slate-900">Upcoming Deadlines</h1>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
          className="w-full sm:w-auto min-h-[44px]"
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
                label="Type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Types' },
                  { value: 'redemption', label: 'Redemption' },
                  { value: 'payment', label: 'Payment' },
                  { value: 'filing', label: 'Filing' },
                ]}
              />
              <Select
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Statuses' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'completed', label: 'Completed' },
                ]}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-xs text-slate-600">Urgent ({"<"}7 days)</p>
                <p className="text-lg font-semibold text-slate-900">
                  {sortedDeadlines.filter(d => d.days_remaining < 7 && d.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-xs text-slate-600">Soon (7-30 days)</p>
                <p className="text-lg font-semibold text-slate-900">
                  {sortedDeadlines.filter(d => d.days_remaining >= 7 && d.days_remaining < 30 && d.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Calendar className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-slate-600">Later ({">"}30 days)</p>
                <p className="text-lg font-semibold text-slate-900">
                  {sortedDeadlines.filter(d => d.days_remaining >= 30 && d.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Deadlines list */}
      {loading ? (
        <div className="p-8 text-center text-sm text-slate-500">
          Loading deadlines...
        </div>
      ) : sortedDeadlines.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-3" />
            <p className="text-sm text-slate-600">No upcoming deadlines</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {sortedDeadlines.map((deadline) => (
            <DeadlineCard
              key={deadline.deadline_id}
              deadline={deadline}
              onMarkCompleted={handleMarkCompleted}
            />
          ))}
        </div>
      )}

      {/* Summary */}
      {!loading && sortedDeadlines.length > 0 && (
        <div className="text-xs text-slate-500">
          Showing {sortedDeadlines.length} of {deadlines.length} deadlines
        </div>
      )}
    </div>
  );
}

function DeadlineCard({ deadline, onMarkCompleted }) {
  const daysRemaining = deadline.days_remaining;
  const urgency = getUrgency(daysRemaining);
  const isCompleted = deadline.status === 'completed';

  return (
    <Card className={isCompleted ? 'opacity-60' : ''}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Urgency indicator */}
          <div
            className={`flex-shrink-0 w-16 h-16 rounded-lg flex flex-col items-center justify-center ${urgency.bgColor}`}
          >
            <span className={`text-2xl font-bold ${urgency.textColor}`}>
              {daysRemaining}
            </span>
            <span className={`text-xs ${urgency.textColor}`}>
              {daysRemaining === 1 ? 'day' : 'days'}
            </span>
          </div>

          {/* Deadline info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-semibold text-slate-900">
                    {deadline.description || 'Deadline'}
                  </h3>
                  <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded bg-slate-100 text-slate-700 capitalize">
                    {deadline.deadline_type}
                  </span>
                  {isCompleted && (
                    <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded bg-green-100 text-green-700">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Completed
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-600">
                  Certificate: {deadline.certificate_number}
                </p>
              </div>
            </div>

            {/* Property address */}
            {deadline.property_address && (
              <div className="flex items-center gap-1 text-sm text-slate-600 mb-3">
                <MapPin className="h-4 w-4" />
                <span>{deadline.property_address}</span>
              </div>
            )}

            {/* Deadline date and countdown */}
            <div className="flex items-center gap-4 mb-3">
              <div className="flex items-center gap-1 text-sm text-slate-600">
                <Calendar className="h-4 w-4" />
                <span>
                  {format(new Date(deadline.deadline_date), 'MMM d, yyyy')}
                </span>
              </div>
              <div className={`text-sm font-medium ${urgency.textColor}`}>
                {daysRemaining === 0
                  ? 'Due today'
                  : daysRemaining === 1
                  ? 'Due tomorrow'
                  : `${daysRemaining} days remaining`}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {deadline.lien_id && (
                <Link
                  to={`/liens/${deadline.lien_id}`}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                >
                  View Lien →
                </Link>
              )}
              {!isCompleted && (
                <button
                  onClick={() => onMarkCompleted(deadline.deadline_id)}
                  className="text-xs text-slate-600 hover:text-slate-900"
                >
                  Mark completed
                </button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function getUrgency(daysRemaining) {
  if (daysRemaining < 0) {
    return {
      level: 'overdue',
      bgColor: 'bg-red-100',
      textColor: 'text-red-700',
    };
  } else if (daysRemaining < 7) {
    return {
      level: 'urgent',
      bgColor: 'bg-red-100',
      textColor: 'text-red-700',
    };
  } else if (daysRemaining < 30) {
    return {
      level: 'soon',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-700',
    };
  } else {
    return {
      level: 'later',
      bgColor: 'bg-green-100',
      textColor: 'text-green-700',
    };
  }
}

export default DeadlinesPage;
