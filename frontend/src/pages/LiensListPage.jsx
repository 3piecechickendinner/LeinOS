import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Select } from '../components/ui/Input';
import { LiensTable } from '../components/liens/LiensTable';
import apiClient from '../api/client';

export function LiensListPage() {
  const navigate = useNavigate();
  const [liens, setLiens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchLiens();
  }, [statusFilter]);

  async function fetchLiens() {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const data = await apiClient.getLiens(params);

      // Defensive: ensure data is an array
      if (Array.isArray(data)) {
        setLiens(data);
      } else {
        console.error('API returned non-array data:', data);
        setLiens([]);
      }
    } catch (error) {
      console.error('Failed to fetch liens:', error);
      setLiens([]);
    } finally {
      setLoading(false);
    }
  }

  const filteredLiens = liens.filter((lien) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      (lien.property_address || '').toLowerCase().includes(query) ||
      (lien.certificate_number || '').toLowerCase().includes(query) ||
      (lien.county || '').toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <h1 className="text-lg md:text-xl font-semibold text-slate-900">Liens</h1>
        <Button
          size="sm"
          className="w-full sm:w-auto"
          onClick={() => navigate('/liens/new')}
        >
          <Plus className="h-4 w-4 mr-1" />
          Add Lien
        </Button>
      </div>

      {/* Search and filters */}
      <Card>
        <CardContent className="py-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by property, certificate, or county..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-md placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[44px]"
              />
            </div>
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

          {showFilters && (
            <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-3">
              <Select
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Statuses' },
                  { value: 'active', label: 'Active' },
                  { value: 'redeemed', label: 'Redeemed' },
                  { value: 'foreclosed', label: 'Foreclosed' },
                  { value: 'expired', label: 'Expired' },
                ]}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <LiensTable liens={filteredLiens} loading={loading} />
      </Card>

      {/* Summary */}
      {!loading && filteredLiens.length > 0 && (
        <div className="text-xs text-slate-500">
          Showing {filteredLiens.length} of {liens.length} liens
        </div>
      )}
    </div>
  );
}

export default LiensListPage;
