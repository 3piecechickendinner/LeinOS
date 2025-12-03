import React from 'react';
import { Card, CardContent } from '../ui/Card';

export function StatsCard({ title, value, change, changeType, icon: Icon }) {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium text-slate-600">{title}</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
            {change && (
              <p className={`mt-1 text-xs ${
                changeType === 'positive' ? 'text-green-600' :
                changeType === 'negative' ? 'text-red-600' : 'text-slate-500'
              }`}>
                {change}
              </p>
            )}
          </div>
          {Icon && (
            <div className="p-2 bg-slate-100 rounded-md">
              <Icon className="h-4 w-4 text-slate-600" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default StatsCard;
