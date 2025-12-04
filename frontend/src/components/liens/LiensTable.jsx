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
    <div className="overflow-x-auto -mx-4 md:mx-0">
      <div className="inline-block min-w-full align-middle">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap">
                Certificate #
              </th>
              <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap">
                Property Address
              </th>
              <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap hidden sm:table-cell">
                County
              </th>
              <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap">
                Amount
              </th>
              <th className="text-right text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap hidden md:table-cell">
                Interest
              </th>
              <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap hidden lg:table-cell">
                Purchase Date
              </th>
              <th className="text-left text-xs font-medium text-slate-600 px-3 md:px-4 py-3 whitespace-nowrap">
                Status
              </th>
              <th className="px-3 md:px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {liens.map((lien) => (
              <tr
                key={lien.id}
                className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <td className="px-3 md:px-4 py-3">
                  <span className="text-sm font-medium text-slate-900 whitespace-nowrap">
                    {lien.certificate_number || '-'}
                  </span>
                </td>
                <td className="px-3 md:px-4 py-3">
                  <div className="max-w-[200px] md:max-w-none">
                    <span className="text-sm text-slate-900 block truncate">
                      {lien.property_address || 'N/A'}
                    </span>
                  </div>
                </td>
                <td className="px-3 md:px-4 py-3 hidden sm:table-cell">
                  <span className="text-sm text-slate-600 whitespace-nowrap">
                    {lien.county || '-'}
                  </span>
                </td>
                <td className="text-right px-3 md:px-4 py-3">
                  <span className="text-sm font-medium text-slate-900 whitespace-nowrap">
                    ${(lien.purchase_amount || 0).toLocaleString()}
                  </span>
                </td>
                <td className="text-right px-3 md:px-4 py-3 hidden md:table-cell">
                  <span className="text-sm text-slate-900 whitespace-nowrap">
                    {(lien.interest_rate || 0).toFixed(2)}%
                  </span>
                </td>
                <td className="px-3 md:px-4 py-3 hidden lg:table-cell">
                  <span className="text-sm text-slate-600 whitespace-nowrap">
                    {lien.purchase_date
                      ? format(new Date(lien.purchase_date), 'MMM d, yyyy')
                      : '-'}
                  </span>
                </td>
                <td className="px-3 md:px-4 py-3">
                  <StatusBadge status={lien.status} />
                </td>
                <td className="px-3 md:px-4 py-3">
                  <Link
                    to={`/liens/${lien.id}`}
                    className="inline-flex items-center text-slate-400 hover:text-slate-600 min-h-[44px] min-w-[44px] justify-center"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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

export default LiensTable;
