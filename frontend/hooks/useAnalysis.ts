/**
 * Custom hooks for analysis operations using React Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { analysisAPI } from '@/lib/api';
import type { AnalysisReport, AnalysisStatusResponse } from '@/lib/types';

/**
 * Hook to start analysis for a tender
 */
export function useStartAnalysis() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (tenderId: string) => analysisAPI.startAnalysis(tenderId),
        onSuccess: () => {
            // Invalidate analysis-related queries
            queryClient.invalidateQueries({ queryKey: ['analysis-status'] });
            queryClient.invalidateQueries({ queryKey: ['current-status'] });
        },
    });
}

/**
 * Hook to get analysis status for a specific tender
 */
export function useAnalysisStatus(tenderId: string | null, enabled = true) {
    return useQuery<AnalysisStatusResponse>({
        queryKey: ['analysis-status', tenderId],
        queryFn: () => analysisAPI.getAnalysisStatus(tenderId!),
        enabled: enabled && tenderId !== null,
        refetchInterval: (data) => {
            // Stop polling if completed or failed
            if (data?.status === 'completed' || data?.status === 'failed') {
                return false;
            }
            // Poll every 3 seconds while processing
            return 3000;
        },
    });
}

/**
 * Hook to get current global analysis status
 */
export function useCurrentAnalysisStatus(enabled = true) {
    return useQuery({
        queryKey: ['current-status'],
        queryFn: () => analysisAPI.getCurrentStatus(),
        enabled,
        refetchInterval: 5000, // Poll every 5 seconds
    });
}

/**
 * Hook to get the latest analysis report
 */
export function useAnalysisReport() {
    return useQuery<AnalysisReport>({
        queryKey: ['analysis-report'],
        queryFn: () => analysisAPI.getAnalysisReport(),
        enabled: false, // Only fetch manually
        staleTime: 0, // Always fetch fresh data when requested
    });
}
