"use client";

import type { ProposalAnalysis } from '@/lib/types';
import { getViabilityColor, getViabilityBgColor } from '@/lib/helpers';
import { cn } from '@/lib/utils';

interface ScoreCardProps {
  proposal: ProposalAnalysis;
  onClick?: () => void;
  isSelected?: boolean;
}

export function ScoreCard({ proposal, onClick, isSelected = false }: ScoreCardProps) {
  const { bidderName, scores, findingsSummary } = proposal;
  const { viabilityTotal, legal, technical, financial } = scores;

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusBadge = (score: number) => {
    if (score >= 85) return { label: 'Viable', className: 'bg-green-100 text-green-800' };
    if (score >= 70) return { label: 'Risky', className: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Not Viable', className: 'bg-red-100 text-red-800' };
  };

  const status = getStatusBadge(viabilityTotal);

  return (
    <div
      onClick={onClick}
      className={cn(
        "relative p-5 rounded-lg border-2 bg-white shadow-sm transition-all cursor-pointer",
        isSelected 
          ? "border-blue-500 shadow-md ring-2 ring-blue-200" 
          : "border-gray-200 hover:border-blue-300 hover:shadow-md"
      )}
    >
      {/* Header with company name and status badge */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{bidderName}</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {findingsSummary.total} findings
          </p>
        </div>
        <span className={cn(
          "px-2 py-0.5 rounded-full text-xs font-medium",
          status.className
        )}>
          {status.label}
        </span>
      </div>

      {/* Viability Score - Reduced size */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-2">
          <span className={cn("text-3xl font-bold", getViabilityColor(viabilityTotal))}>
            {viabilityTotal}
          </span>
          <span className="text-gray-500 text-xs">/100</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className={cn("h-1.5 rounded-full transition-all", getScoreColor(viabilityTotal))}
            style={{ width: `${viabilityTotal}%` }}
          />
        </div>
      </div>

      {/* Score breakdown */}
      <div className="space-y-2.5">
        <ScoreBar label="Legal" score={legal} />
        <ScoreBar label="Technical" score={technical} />
        <ScoreBar label="Financial" score={financial} />
      </div>

      {/* Findings summary */}
      <div className="mt-3 pt-3 border-t flex gap-3 text-xs">
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
          <span className="text-gray-600">{findingsSummary.critical} Critical</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
          <span className="text-gray-600">{findingsSummary.warning} Warning</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
          <span className="text-gray-600">{findingsSummary.ok} OK</span>
        </div>
      </div>
    </div>
  );
}

interface ScoreBarProps {
  label: string;
  score: number;
}

function ScoreBar({ label, score }: ScoreBarProps) {
  const getColor = (score: number) => {
    if (score >= 85) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2.5">
      <span className="text-xs font-medium text-gray-700 w-16">{label}</span>
      <div className="flex-1 bg-gray-200 rounded-full h-1.5">
        <div
          className={cn("h-1.5 rounded-full transition-all", getColor(score))}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-gray-900 w-7 text-right">{score}</span>
    </div>
  );
}
