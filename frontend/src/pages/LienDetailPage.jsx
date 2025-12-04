import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ArrowLeft, FileText, Calendar, DollarSign, MapPin } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { InterestCalculator } from '../components/liens/InterestCalculator';
import apiClient from '../api/client';

export function LienDetailPage() {
  const { id } = useParams();
  const [lien, setLien] = useState(null);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [lienData, paymentsData] = await Promise.all([
          apiClient.getLien(id),
          apiClient.getPayments(id).catch(() => []),
        ]);
        setLien(lienData);
        setPayments(paymentsData);
      } catch (err) {
        setError(err.message || 'Failed to load lien details');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-sm text-slate-500">Loading lien details...</p>
      </div>
    );
  }

  if (error || !lien) {
    return (
      <div className="space-y-4">
        <Link to="/liens" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Liens
        </Link>
        <div className="p-8 text-center">
          <p className="text-sm text-red-600">{error || 'Lien not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3 md:gap-4 min-w-0 flex-1">
          <Link to="/liens" className="p-2 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 min-h-[44px] min-w-[44px] flex items-center justify-center">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="min-w-0 flex-1">
            <h1 className="text-base md:text-lg font-semibold text-slate-900 truncate">
              {lien.certificate_number || 'Lien Details'}
            </h1>
            <p className="text-sm text-slate-600 truncate">{lien.property_address}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <StatusBadge status={lien.status} />
          <Button size="sm" variant="secondary" className="flex-1 sm:flex-none min-h-[44px]">Edit</Button>
        </div>
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Main details */}
        <div className="lg:col-span-2 space-y-4 md:space-y-6">
          {/* Property Info */}
          <Card>
            <CardHeader>
              <CardTitle>Property Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <InfoItem
                  icon={MapPin}
                  label="Address"
                  value={lien.property_address || 'N/A'}
                />
                <InfoItem
                  icon={FileText}
                  label="Parcel ID"
                  value={lien.parcel_id || 'N/A'}
                />
                <InfoItem
                  label="County"
                  value={lien.county || 'N/A'}
                />
                <InfoItem
                  label="State"
                  value={lien.state || 'N/A'}
                />
              </div>
            </CardContent>
          </Card>

          {/* Financial Info */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <InfoItem
                  icon={DollarSign}
                  label="Purchase Amount"
                  value={`$${(lien.purchase_amount || 0).toLocaleString()}`}
                />
                <InfoItem
                  label="Interest Rate"
                  value={`${(lien.interest_rate || 0).toFixed(2)}%`}
                />
                <InfoItem
                  label="Premium"
                  value={`$${(lien.premium || 0).toLocaleString()}`}
                />
                <InfoItem
                  icon={Calendar}
                  label="Purchase Date"
                  value={lien.purchase_date ? format(new Date(lien.purchase_date), 'MMM d, yyyy') : 'N/A'}
                />
                <InfoItem
                  label="Redemption Deadline"
                  value={lien.redemption_deadline ? format(new Date(lien.redemption_deadline), 'MMM d, yyyy') : 'N/A'}
                />
                <InfoItem
                  label="Tax Year"
                  value={lien.tax_year || 'N/A'}
                />
              </div>
            </CardContent>
          </Card>

          {/* Payment History */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Payment History</CardTitle>
                <Button size="sm" variant="secondary">Record Payment</Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {payments.length === 0 ? (
                <div className="p-4 text-center text-sm text-slate-500">
                  No payments recorded
                </div>
              ) : (
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-xs font-medium text-slate-600 px-4 py-2">Date</th>
                      <th className="text-right text-xs font-medium text-slate-600 px-4 py-2">Amount</th>
                      <th className="text-left text-xs font-medium text-slate-600 px-4 py-2">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map((payment, index) => (
                      <tr key={index} className="border-b border-slate-100 last:border-0">
                        <td className="px-4 py-2 text-sm text-slate-900">
                          {payment.date ? format(new Date(payment.date), 'MMM d, yyyy') : '-'}
                        </td>
                        <td className="text-right px-4 py-2 text-sm font-medium text-slate-900">
                          ${(payment.amount || 0).toLocaleString()}
                        </td>
                        <td className="px-4 py-2 text-sm text-slate-600">
                          {payment.type || 'Payment'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4 md:space-y-6">
          <InterestCalculator
            lienId={id}
            faceValue={lien.purchase_amount || 0}
            interestRate={lien.interest_rate || 0}
          />

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="secondary" size="sm" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
              <Button variant="secondary" size="sm" className="w-full justify-start">
                <Calendar className="h-4 w-4 mr-2" />
                Set Deadline Reminder
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ icon: Icon, label, value }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-600 flex items-center gap-1">
        {Icon && <Icon className="h-3 w-3" />}
        {label}
      </p>
      <p className="mt-0.5 text-sm text-slate-900">{value}</p>
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
    <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${styles[status] || styles.active}`}>
      {status || 'active'}
    </span>
  );
}

export default LienDetailPage;
