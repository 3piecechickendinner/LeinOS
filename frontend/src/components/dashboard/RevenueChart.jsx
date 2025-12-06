import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

export function RevenueChart({ currentVertical }) {
  // 1. DYNAMIC DATA GENERATOR
  const getChartData = () => {
    switch (currentVertical) {
      case 'civil_judgment':
        return [
          { name: 'Jan', value: 12000 }, { name: 'Feb', value: 19000 },
          { name: 'Mar', value: 15000 }, { name: 'Apr', value: 22000 },
          { name: 'May', value: 28000 }, { name: 'Jun', value: 25000 },
        ];
      case 'mineral_rights':
        return [
          { name: 'Jan', value: 4500 }, { name: 'Feb', value: 5200 },
          { name: 'Mar', value: 4800 }, { name: 'Apr', value: 6100 },
          { name: 'May', value: 5900 }, { name: 'Jun', value: 7200 },
        ];
      case 'probate':
        return [
          { name: 'Jan', value: 0 }, { name: 'Feb', value: 150000 },
          { name: 'Mar', value: 0 }, { name: 'Apr', value: 0 },
          { name: 'May', value: 210000 }, { name: 'Jun', value: 0 },
        ];
      case 'surplus_funds':
        return [
          { name: 'Jan', value: 8500 }, { name: 'Feb', value: 2000 },
          { name: 'Mar', value: 12000 }, { name: 'Apr', value: 5000 },
          { name: 'May', value: 18000 }, { name: 'Jun', value: 9000 },
        ];
      default: // tax_lien
        return [
          { name: 'Jan', value: 4000 }, { name: 'Feb', value: 3000 },
          { name: 'Mar', value: 2000 }, { name: 'Apr', value: 2780 },
          { name: 'May', value: 1890 }, { name: 'Jun', value: 2390 },
        ];
    }
  };

  // 2. DYNAMIC TITLES
  const getTitle = () => {
    const titles = {
      civil_judgment: 'Monthly Collections (Garnishments)',
      mineral_rights: 'Royalty Income Stream',
      probate: 'Estate Liquidation Events',
      surplus_funds: 'Recovered Surplus Fees',
      tax_lien: 'Redemption Revenue'
    };
    return titles[currentVertical] || 'Revenue';
  };

  const data = getChartData();

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>{getTitle()}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="name"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                cursor={{ fill: 'transparent' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar
                dataKey="value"
                fill="#2563eb"
                radius={[4, 4, 0, 0]}
                barSize={40}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export default RevenueChart;