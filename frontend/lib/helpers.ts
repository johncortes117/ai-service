/**
 * Custom helper functions for the TenderAnalyzer application
 */

/**
 * Format a number as USD currency
 */
export function formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(value)
}

/**
 * Format a date string to a readable format
 */
export function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    })
}

/**
 * Get color based on severity
 */
export function getSeverityColor(severity: "OK" | "WARNING" | "CRITICAL"): string {
    switch (severity) {
        case "OK":
            return "text-green-600 bg-green-50 border-green-200"
        case "WARNING":
            return "text-yellow-600 bg-yellow-50 border-yellow-200"
        case "CRITICAL":
            return "text-red-600 bg-red-50 border-red-200"
    }
}

/**
 * Get badge variant based on severity
 */
export function getSeverityVariant(severity: "OK" | "WARNING" | "CRITICAL"): "default" | "secondary" | "destructive" {
    switch (severity) {
        case "OK":
            return "secondary"
        case "WARNING":
            return "default"
        case "CRITICAL":
            return "destructive"
    }
}

/**
 * Get color for viability score
 */
export function getViabilityColor(score: number): string {
    if (score >= 85) return "text-green-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
}

/**
 * Get background color for viability score
 */
export function getViabilityBgColor(score: number): string {
    if (score >= 85) return "bg-green-100"
    if (score >= 70) return "bg-yellow-100"
    return "bg-red-100"
}

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + "..."
}

/**
 * Calculate percentage
 */
export function calculatePercentage(value: number, total: number): number {
    if (total === 0) return 0
    return Math.round((value / total) * 100)
}
