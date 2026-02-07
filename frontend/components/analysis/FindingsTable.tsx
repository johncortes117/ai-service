"use client";

import { useState, useMemo } from 'react';
import type { Finding } from '@/lib/types';
import { getSeverityColor } from '@/lib/helpers';
import { cn } from '@/lib/utils';

interface FindingsTableProps {
  findings: Finding[];
}

type SeverityFilter = 'ALL' | 'OK' | 'WARNING' | 'CRITICAL';

export function FindingsTable({ findings }: FindingsTableProps) {
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('ALL');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const filteredFindings = useMemo(() => {
    if (severityFilter === 'ALL') return findings;
    return findings.filter(f => f.severity === severityFilter);
  }, [findings, severityFilter]);

  const severityCounts = useMemo(() => {
    return {
      ALL: findings.length,
      OK: findings.filter(f => f.severity === 'OK').length,
      WARNING: findings.filter(f => f.severity === 'WARNING').length,
      CRITICAL: findings.filter(f => f.severity === 'CRITICAL').length,
    };
  }, [findings]);

  const getSeverityBadge = (severity: Finding['severity']) => {
    const colors = {
      OK: 'bg-green-100 text-green-800 border-green-200',
      WARNING: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
    };

    return (
      <span className={cn('px-2.5 py-1 rounded-md text-xs font-semibold border', colors[severity])}>
        {severity}
      </span>
    );
  };

  const FilterButton = ({ filter, label }: { filter: SeverityFilter; label: string }) => (
    <button
      onClick={() => setSeverityFilter(filter)}
      className={cn(
        'px-4 py-2 text-sm font-medium rounded-md transition-colors',
        severityFilter === filter
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      )}
    >
      {label} ({severityCounts[filter]})
    </button>
  );

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        <FilterButton filter="ALL" label="All" />
        <FilterButton filter="CRITICAL" label="Critical" />
        <FilterButton filter="WARNING" label="Warning" />
        <FilterButton filter="OK" label="OK" />
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden bg-white">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-1/3">
                  Requirement
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-24">
                  Severity
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-24">
                  Compliant
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Observation
                </th>
                <th className="px-4 py-3 w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredFindings.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No findings match the selected filter
                  </td>
                </tr>
              ) : (
                filteredFindings.map((finding, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {finding.requirementName}
                    </td>
                    <td className="px-4 py-3">
                      {getSeverityBadge(finding.severity)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn(
                        'inline-flex items-center gap-1.5 text-sm font-medium',
                        finding.isCompliant ? 'text-green-600' : 'text-red-600'
                      )}>
                        <span className={cn(
                          'w-2 h-2 rounded-full',
                          finding.isCompliant ? 'bg-green-500' : 'bg-red-500'
                        )} />
                        {finding.isCompliant ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {expandedRow === index ? (
                        <div className="whitespace-pre-wrap">{finding.observation}</div>
                      ) : (
                        <div className="truncate max-w-md">{finding.observation}</div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setExpandedRow(expandedRow === index ? null : index)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        {expandedRow === index ? 'Less' : 'More'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="text-sm text-gray-600">
        Showing {filteredFindings.length} of {findings.length} findings
      </div>
    </div>
  );
}
