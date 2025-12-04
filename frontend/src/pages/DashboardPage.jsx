import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DollarSign, FileText, TrendingUp, AlertCircle } from 'lucide-react';
import { StatsCard } from '../components/dashboard/StatsCard';
import { RevenueChart } from '../components/dashboard/RevenueChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import apiClient from '../api/client';

export function DashboardPage() {
  const [stats, setStats] = useState({
    totalValue: '$0',
    activeLiens: 0,
    avgReturn: '0%',
    upcomingDeadlines: 0,
  });
  const [recentLiens, setRecentLiens] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [summary, liens] = await Promise.all([
          apiClient.getPortfolioSummary().catch(() => null),
          apiClient.getLiens({ limit: 5 }).catch(() => []),
        ]);

        if (summary) {
          setStats({
            totalValue: `$${(summary.total_value || 0).toLocaleString()}`,
            activeLiens: summary.active_liens || 0,
            avgReturn: `${(summary.average_return_rate || 0).toFixed(1)}%`,
            upcomingDeadlines: summary.upcoming_deadlines || 0,
          });
        }

        // Defensive: ensure liens is an array
        setRecentLiens(Array.isArray(liens) ? liens : []);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <h1 className="text-lg md:text-xl font-semibold text-slate-900">Dashboard</h1>
        <Link to="/liens" className="w-full sm:w-auto">
          <Button size="sm" className="w-full sm:w-auto">Add Lien</Button>
        </Link>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <StatsCard
          title="Total Portfolio Value"
          value={stats.totalValue}
          change="+12.5% from last month"
          changeType="positive"
          icon={DollarSign}
        />
        <StatsCard
          title="Active Liens"
          value={stats.activeLiens}
          change={`${stats.activeLiens} total`}
          icon={FileText}
        />
        <StatsCard
          title="Average Return"
          value={stats.avgReturn}
          change="+2.1% from last month"
          changeType="positive"
          icon={TrendingUp}
        />
        <StatsCard
          title="Upcoming Deadlines"
          value={stats.upcomingDeadlines}
          change="Next 30 days"
          changeType={stats.upcomingDeadlines > 0 ? 'negative' : undefined}
          icon={AlertCircle}
        />
      </div>

      {/* Charts and tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <RevenueChart />

        {/* Recent Liens */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Liens</CardTitle>
              <Link to="/liens" className="text-xs text-blue-600 hover:text-blue-700">
                View all
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-4 text-center text-sm text-slate-500">Loading...</div>
            ) : recentLiens.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-500">
                No liens found
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-2 whitespace-nowrap">
                        Property
                      </th>
                      <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-2 whitespace-nowrap">
                        Amount
                      </th>
                      <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-2 whitespace-nowrap">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentLiens.map((lien) => (
                      <tr key={lien.id} className="border-b border-slate-100 last:border-0">
                        <td className="px-3 md:px-4 py-2 max-w-[200px]">
                          <Link
                            to={`/liens/${lien.id}`}
                            className="text-sm text-slate-900 hover:text-blue-600 block truncate"
                          >
                            {lien.property_address || 'N/A'}
                          </Link>
                        </td>
                        <td className="text-right text-sm text-slate-900 px-3 md:px-4 py-2 whitespace-nowrap">
                          ${(lien.purchase_amount || 0).toLocaleString()}
                        </td>
                        <td className="text-right px-3 md:px-4 py-2">
                          <StatusBadge status={lien.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    active: 'bg-green-100 text-green-700',
    redeemed: 'bg-blue-100 text-blue-700',
    foreclosed: 'bg-yellow-100 text-yellow-700',
    expired: 'bg-slate-100 text-slate-700',
  };

  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded ${styles[status] || styles.active}`}>
      {status || 'active'}
    </span>
  );
}

export default DashboardPage;
