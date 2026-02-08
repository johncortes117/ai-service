"use client";

import { useState } from 'react';
import type { AnalysisReport } from '@/lib/types';
import { ScoreCard } from './ScoreCard';
import { FindingsTable } from './FindingsTable';
import { RadarScoreChart } from '../charts/RadarScoreChart';
import { FindingsPieChart } from '../charts/FindingsPieChart';
import { CHART_COLORS } from '@/lib/chart-utils';
import { Award, ChevronDown, ChevronUp } from 'lucide-react';

interface AnalysisDashboardProps {
  report: AnalysisReport;
}

export function AnalysisDashboard({ report }: AnalysisDashboardProps) {
  const { executiveSummary, proposalsAnalysis } = report;

  // Find best proposal by viability score and its index
  const bestProposalIndex = proposalsAnalysis.reduce((bestIdx, current, currentIdx, arr) => 
    current.scores.viabilityTotal > arr[bestIdx].scores.viabilityTotal ? currentIdx : bestIdx
  , 0);

  const [selectedProposalIndex, setSelectedProposalIndex] = useState(bestProposalIndex);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  
  const selectedProposal = proposalsAnalysis[selectedProposalIndex];
  const bestProposal = proposalsAnalysis[bestProposalIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        
        {/* Compact Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm px-6 py-4">
          <h1 className="text-2xl font-bold text-white">
            Tender Analysis Report
          </h1>
          <p className="text-sm text-blue-100 mt-1">
            AI-powered analysis of {proposalsAnalysis.length} proposals
          </p>
        </div>

        {/* Collapsible Executive Summary */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <button
            onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-gray-900">
                Executive Summary
              </h2>
              <span className="text-xs text-gray-500 font-medium">
                {isSummaryExpanded ? 'Click to collapse' : 'Click to expand'}
              </span>
            </div>
            {isSummaryExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {isSummaryExpanded && (
            <div className="px-6 pb-6 border-t border-gray-100">
              <div className="mt-4 mb-4">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {executiveSummary}
                </p>
              </div>
              
              {/* Best Proposal Highlight - Always visible when expanded */}
              <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg">
                <div className="flex items-center gap-3">
                  <Award className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-green-900 mb-1">
                      Recommended Proposal
                    </p>
                    <p className="text-sm text-green-800">
                      <span className="font-bold">{bestProposal.bidderName}</span>
                      {' '}with a viability score of{' '}
                      <span className="font-bold">{bestProposal.scores.viabilityTotal}/100</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Condensed recommended proposal when collapsed */}
          {!isSummaryExpanded && (
            <div className="px-6 pb-4">
              <div className="flex items-center gap-2 text-sm">
                <Award className="w-4 h-4 text-green-600" />
                <span className="text-gray-600">Recommended:</span>
                <span className="font-semibold text-gray-900">{bestProposal.bidderName}</span>
                <span className="text-gray-500">({bestProposal.scores.viabilityTotal}/100)</span>
              </div>
            </div>
          )}
        </div>

        {/* Proposals Comparison Cards */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Proposals Comparison
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {proposalsAnalysis.map((proposal, index) => (
              <ScoreCard
                key={index}
                proposal={proposal}
                onClick={() => setSelectedProposalIndex(index)}
                isSelected={index === selectedProposalIndex}
              />
            ))}
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Radar Chart for Selected Proposal */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-gray-900">
                Score Breakdown
              </h3>
              <select
                value={selectedProposalIndex}
                onChange={(e) => setSelectedProposalIndex(Number(e.target.value))}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                {proposalsAnalysis.map((proposal, index) => (
                  <option key={index} value={index}>
                    {proposal.bidderName}
                  </option>
                ))}
              </select>
            </div>
            <RadarScoreChart
              scores={selectedProposal.scores}
              bidderName={selectedProposal.bidderName}
              color={CHART_COLORS[selectedProposalIndex % CHART_COLORS.length]}
            />
          </div>

          {/* Findings Distribution Pie Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-bold text-gray-900 mb-4">
              Findings Distribution - {selectedProposal.bidderName}
            </h3>
            <div className="flex items-center justify-center">
              <FindingsPieChart findingsSummary={selectedProposal.findingsSummary} />
            </div>
          </div>
        </div>

        {/* Detailed Findings Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">
            Detailed Findings - {selectedProposal.bidderName}
          </h3>
          <FindingsTable findings={selectedProposal.findings} />
        </div>
        
      </div>
    </div>
  );
}
