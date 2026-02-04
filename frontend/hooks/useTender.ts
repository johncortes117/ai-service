/**
 * Custom hooks for tender operations using React Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { tenderAPI } from '@/lib/api';
import type { TenderDetails } from '@/lib/types';

/**
 * Hook to upload a tender
 */
export function useUploadTender() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (file: File) => tenderAPI.uploadTender(file),
        onSuccess: () => {
            // Invalidate tender queries to refetch the list
            queryClient.invalidateQueries({ queryKey: ['tender-details'] });
        },
    });
}

/**
 * Hook to get tender details
 */
export function useTenderDetails(tenderId: string | null, enabled = true) {
    return useQuery<TenderDetails>({
        queryKey: ['tender-details', tenderId],
        queryFn: () => tenderAPI.getTenderDetails(tenderId!),
        enabled: enabled && tenderId !== null,
    });
}

/**
 * Hook to get tender contractors
 */
export function useTenderContractors(tenderId: string | null, enabled = true) {
    return useQuery({
        queryKey: ['tender-contractors', tenderId],
        queryFn: () => tenderAPI.getTenderContractors(tenderId!),
        enabled: enabled && tenderId !== null,
    });
}
