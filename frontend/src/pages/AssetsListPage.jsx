import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Download } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import apiClient from '../api/client';
import { useVertical } from '../context/VerticalContext';

export default function AssetsListPage() {
  const { currentVertical, getVerticalName } = useVertical();
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // FETCH DATA
  useEffect(() => {
    async function fetchAssets() {
      setLoading(true);
      try {
        const data = await apiClient.getAssets(currentVertical);
        setAssets(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to fetch assets:", error);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    }
    fetchAssets();
  }, [currentVertical]);

  // DYNAMIC COLUMNS LOGIC
  const renderRow = (asset) => {
    switch (currentVertical) {
      case 'civil_judgment':
        return (
          <>
            <td className="px-4 py-3 font-medium">{asset.case_number || 'N/A'}</td>
            <td className="px-4 py-3">{asset.defendant_name || asset.debtor_name || 'Unknown'}</td> {/* Adjusted to look for defendant_name */}
            <td className="px-4 py-3">${(asset.judgment_amount || 0).toLocaleString()}</td>
            <td className="px-4 py-3 text-slate-500">{asset.court_name}</td>
          </>
        );
      case 'mineral_rights':
        return (
          <>
            <td className="px-4 py-3 font-medium truncate max-w-[200px]">{asset.legal_description || 'N/A'}</td>
            <td className="px-4 py-3">{asset.operator_name}</td>
            <td className="px-4 py-3">{asset.net_mineral_acres?.toFixed(2)} NMA</td>
            <td className="px-4 py-3 text-slate-500">{asset.status}</td>
          </>
        );
      case 'probate':
        return (
          <>
            <td className="px-4 py-3 font-medium">{asset.deceased_name}</td>
            <td className="px-4 py-3">{asset.date_of_death}</td>
            <td className="px-4 py-3">{asset.case_status}</td>
            <td className="px-4 py-3 text-slate-500">{asset.attorney_contact}</td>
          </>
        );
      case 'surplus_funds':
        return (
          <>
            <td className="px-4 py-3 font-medium">{asset.county}</td>
            <td className="px-4 py-3">${(asset.surplus_amount || 0).toLocaleString()}</td>
            <td className="px-4 py-3">{asset.foreclosure_date}</td>
            <td className="px-4 py-3 text-red-600 font-medium">{asset.claim_deadline}</td>
          </>
        );
      default: // tax_lien
        return (
          <>
            <td className="px-4 py-3 font-medium">{asset.certificate_number}</td>
            <td className="px-4 py-3">{asset.county}</td>
            <td className="px-4 py-3">${(asset.purchase_amount || 0).toLocaleString()}</td>
            <td className="px-4 py-3 text-slate-500">{asset.interest_rate}%</td>
          </>
        );
    }
  };

  // DYNAMIC HEADERS
  const getHeaders = () => {
    switch (currentVertical) {
      case 'civil_judgment': return ['Case #', 'Defendant', 'Amount', 'Court'];
      case 'mineral_rights': return ['Legal Desc', 'Operator', 'Net Acres', 'Status'];
      case 'probate': return ['Deceased', 'Date of Death', 'Status', 'Attorney'];
      case 'surplus_funds': return ['County', 'Surplus Amount', 'Auction Date', 'Deadline'];
      default: return ['Cert #', 'County', 'Amount', 'Interest'];
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{getVerticalName()}</h1>
          <p className="text-slate-500">Manage your {getVerticalName().toLowerCase()} portfolio</p>
        </div>
        <Link to="/assets/new">
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add New
          </Button>
        </Link>
      </div>

      <Card>
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder={`Search ${getVerticalName().toLowerCase()}...`}
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex items-center gap-2">
              <Filter className="h-4 w-4" /> Filter
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Download className="h-4 w-4" /> Export
            </Button>
          </div>
        </div>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                <tr>
                  {getHeaders().map((h, i) => <th key={i} className="px-4 py-3">{h}</th>)}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr><td colSpan="4" className="p-8 text-center text-slate-500">Loading assets...</td></tr>
                ) : assets.length === 0 ? (
                  <tr><td colSpan="4" className="p-8 text-center text-slate-500">No assets found. Add one to get started.</td></tr>
                ) : (
                  assets.map((asset, i) => (
                    <tr key={asset.id || i} className="hover:bg-slate-50 transition-colors">
                      {renderRow(asset)}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}