import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  DollarSign, FileText, TrendingUp, AlertCircle,
  Calculator, Clock, CreditCard, BarChart3,
  FileCheck, Bell, FolderOpen, X, ArrowRight, Mail
} from 'lucide-react';
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
  const [showHero, setShowHero] = useState(() => {
    return localStorage.getItem('lienOSHeroDismissed') !== 'true';
  });
  const [showContact, setShowContact] = useState(() => {
    return localStorage.getItem('lienOSContactDismissed') !== 'true';
  });

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

  const handleDismissHero = () => {
    localStorage.setItem('lienOSHeroDismissed', 'true');
    setShowHero(false);
  };

  const handleDismissContact = () => {
    localStorage.setItem('lienOSContactDismissed', 'true');
    setShowContact(false);
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <h1 className="text-lg md:text-xl font-semibold text-slate-900">Dashboard</h1>
        <Link to="/liens" className="w-full sm:w-auto">
          <Button size="sm" className="w-full sm:w-auto">Add Lien</Button>
        </Link>
      </div>

      {/* Hero Section - Show on first visit or when portfolio is empty */}
      {showHero && (stats.activeLiens === 0 || localStorage.getItem('lienOSHeroDismissed') !== 'true') && (
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-slate-50 opacity-50" />

          <button
            onClick={handleDismissHero}
            className="absolute top-4 right-4 p-1 text-slate-400 hover:text-slate-600 rounded-md hover:bg-white/50 z-10 min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>

          <CardContent className="relative pt-8 pb-8 px-6 md:px-8">
            {/* Header */}
            <div className="text-center max-w-3xl mx-auto mb-8">
              <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-3">
                AI-Powered Tax Lien Management
              </h2>
              <p className="text-lg text-slate-600 mb-4">
                7 specialized agents working 24/7 to automate your tax lien operations
              </p>
              <p className="text-sm md:text-base text-slate-700 leading-relaxed">
                LienOS uses intelligent AI agents to handle the operational complexity of tax lien investing.
                While you focus on deal flow, our agents calculate interest, monitor deadlines, track payments,
                and keep your portfolio optimized—automatically.
              </p>
            </div>

            {/* Agent Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <AgentCard
                icon={Calculator}
                title="Interest Calculator"
                description="Real-time ROI tracking"
              />
              <AgentCard
                icon={Clock}
                title="Deadline Monitor"
                description="Never miss a redemption period"
              />
              <AgentCard
                icon={CreditCard}
                title="Payment Processor"
                description="Automatic reconciliation"
              />
              <AgentCard
                icon={BarChart3}
                title="Portfolio Analytics"
                description="Performance insights"
              />
              <AgentCard
                icon={FileCheck}
                title="Document Generator"
                description="Compliance automation"
              />
              <AgentCard
                icon={Bell}
                title="Communication Hub"
                description="Alert coordination"
              />
              <AgentCard
                icon={FolderOpen}
                title="Lien Tracker"
                description="Centralized management"
              />
              <div className="flex items-center justify-center">
                <Link to="/liens/new" className="w-full">
                  <Button className="w-full min-h-[44px]">
                    Get Started
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Contact Section - Subtle partnership inquiry */}
      {showContact && (
        <Card className="relative bg-slate-50 border-slate-200">
          <button
            onClick={handleDismissContact}
            className="absolute top-3 right-3 p-1 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 z-10 min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>

          <CardContent className="py-4 px-5">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-2 bg-blue-100 rounded-md">
                <Mail className="h-5 w-5 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0 pt-0.5">
                <p className="text-sm font-semibold text-slate-900 mb-1">
                  Want LienOS for your organization?
                </p>
                <p className="text-sm text-slate-600 mb-2">
                  We're exploring partnerships with tax lien investors and training companies.
                  Get in touch to discuss custom deployments.
                </p>
                <a
                  href="mailto:sdhines3@gmail.com"
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
                >
                  <Mail className="h-3.5 w-3.5" />
                  sdhines3@gmail.com
                </a>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

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

function AgentCard({ icon: Icon, title, description }) {
  return (
    <div className="flex items-start gap-3 p-4 bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-sm transition-all">
      <div className="flex-shrink-0 p-2 bg-blue-50 rounded-md">
        <Icon className="h-5 w-5 text-blue-600" />
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="text-sm font-semibold text-slate-900 mb-0.5">
          {title}
        </h3>
        <p className="text-xs text-slate-600">
          {description}
        </p>
      </div>
    </div>
  );
}

export default DashboardPage;
