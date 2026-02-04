"use client";

import { useSSEStream } from '@/hooks/useSSEStream';
import { useState } from 'react';
import type { SSEEvent } from '@/lib/types';

interface AnalysisProgressIndicatorProps {
  tenderId?: string;
}

export function AnalysisProgressIndicator({ tenderId }: AnalysisProgressIndicatorProps) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [message, setMessage] = useState('');

  useSSEStream({
    onMessage: (data: SSEEvent) => {
      if (data.tenderId === tenderId || !tenderId) {
        setProgress(data.currentProgress || 0);
        setCurrentStep(data.currentStep || '');
        setMessage(data.message || '');
      }
    },
    enabled: true,
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
      <div className="w-full max-w-md space-y-6">
        {/* Animated spinner */}
        <div className="flex justify-center">
          <div className="relative w-20 h-20">
            <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 rounded-full"></div>
            <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium text-gray-700">Analyzing...</span>
            <span className="text-gray-500">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Current step */}
        {currentStep && (
          <div className="text-center">
            <p className="text-sm font-medium text-gray-900">{currentStep}</p>
            {message && (
              <p className="text-xs text-gray-500 mt-1">{message}</p>
            )}
          </div>
        )}

        {/* Info text */}
        <div className="text-center text-sm text-gray-500">
          <p>This may take a few minutes depending on the number of proposals.</p>
          <p className="mt-1">Please do not close this window.</p>
        </div>
      </div>
    </div>
  );
}
