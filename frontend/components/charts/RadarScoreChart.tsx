"use client";

import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
} from 'recharts';
import { transformScoresForRadar } from '@/lib/chart-utils';
import type { ProposalScores } from '@/lib/types';

interface RadarScoreChartProps {
  scores: ProposalScores;
  bidderName: string;
  color?: string;
}

export function RadarScoreChart({ scores, bidderName, color = '#2563eb' }: RadarScoreChartProps) {
  const data = transformScoresForRadar(scores);

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#6b7280', fontSize: 10 }}
          />
          <Radar
            name={bidderName}
            dataKey="score"
            stroke={color}
            fill={color}
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              padding: '8px 12px',
            }}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
