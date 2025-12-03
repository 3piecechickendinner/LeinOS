import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

const defaultData = [
  { month: 'Jan', revenue: 4000, interest: 2400 },
  { month: 'Feb', revenue: 3000, interest: 1398 },
  { month: 'Mar', revenue: 2000, interest: 9800 },
  { month: 'Apr', revenue: 2780, interest: 3908 },
  { month: 'May', revenue: 1890, interest: 4800 },
  { month: 'Jun', revenue: 2390, interest: 3800 },
];

export function RevenueChart({ data = defaultData, title = 'Revenue & Interest' }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '12px',
                }}
                formatter={(value) => [`$${value}`, '']}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stackId="1"
                stroke="#3b82f6"
                fill="#93c5fd"
                name="Revenue"
              />
              <Area
                type="monotone"
                dataKey="interest"
                stackId="1"
                stroke="#10b981"
                fill="#6ee7b7"
                name="Interest"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export default RevenueChart;
