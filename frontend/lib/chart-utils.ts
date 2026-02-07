/**
 * Chart data transformation utilities
 */

import type { BudgetComparison, ProposalScores, FindingsSummary } from './types';

/**
 * Transform budget comparison data for Bar Chart
 */
export function transformBudgetForBarChart(budgetComparison: BudgetComparison) {
    // Handle undefined or missing data
    if (!budgetComparison || !budgetComparison.categories || !budgetComparison.proposals) {
        return [];
    }

    const { categories, proposals } = budgetComparison;

    return categories.map((category, idx) => ({
        category,
        ...proposals.reduce((acc, proposal) => ({
            ...acc,
            [proposal.bidderName]: proposal.valuesUSD[idx] || 0
        }), {})
    }));
}

/**
 * Transform proposal scores for Radar Chart
 */
export function transformScoresForRadar(scores: ProposalScores) {
    return [
        { category: 'Legal', score: scores.legal, fullMark: 100 },
        { category: 'Technical', score: scores.technical, fullMark: 100 },
        { category: 'Financial', score: scores.financial, fullMark: 100 },
    ];
}

/**
 * Transform findings summary for Pie/Donut Chart
 */
export function transformFindingsForPie(findingsSummary: FindingsSummary) {
    return [
        { name: 'OK', value: findingsSummary.ok, fill: '#22c55e' },
        { name: 'WARNING', value: findingsSummary.warning, fill: '#f59e0b' },
        { name: 'CRITICAL', value: findingsSummary.critical, fill: '#ef4444' },
    ];
}

/**
 * Colors for charts - consistent palette
 */
export const CHART_COLORS = [
    '#2563eb', // Blue
    '#8b5cf6', // Purple
    '#ec4899', // Pink
    '#f59e0b', // Amber
    '#10b981', // Green
    '#06b6d4', // Cyan
    '#f97316', // Orange
    '#6366f1', // Indigo
];

/**
 * Get color by index for consistent proposal coloring
 */
export function getProposalColor(index: number): string {
    return CHART_COLORS[index % CHART_COLORS.length];
}
