// TypeScript types based on the backend API contract

export interface Finding {
    requirementName: string;
    isCompliant: boolean;
    severity: "OK" | "WARNING" | "CRITICAL";
    observation: string;
}

export interface ProposalScores {
    legal: number;
    technical: number;
    financial: number;
    viabilityTotal: number;
}

export interface FindingsSummary {
    total: number;
    critical: number;
    warning: number;
    ok: number;
}

export interface ProposalAnalysis {
    bidderName: string;
    scores: ProposalScores;
    findingsSummary: FindingsSummary;
    findings: Finding[];
}

export interface BudgetProposal {
    bidderName: string;
    valuesUSD: number[];
}

export interface BudgetComparison {
    categories: string[];
    proposals: BudgetProposal[];
}

export interface AnalysisReport {
    executiveSummary: string;
    budgetComparison: BudgetComparison;
    proposalsAnalysis: ProposalAnalysis[];
}

// SSE Event types
export interface SSEEvent {
    state: "En Análisis" | "Completado" | "Error";
    isLoading: boolean;
    tenderId?: string;
    currentProgress?: number;
    currentStep?: string;
    message?: string;
    lastUpdate?: string;
    // When completed, contains the full report
    executiveSummary?: string;
    budgetComparison?: BudgetComparison;
    proposalsAnalysis?: ProposalAnalysis[];
}

// API Response types
export interface TenderUploadResponse {
    message: string;
    tender_id: string;
    filename: string;
    file_path: string;
}

export interface ProposalUploadResponse {
    message: string;
    tender_id: string;
    contractor_id: string;
    company_name: string;
    company_directory: string;
    principal_file: string;
    attachments: string[];
    total_files: number;
}

export interface AnalysisStatusResponse {
    tender_id: string;
    status: "pending" | "processing" | "completed" | "failed";
    progress: number;
    current_step?: string;
    message: string;
    error_details?: string;
}

export interface TenderDetails {
    tenderId: string;
    tenderFile: string;
    totalApplications: number;
    applications: ContractorInfo[];
}

export interface ContractorInfo {
    contractor_id: string;
    company_name: string;
    total_files: number;
}

export interface ApplicationDetails {
    tender_id: string;
    contractor_id: string;
    company_name: string;
    files: {
        principal: string[];
        attachments: string[];
    };
    total_files: number;
}
