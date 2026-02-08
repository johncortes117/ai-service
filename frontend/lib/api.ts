/**
 * API Client for TenderAnalyzer Backend
 * Base URL should be configured via environment variable
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

/**
 * Tender API endpoints
 */
export const tenderAPI = {
    /**
     * Upload a tender PDF
     */
    uploadTender: async (file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/tenders/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Failed to upload tender');
        }

        return response.json();
    },

    /**
     * Get tender details
     */
    getTenderDetails: async (tenderId: string): Promise<any> => {
        return fetchAPI(`/tenders/${tenderId}`);
    },

    /**
     * Get all contractors for a tender
     */
    getTenderContractors: async (tenderId: string): Promise<any> => {
        return fetchAPI(`/tenders/${tenderId}/contractors`);
    },
};

/**
 * Proposal API endpoints
 */
export const proposalAPI = {
    /**
     * Upload proposal files
     */
    uploadProposal: async (
        tenderId: string,
        contractorId: string,
        companyName: string,
        ruc: string,
        principalFile: File,
        attachments: File[]
    ): Promise<any> => {
        const formData = new FormData();
        formData.append('principal_file', principalFile);
        attachments.forEach(file => formData.append('attachment_files', file));

        const response = await fetch(
            `${API_BASE}/proposals/upload/${tenderId}/${contractorId}/${companyName}/${ruc}`,
            {
                method: 'POST',
                body: formData,
            }
        );

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Failed to upload proposal');
        }

        return response.json();
    },

    /**
     * Get application details
     */
    getApplicationDetails: async (tenderId: string, proposalId: string): Promise<any> => {
        return fetchAPI(`/tenders/${tenderId}/applications/${proposalId}`);
    },
};

/**
 * Analysis API endpoints
 */
export const analysisAPI = {
    /**
     * Start analysis for a tender
     */
    startAnalysis: async (tenderId: string): Promise<any> => {
        return fetchAPI(`/tenders/${tenderId}/analyze`, {
            method: 'POST',
        });
    },

    /**
     * Get analysis status for a specific tender
     */
    getAnalysisStatus: async (tenderId: string): Promise<any> => {
        return fetchAPI(`/tenders/${tenderId}/analysis/status`);
    },

    /**
     * Get current global analysis status
     */
    getCurrentStatus: async (): Promise<any> => {
        return fetchAPI(`/analysis/current-status`);
    },

    /**
     * Get the latest analysis report
     */
    getAnalysisReport: async (): Promise<any> => {
        return fetchAPI(`/get-analysis-report`);
    },
};

/**
 * SSE Stream URL
 */
export const SSE_STREAM_URL = `${API_BASE}/sse/stream`;
