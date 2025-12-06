import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Select } from '../components/ui/Input';
import apiClient from '../api/client';
import { useVertical } from '../context/VerticalContext';

// Florida counties for dropdown
const FLORIDA_COUNTIES = [
  'Miami-Dade', 'Broward', 'Palm Beach', 'Hillsborough', 'Orange',
  'Pinellas', 'Duval', 'Lee', 'Polk', 'Brevard', 'Volusia',
  'Pasco', 'Seminole', 'Sarasota', 'Manatee', 'Lake', 'Collier',
  'Marion', 'Osceola', 'St. Lucie', 'Escambia', 'Hernando'
].sort();

export function AddAssetPage() {
  const navigate = useNavigate();
  const { currentVertical } = useVertical();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Unified form state
  const [formData, setFormData] = useState({
    // Common
    county: '',
    status: 'ACTIVE',

    // Tax Lien specific
    certificate_number: '',
    purchase_amount: '',
    interest_rate: '',
    sale_date: '',
    redemption_deadline: '',
    property_address: '',
    parcel_id: '',

    // Civil Judgment specific
    case_number: '',
    court_name: '',
    judgment_date: '',
    defendant_name: '',
    judgment_amount: '',
  });

  const [errors, setErrors] = useState({});

  // Reset form when vertical changes
  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      certificate_number: '',
      purchase_amount: '',
      interest_rate: '',
      sale_date: '',
      redemption_deadline: '',
      property_address: '',
      parcel_id: '',
      case_number: '',
      court_name: '',
      judgment_date: '',
      defendant_name: '',
      judgment_amount: '',
      county: '',
    }));
    setErrors({});
  }, [currentVertical]);

  // Auto-calculate redemption deadline (2 years from sale date)
  const handleSaleDateChange = (e) => {
    const saleDate = e.target.value;
    setFormData((prev) => ({ ...prev, sale_date: saleDate }));

    if (saleDate && currentVertical === 'tax_lien') {
      const sale = new Date(saleDate);
      sale.setFullYear(sale.getFullYear() + 2);
      const redemptionDate = sale.toISOString().split('T')[0];
      setFormData((prev) => ({ ...prev, redemption_deadline: redemptionDate }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (currentVertical === 'tax_lien') {
      if (!formData.certificate_number.trim()) newErrors.certificate_number = 'Certificate number is required';
      if (!formData.purchase_amount || parseFloat(formData.purchase_amount) <= 0) newErrors.purchase_amount = 'Purchase amount must be greater than 0';
      if (!formData.interest_rate) {
        newErrors.interest_rate = 'Interest rate is required';
      } else {
        const rate = parseFloat(formData.interest_rate);
        if (rate < 0 || rate > 100) newErrors.interest_rate = 'Interest rate must be between 0 and 100';
      }
      if (!formData.sale_date) newErrors.sale_date = 'Sale date is required';
      if (!formData.redemption_deadline) newErrors.redemption_deadline = 'Redemption deadline is required';
      if (!formData.property_address.trim()) newErrors.property_address = 'Property address is required';
      if (!formData.parcel_id.trim()) newErrors.parcel_id = 'Parcel ID is required';
    } else {
      // Civil Judgment validation
      if (!formData.case_number.trim()) newErrors.case_number = 'Case number is required';
      if (!formData.court_name.trim()) newErrors.court_name = 'Court name is required';
      if (!formData.judgment_date) newErrors.judgment_date = 'Judgment date is required';
      if (!formData.defendant_name.trim()) newErrors.defendant_name = 'Defendant name is required';
      if (!formData.judgment_amount || parseFloat(formData.judgment_amount) <= 0) newErrors.judgment_amount = 'Judgment amount must be greater than 0';
    }

    if (!formData.county.trim()) newErrors.county = 'County is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setLoading(true);

    try {
      if (currentVertical === 'tax_lien') {
        const lienData = {
          certificate_number: formData.certificate_number.trim(),
          purchase_amount: parseFloat(formData.purchase_amount),
          interest_rate: parseFloat(formData.interest_rate),
          sale_date: formData.sale_date,
          redemption_deadline: formData.redemption_deadline,
          county: formData.county.trim(),
          property_address: formData.property_address.trim(),
          parcel_id: formData.parcel_id.trim(),
          status: 'ACTIVE',
        };
        await apiClient.createLien(lienData);
      } else {
        const judgmentData = {
          case_number: formData.case_number.trim(),
          court_name: formData.court_name.trim(),
          judgment_date: formData.judgment_date,
          defendant_name: formData.defendant_name.trim(),
          judgment_amount: parseFloat(formData.judgment_amount),
          county: formData.county.trim(),
          status: 'ACTIVE',
        };
        await apiClient.createJudgment(judgmentData);
      }

      navigate('/liens');
    } catch (err) {
      console.error('Failed to create asset:', err);
      setError(err.message || 'Failed to create asset. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6 max-w-4xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/liens')}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 min-h-[44px] min-w-[44px] flex items-center justify-center"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <h1 className="text-lg md:text-xl font-semibold text-slate-900">
            Add New {currentVertical === 'tax_lien' ? 'Lien' : 'Judgment'}
          </h1>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>{currentVertical === 'tax_lien' ? 'Lien Information' : 'Judgment Information'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* Common Fields */}
              <div className="md:col-span-2">
                <Select
                  label="County"
                  name="county"
                  value={formData.county}
                  onChange={handleChange}
                  required
                  error={errors.county}
                  options={[
                    { value: '', label: 'Select a county' },
                    ...FLORIDA_COUNTIES.map((county) => ({
                      value: county,
                      label: county,
                    })),
                  ]}
                />
              </div>

              {currentVertical === 'tax_lien' ? (
                <>
                  <div className="md:col-span-2">
                    <Input
                      label="Certificate Number"
                      name="certificate_number"
                      value={formData.certificate_number}
                      onChange={handleChange}
                      placeholder="MD-2024-1234"
                      required
                      error={errors.certificate_number}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Input
                      label="Property Address"
                      name="property_address"
                      value={formData.property_address}
                      onChange={handleChange}
                      placeholder="123 Main St, Miami, FL 33130"
                      required
                      error={errors.property_address}
                    />
                  </div>
                  <div>
                    <Input
                      label="Parcel ID"
                      name="parcel_id"
                      value={formData.parcel_id}
                      onChange={handleChange}
                      placeholder="01-3245-067-0890"
                      required
                      error={errors.parcel_id}
                    />
                  </div>
                  <div>
                    <Input
                      label="Purchase Amount"
                      type="number"
                      name="purchase_amount"
                      value={formData.purchase_amount}
                      onChange={handleChange}
                      placeholder="5000"
                      min="0"
                      step="0.01"
                      required
                      error={errors.purchase_amount}
                    />
                  </div>
                  <div>
                    <Input
                      label="Interest Rate (%)"
                      type="number"
                      name="interest_rate"
                      value={formData.interest_rate}
                      onChange={handleChange}
                      placeholder="18"
                      min="0"
                      max="100"
                      step="0.01"
                      required
                      error={errors.interest_rate}
                    />
                  </div>
                  <div>
                    <Input
                      label="Sale Date"
                      type="date"
                      name="sale_date"
                      value={formData.sale_date}
                      onChange={handleSaleDateChange}
                      required
                      error={errors.sale_date}
                    />
                  </div>
                  <div>
                    <Input
                      label="Redemption Deadline"
                      type="date"
                      name="redemption_deadline"
                      value={formData.redemption_deadline}
                      onChange={handleChange}
                      required
                      error={errors.redemption_deadline}
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Auto-calculated as 2 years from sale date
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="md:col-span-2">
                    <Input
                      label="Case Number"
                      name="case_number"
                      value={formData.case_number}
                      onChange={handleChange}
                      placeholder="CASE-2024-001"
                      required
                      error={errors.case_number}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Input
                      label="Court Name"
                      name="court_name"
                      value={formData.court_name}
                      onChange={handleChange}
                      placeholder="Circuit Court"
                      required
                      error={errors.court_name}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Input
                      label="Defendant Name"
                      name="defendant_name"
                      value={formData.defendant_name}
                      onChange={handleChange}
                      placeholder="John Doe"
                      required
                      error={errors.defendant_name}
                    />
                  </div>
                  <div>
                    <Input
                      label="Judgment Amount"
                      type="number"
                      name="judgment_amount"
                      value={formData.judgment_amount}
                      onChange={handleChange}
                      placeholder="5000"
                      min="0"
                      step="0.01"
                      required
                      error={errors.judgment_amount}
                    />
                  </div>
                  <div>
                    <Input
                      label="Judgment Date"
                      type="date"
                      name="judgment_date"
                      value={formData.judgment_date}
                      onChange={handleChange}
                      required
                      error={errors.judgment_date}
                    />
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-end gap-3 mt-6">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/liens')}
            disabled={loading}
            className="w-full sm:w-auto min-h-[44px]"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto min-h-[44px]"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Create {currentVertical === 'tax_lien' ? 'Lien' : 'Judgment'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

export default AddAssetPage;
