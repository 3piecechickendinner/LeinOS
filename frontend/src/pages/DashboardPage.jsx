import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  DollarSign, FileText, TrendingUp, AlertCircle,
  Calculator, Clock, CreditCard, BarChart3,
  FileCheck, Bell, FolderOpen, X, ArrowRight, Mail, Layers
} from 'lucide-react';
import { StatsCard } from '../components/dashboard/StatsCard';
import { RevenueChart } from '../components/dashboard/RevenueChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import apiClient from '../api/client';
import { useVertical } from '../context/VerticalContext';

export function DashboardPage() {
  const { currentVertical, getVerticalName } = useVertical();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ value: '$0', active: 0, return: '0%', deadline: 0 });
  const [recentItems, setRecentItems] = useState([]);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const assets = await apiClient.getAssets(currentVertical);

        // Calculate Total Value based on Vertical
        const totalValue = assets.reduce((sum, item) => {
          let val = 0;
          switch (currentVertical) {
            case 'civil_judgment':
              val = item.judgment_amount || 0;
              break;
            case 'mineral_rights':
              // Assuming a valuation per NMA or just summing known value field if exists
              // For now, if no explicit value, might use 0 or a placeholder
              val = item.estimated_value || 0;
              break;
            case 'probate':
              val = item.est_asset_value || item.estimated_value || 0;
              break;
            case 'surplus_funds':
              val = item.surplus_amount || 0;
              break;
            default: // tax_lien
              val = item.purchase_amount || item.amount || 0;
          }
          return sum + parseFloat(val);
        }, 0);

        setStats({
          value: `$${totalValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
          active: assets.length,
          // These metrics would ideally be calculated from real data too, but static for now as per instructions to focus on Data/Assets
          return: getVerticalDefaults(currentVertical).returnRate,
          deadline: Math.floor(assets.length * 0.1)
        });

        setRecentItems(assets.slice(0, 5));
      } catch (error) {
        console.error("Dashboard Load Failed:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [currentVertical]);

  const getVerticalDefaults = (vertical) => {
    switch (vertical) {
      case 'civil_judgment': return { returnRate: '10% Stat.' }; // Statutory Interest
      case 'mineral_rights': return { returnRate: '18% IRR' };
      case 'probate': return { returnRate: '3-4x ROI' };
      case 'surplus_funds': return { returnRate: '30-40% Fee' };
      default: return { returnRate: '18.2%' };
    }
  }

  // Row Data Mapping
  const getRowData = (item) => {
    const fmt = (v) => v ? `$${parseFloat(v).toLocaleString()}` : '$0';

    switch (currentVertical) {
      case 'civil_judgment':
        return {
          desc: item.case_number || 'No Case #',
          val: fmt(item.judgment_amount),
          status: item.status
        };
      case 'mineral_rights':
        return {
          desc: item.legal_description || 'No Legal Desc',
          val: `${item.net_mineral_acres || 0} NMA`,
          status: item.status
        };
      case 'probate':
        return {
          desc: item.deceased_name || 'Unknown Name',
          val: item.appointment_date || 'No Date', // Fallback if no value
          status: item.case_status
        };
      case 'surplus_funds':
        return {
          desc: item.county || 'Unknown County',
          val: fmt(item.surplus_amount),
          status: item.status || 'Pending'
        };
      default:
        return {
          desc: item.certificate_number || 'No Cert #',
          val: fmt(item.purchase_amount || item.amount),
          status: item.status
        };
    }
  };

  const getMetricLabels = () => {
    switch (currentVertical) {
      case 'civil_judgment': return { value: 'Total Judgment Value', active: 'Active Judgments', return: 'Avg Statutory Rate', deadline: 'Expiring Statutes' };
      case 'mineral_rights': return { value: 'Total Asset Value', active: 'Net Mineral Acres', return: 'Avg Royalty %', deadline: 'Lease Expirations' };
      case 'probate': return { value: 'Total Estate Equity', active: 'Open Probate Cases', return: 'Avg LTV', deadline: 'Creditor Windows' };
      case 'surplus_funds': return { value: 'Total Surplus Found', active: 'Pending Claims', return: 'Avg Recovery Fee', deadline: 'Escheatment Dates' };
      default: return { value: 'Total Portfolio Value', active: 'Active Tax Liens', return: 'Avg Interest Rate', deadline: 'Redemption Deadlines' };
    }
  };
  const labels = getMetricLabels();

  const getHeroDescription = () => {
    switch (currentVertical) {
      case 'civil_judgment': return "Automate your judgment recovery business. Our agents track court dockets, calculate statutory interest daily, monitor statutes of limitations, and generate garnishment paperwork instantly.";
      case 'mineral_rights': return "Manage your subsurface assets with precision. Track monthly production reports, verify royalty checks against operator data, and monitor lease expirations across your entire acreage.";
      case 'probate': return "Streamline your estate lead generation. Our system identifies property equity, tracks probate filing dates, and manages sensitive heir outreach campaigns while you focus on closing.";
      case 'surplus_funds': return "Recover unclaimed funds faster. We monitor foreclosure auctions, calculate accurate surplus amounts after debt satisfaction, and automate claim generation for former homeowners.";
      default: return "7 specialized agents working 24/7 to automate your tax lien operations. We calculate interest, monitor redemption deadlines, track payments, and optimize your portfolio—automatically.";
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <h1 className="text-lg md:text-xl font-semibold text-slate-900">{getVerticalName()} Dashboard</h1>
        <Link to="/assets" className="w-full sm:w-auto"><Button size="sm" className="w-full sm:w-auto">View All</Button></Link>
      </div>

      <Card className="relative overflow-hidden border-blue-200">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-50 opacity-50" />
        <CardContent className="relative pt-8 pb-8 px-6 md:px-8">
          <div className="text-center max-w-3xl mx-auto mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-3">AI-Powered Distressed Asset Management</h2>
            <p className="text-lg text-slate-600 mb-4 font-medium">{getVerticalName()} Edition</p>
            <p className="text-sm md:text-base text-slate-700 leading-relaxed max-w-2xl mx-auto">{getHeroDescription()}</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <AgentCard icon={Calculator} title="Interest Engine" description="Real-time valuation & ROI" />
            <AgentCard icon={Clock} title="Deadline Monitor" description="Statutes & Expirations" />
            <AgentCard icon={CreditCard} title="Revenue Tracker" description="Royalties & Garnishments" />
            <AgentCard icon={FolderOpen} title="Asset Tracker" description="Centralized Data Room" />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white border border-slate-200 shadow-sm">
        <CardContent className="py-6 px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex-1 space-y-1">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full text-blue-600 text-xs">i</span>
              Want AssetOS for your organization?
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">We are exploring partnerships with distressed asset funds, family offices, and high-volume investors. Get in touch to discuss custom deployments.</p>
          </div>
          <div className="flex-shrink-0 bg-slate-50 px-5 py-3 rounded-lg border border-slate-100 text-center md:text-right">
            <p className="text-xs text-slate-500 uppercase tracking-wide font-semibold mb-1">Direct Contact</p>
            <a href="mailto:sdhines3@gmail.com" className="text-lg font-bold text-blue-700 hover:text-blue-900 transition-colors">sdhines3@gmail.com</a>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <StatsCard title={labels.value} value={stats.value} change="+12.5% YTD" changeType="positive" icon={DollarSign} />
        <StatsCard title={labels.active} value={stats.active} change="Records Found" icon={Layers} />
        <StatsCard title={labels.return} value={stats.return} change="Target: 15%" changeType="positive" icon={TrendingUp} />
        <StatsCard title={labels.deadline} value={stats.deadline} change="Next 30 days" changeType={stats.deadline > 0 ? 'negative' : undefined} icon={AlertCircle} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <RevenueChart currentVertical={currentVertical} />
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Activity</CardTitle>
              <Link to="/assets" className="text-xs text-blue-600 hover:text-blue-700">View all</Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-4 text-center text-sm text-slate-500">Loading...</div>
            ) : recentItems.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-500">No assets found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-2">Item / Case</th>
                      <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-2">Value</th>
                      <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentItems.map((item, i) => {
                      const { desc, val, status } = getRowData(item);
                      return (
                        <tr key={item.id || i} className="border-b border-slate-100 last:border-0">
                          <td className="px-3 md:px-4 py-2 text-sm text-slate-900 truncate max-w-[150px]">{desc}</td>
                          <td className="text-right text-sm text-slate-900 px-3 md:px-4 py-2">{val}</td>
                          <td className="text-right px-3 md:px-4 py-2"><StatusBadge status={status} /></td>
                        </tr>
                      );
                    })}
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
  const normalized = (status || 'active').toLowerCase();
  const styles = {
    active: 'bg-green-100 text-green-700',
    open: 'bg-blue-100 text-blue-700',
    producing: 'bg-emerald-100 text-emerald-700',
    leased: 'bg-purple-100 text-purple-700',
    garnishing: 'bg-indigo-100 text-indigo-700',
    settled: 'bg-gray-100 text-gray-700',
    redeemed: 'bg-blue-50 text-blue-600',
    foreclosed: 'bg-red-100 text-red-700',
    pending: 'bg-yellow-100 text-yellow-700',
  };
  // Fallback to active style if no match, just to look good
  const badgeStyle = Object.entries(styles).find(([k]) => normalized.includes(k))?.[1] || 'bg-slate-100 text-slate-700';

  return <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded ${badgeStyle}`}>{status}</span>;
}

function AgentCard({ icon: Icon, title, description }) {
  return (
    <div className="flex items-start gap-3 p-4 bg-white/80 backdrop-blur rounded-lg border border-slate-200 shadow-sm hover:border-blue-300 transition-colors">
      <div className="flex-shrink-0 p-2 bg-blue-50 rounded-md"><Icon className="h-5 w-5 text-blue-600" /></div>
      <div className="min-w-0 flex-1"><h3 className="text-sm font-semibold text-slate-900 mb-0.5">{title}</h3><p className="text-xs text-slate-600">{description}</p></div>
    </div>
  );
}

export default DashboardPage;