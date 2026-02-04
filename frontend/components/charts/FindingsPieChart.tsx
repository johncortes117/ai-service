"use client";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
} from 'recharts';
import { transformFindingsForPie } from '@/lib/chart-utils';
import type { FindingsSummary } from '@/lib/types';

interface FindingsPieChartProps {
  findingsSummary: FindingsSummary;
}

export function FindingsPieChart({ findingsSummary }: FindingsPieChartProps) {
  const data = transformFindingsForPie(findingsSummary);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const { name, value } = payload[0];
      const total = findingsSummary.total;
      const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-md shadow-sm">
          <p className="text-sm font-semibold text-gray-900">{name}</p>
          <p className="text-sm text-gray-600">
            {value} findings ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  const renderLabel = (entry: any) => {
    const percentage = findingsSummary.total > 0 
      ? Math.round((entry.value / findingsSummary.total) * 100) 
      : 0;
    return `${percentage}%`;
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderLabel}
            outerRadius={100}
            innerRadius={60}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
