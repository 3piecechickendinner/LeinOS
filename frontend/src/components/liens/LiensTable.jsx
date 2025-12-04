import React from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ChevronRight } from 'lucide-react';

export function LiensTable({ liens = [], loading = false }) {
  if (loading) {
    return (
      <div className="p-8 text-center text-sm text-slate-500">
        Loading liens...
      </div>
    );
  }

  if (liens.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-slate-500">
        No liens found. Add your first lien to get started.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200">
            <th className="text-left text-xs font-medium text-slate-600 px-4 py-3">
              Certificate #
            </th>
            <th className="text-left text-xs font-medium text-slate-600 px-4 py-3">
              Property Address
            </th>
            <th className="text-left text-xs font-medium text-slate-600 px-4 py-3">
              County
            </th>
            <th className="text-right text-xs font-medium text-slate-600 px-4 py-3">
              Face Value
            </th>
            <th className="text-right text-xs font-medium text-slate-600 px-4 py-3">
              Interest Rate
            </th>
            <th className="text-left text-xs font-medium text-slate-600 px-4 py-3">
              Purchase Date
            </th>
            <th className="text-left text-xs font-medium text-slate-600 px-4 py-3">
              Status
            </th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {liens.map((lien) => (
            <tr
              key={lien.id}
              className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
            >
              <td className="px-4 py-3">
                <span className="text-sm font-medium text-slate-900">
                  {lien.certificate_number || '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm text-slate-900">
                  {lien.property_address || 'N/A'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm text-slate-600">
                  {lien.county || '-'}
                </span>
              </td>
              <td className="text-right px-4 py-3">
                <span className="text-sm font-medium text-slate-900">
                  ${(lien.purchase_amount || 0).toLocaleString()}
                </span>
              </td>
              <td className="text-right px-4 py-3">
                <span className="text-sm text-slate-900">
                  {(lien.interest_rate || 0).toFixed(2)}%
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm text-slate-600">
                  {lien.purchase_date
                    ? format(new Date(lien.purchase_date), 'MMM d, yyyy')
                    : '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={lien.status} />
              </td>
              <td className="px-4 py-3">
                <Link
                  to={`/liens/${lien.id}`}
                  className="inline-flex items-center text-slate-400 hover:text-slate-600"
                >
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
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

export default LiensTable;
