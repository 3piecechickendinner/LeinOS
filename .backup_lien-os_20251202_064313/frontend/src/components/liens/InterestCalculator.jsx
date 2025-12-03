import React, { useState } from 'react';
import { Calculator } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import apiClient from '../../api/client';

export function InterestCalculator({ lienId, faceValue = 0, interestRate = 0 }) {
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleCalculate() {
    setCalculating(true);
    setError(null);
    try {
      const data = await apiClient.calculateInterest(lienId);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to calculate interest');
    } finally {
      setCalculating(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Interest Calculator</CardTitle>
          <Button
            size="sm"
            variant="secondary"
            onClick={handleCalculate}
            loading={calculating}
          >
            <Calculator className="h-4 w-4 mr-1" />
            Calculate
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Input values */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-slate-600">Face Value</p>
              <p className="text-lg font-semibold text-slate-900">
                ${faceValue.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600">Interest Rate</p>
              <p className="text-lg font-semibold text-slate-900">
                {interestRate.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Results */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {result && (
            <div className="pt-4 border-t border-slate-200 space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-slate-600">Days Held</p>
                  <p className="text-sm font-medium text-slate-900">
                    {result.days_held || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-600">
                    Accrued Interest
                  </p>
                  <p className="text-sm font-medium text-green-600">
                    ${(result.accrued_interest || 0).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
              </div>
              <div className="p-3 bg-slate-50 rounded-md">
                <p className="text-xs font-medium text-slate-600">Total Value</p>
                <p className="text-xl font-bold text-slate-900">
                  ${(result.total_value || 0).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              {result.calculation_date && (
                <p className="text-xs text-slate-500">
                  Calculated as of {new Date(result.calculation_date).toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {!result && !error && (
            <p className="text-xs text-slate-500">
              Click "Calculate" to compute current interest accrued
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default InterestCalculator;
