"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AnalysisProgressIndicator } from '@/components/layout/AnalysisProgressIndicator';
import { AnalysisDashboard } from '@/components/analysis/AnalysisDashboard';
import { useSSEStream } from '@/hooks/useSSEStream';
import { useStartAnalysis, useAnalysisReport } from '@/hooks/useAnalysis';
import { ChevronLeft, Play, AlertCircle } from 'lucide-react';
import type { SSEEvent, AnalysisReport } from '@/lib/types';

type AnalysisState = 'idle' | 'processing' | 'completed' | 'error';

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const tenderId = params.tenderId as string;

  const [analysisState, setAnalysisState] = useState<AnalysisState>('idle');
  const [analysisReport, setAnalysisReport] = useState<AnalysisReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const startAnalysisMutation = useStartAnalysis();
  const reportQuery = useAnalysisReport();

  // Connect to SSE stream
  useSSEStream({
    onMessage: (data: SSEEvent) => {
      // Only process events for this tender
      if (data.tenderId && data.tenderId !== tenderId) {
        return;
      }

      if (data.state === 'En Análisis') {
        setAnalysisState('processing');
      } else if (data.state === 'Completado') {
        setAnalysisState('completed');
        
        // Set the report data if it's in the SSE event
        if (data.executiveSummary && data.proposalsAnalysis) {
          setAnalysisReport({
            executiveSummary: data.executiveSummary,
            budgetComparison: data.budgetComparison || { categories: [], proposals: [] },
            proposalsAnalysis: data.proposalsAnalysis,
          });
        } else {
          // Fetch the report from the API
          reportQuery.refetch().then((result) => {
            if (result.data) {
              setAnalysisReport(result.data);
            }
          });
        }
      } else if (data.state === 'Error') {
        setAnalysisState('error');
        setErrorMessage(data.message || 'An error occurred during analysis');
      }
    },
    enabled: true,
  });

  const handleStartAnalysis = async () => {
    try {
      setErrorMessage('');
      await startAnalysisMutation.mutateAsync(tenderId);
      setAnalysisState('processing');
    } catch (error: any) {
      setAnalysisState('error');
      setErrorMessage(error.message || 'Failed to start analysis');
    }
  };

  const handleRetry = () => {
    setAnalysisState('idle');
    setErrorMessage('');
    setAnalysisReport(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      {analysisState !== 'completed' && (
        <div className="bg-white border-b sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => router.back()}
                  className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                >
                  <ChevronLeft className="w-5 h-5 text-gray-600" />
                </button>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    Tender Analysis
                  </h1>
                  <p className="text-sm text-gray-600">
                    Tender ID: <span className="font-mono">{tenderId}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      {analysisState === 'idle' && (
        <div className="max-w-2xl mx-auto px-6 py-20">
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100 text-center">
            <div className="w-16 h-16 rounded-full bg-blue-100 mx-auto mb-6 flex items-center justify-center">
              <Play className="w-8 h-8 text-blue-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Ready to Analyze
            </h2>
            <p className="text-gray-600 mb-6">
              Click the button below to start the AI analysis of all uploaded proposals.
              This process may take several minutes.
            </p>
            
            <button
              onClick={handleStartAnalysis}
              disabled={startAnalysisMutation.isPending}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {startAnalysisMutation.isPending ? 'Starting...' : 'Start Analysis'}
            </button>

            <div className="mt-8 pt-6 border-t text-left">
              <h3 className="font-semibold text-gray-900 mb-3">What happens next?</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex gap-2">
                  <span className="text-blue-600">1.</span>
                  <span>AI agents extract requirements from the tender document</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">2.</span>
                  <span>Each proposal is analyzed by specialized agents (Legal, Technical, Financial)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">3.</span>
                  <span>Compliance findings are generated and scored</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">4.</span>
                  <span>Results are aggregated into a comprehensive report</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {analysisState === 'processing' && (
        <AnalysisProgressIndicator tenderId={tenderId} />
      )}

      {analysisState === 'completed' && analysisReport && (
        <AnalysisDashboard report={analysisReport} />
      )}

      {analysisState === 'error' && (
        <div className="max-w-2xl mx-auto px-6 py-20">
          <div className="bg-white rounded-xl shadow-lg p-8 border border-red-200 text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 mx-auto mb-6 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Analysis Failed
            </h2>
            <p className="text-gray-600 mb-6">
              {errorMessage}
            </p>
            
            <button
              onClick={handleRetry}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
