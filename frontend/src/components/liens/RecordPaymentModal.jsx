import React, { useState, useEffect } from 'react';
import { X, DollarSign, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input, Select } from '../ui/Input';

export function RecordPaymentModal({ isOpen, onClose, lienId, suggestedAmount = 0, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    amount: '',
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: 'Check',
    payer_name: '',
    reference_number: '',
    notes: '',
  });
  const [errors, setErrors] = useState({});

  // Pre-fill amount when modal opens
  useEffect(() => {
    if (isOpen && suggestedAmount > 0) {
      setFormData(prev => ({ ...prev, amount: suggestedAmount.toFixed(2) }));
    }
  }, [isOpen, suggestedAmount]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        amount: '',
        payment_date: new Date().toISOString().split('T')[0],
        payment_method: 'Check',
        payer_name: '',
        reference_number: '',
        notes: '',
      });
      setErrors({});
      setError('');
    }
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Amount must be greater than 0';
    }

    if (!formData.payment_date) {
      newErrors.payment_date = 'Payment date is required';
    }

    if (!formData.payment_method) {
      newErrors.payment_method = 'Payment method is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const paymentData = {
        amount: parseFloat(formData.amount),
        payment_date: formData.payment_date,
        payment_method: formData.payment_method,
        payer_name: formData.payer_name.trim() || null,
        reference_number: formData.reference_number.trim() || null,
        notes: formData.notes.trim() || null,
      };

      // Import apiClient dynamically
      const { default: apiClient } = await import('../../api/client');
      await apiClient.recordPayment(lienId, paymentData);

      // Success - call callback and close modal
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err) {
      console.error('Failed to record payment:', err);
      setError(err.message || 'Failed to record payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/50 z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">Record Payment</h2>
            <button
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 min-h-[44px] min-w-[44px] flex items-center justify-center"
              disabled={loading}
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Error message */}
          {error && (
            <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            {/* Amount */}
            <div>
              <Input
                label="Amount"
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                placeholder="5000.00"
                min="0"
                step="0.01"
                required
                error={errors.amount}
              />
              {suggestedAmount > 0 && (
                <p className="text-xs text-slate-500 mt-1">
                  Suggested from interest calculator: ${suggestedAmount.toLocaleString()}
                </p>
              )}
            </div>

            {/* Payment Date */}
            <div>
              <Input
                label="Payment Date"
                type="date"
                name="payment_date"
                value={formData.payment_date}
                onChange={handleChange}
                required
                error={errors.payment_date}
              />
            </div>

            {/* Payment Method */}
            <div>
              <Select
                label="Payment Method"
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
                required
                error={errors.payment_method}
                options={[
                  { value: 'Check', label: 'Check' },
                  { value: 'ACH', label: 'ACH Transfer' },
                  { value: 'Wire', label: 'Wire Transfer' },
                  { value: 'Cash', label: 'Cash' },
                  { value: 'Money Order', label: 'Money Order' },
                ]}
              />
            </div>

            {/* Payer Name (Optional) */}
            <div>
              <Input
                label="Payer Name (Optional)"
                type="text"
                name="payer_name"
                value={formData.payer_name}
                onChange={handleChange}
                placeholder="John Doe"
              />
            </div>

            {/* Reference Number (Optional) */}
            <div>
              <Input
                label="Reference Number (Optional)"
                type="text"
                name="reference_number"
                value={formData.reference_number}
                onChange={handleChange}
                placeholder="CHK-12345"
              />
            </div>

            {/* Notes (Optional) */}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Notes (Optional)
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Additional notes about this payment..."
                rows="3"
                className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-md placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Actions */}
            <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-end gap-3 pt-4 border-t border-slate-200">
              <Button
                type="button"
                variant="secondary"
                onClick={onClose}
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
                    Recording...
                  </>
                ) : (
                  <>
                    <DollarSign className="h-4 w-4 mr-2" />
                    Record Payment
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default RecordPaymentModal;
