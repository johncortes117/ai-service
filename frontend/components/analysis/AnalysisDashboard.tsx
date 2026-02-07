"use client";

import { useState } from 'react';
import type { AnalysisReport } from '@/lib/types';
import { ScoreCard } from './ScoreCard';
import { FindingsTable } from './FindingsTable';
import { RadarScoreChart } from '../charts/RadarScoreChart';
import { BudgetComparisonChart } from '../charts/BudgetComparisonChart';
import { FindingsPieChart } from '../charts/FindingsPieChart';
import { CHART_COLORS } from '@/lib/chart-utils';

interface AnalysisDashboardProps {
  report: AnalysisReport;
}

export function AnalysisDashboard({ report }: AnalysisDashboardProps) {
  const [selectedProposalIndex, setSelectedProposalIndex] = useState(0);
  
  const { executiveSummary, budgetComparison, proposalsAnalysis } = report;
  const selectedProposal = proposalsAnalysis[selectedProposalIndex];

  // Find best proposal by viability score
  const bestProposal = proposalsAnalysis.reduce((best, current) => 
    current.scores.viabilityTotal > best.scores.viabilityTotal ? current : best
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg border p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Tender Analysis Report
          </h1>
          <p className="text-gray-600">
            Comprehensive analysis of {proposalsAnalysis.length} proposals
          </p>
        </div>

        {/* Executive Summary */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Executive Summary
          </h2>
          <div className="prose prose-sm max-w-none">
            <div className="whitespace-pre-wrap text-gray-700">
              {executiveSummary}
            </div>
          </div>
          
          {/* Best Proposal Highlight */}
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm font-medium text-green-900">
              🏆 Recommended: <span className="font-bold">{bestProposal.bidderName}</span> with a viability score of {bestProposal.scores.viabilityTotal}/100
            </p>
          </div>
        </div>

        {/* Proposals Grid */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Proposals Comparison
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {proposalsAnalysis.map((proposal, index) => (
              <ScoreCard
                key={index}
                proposal={proposal}
                onClick={() => setSelectedProposalIndex(index)}
              />
            ))}
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Budget Comparison */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Budget Comparison
            </h3>
            <BudgetComparisonChart budgetComparison={budgetComparison} />
          </div>

          {/* Radar Chart for Selected Proposal */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Score Breakdown
              </h3>
              <select
                value={selectedProposalIndex}
                onChange={(e) => setSelectedProposalIndex(Number(e.target.value))}
                className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        </div>

        {/* Findings Distribution for Selected Proposal */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Findings Distribution - {selectedProposal.bidderName}
          </h3>
          <div className="max-w-md mx-auto">
            <FindingsPieChart findingsSummary={selectedProposal.findingsSummary} />
          </div>
        </div>

        {/* Detailed Findings Table */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Detailed Findings - {selectedProposal.bidderName}
          </h3>
          <FindingsTable findings={selectedProposal.findings} />
        </div>

        {/* Comparison Table */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Comparison
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                    Company
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                    Viability
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                    Legal
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                    Technical
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                    Financial
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                    Critical Issues
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {proposalsAnalysis.map((proposal, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedProposalIndex(index)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {proposal.bidderName}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="text-lg font-bold text-blue-600">
                        {proposal.scores.viabilityTotal}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {proposal.scores.legal}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {proposal.scores.technical}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {proposal.scores.financial}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {proposal.findingsSummary.critical}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
