"use client";

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProposalUploadForm } from '@/components/tenders/ProposalUploadForm';
import { proposalAPI } from '@/lib/api';
import { ChevronRight, CheckCircle, Upload } from 'lucide-react';

export default function UploadProposalsPage() {
  const params = useParams();
  const router = useRouter();
  const tenderId = params.tenderId as string;
  
  const [uploadedProposals, setUploadedProposals] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleProposalUpload = async (data: {
    contractorId: string;
    companyName: string;
    ruc: string;
    principalFile: File;
    attachments: File[];
  }) => {
    setIsUploading(true);
    try {
      await proposalAPI.uploadProposal(
        tenderId,
        data.contractorId,
        data.companyName,
        data.ruc,
        data.principalFile,
        data.attachments
      );
      
      setUploadedProposals([...uploadedProposals, data.companyName]);
    } catch (error) {
      console.error('Proposal upload failed:', error);
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const handleProceedToAnalysis = () => {
    router.push(`/tenders/${tenderId}/analysis`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center text-sm text-gray-600 mb-4">
            <span className="hover:text-gray-900 cursor-pointer" onClick={() => router.push('/')}>
              Home
            </span>
            <ChevronRight className="w-4 h-4 mx-2" />
            <span>Upload Proposals</span>
          </div>
          
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <Upload className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Step 2: Upload Proposals
                </h1>
                <p className="text-sm text-gray-600">
                  Tender ID: <span className="font-mono font-semibold">{tenderId}</span>
                </p>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-900">
                💡 Upload one or more proposal documents. You can add multiple contractors' proposals before proceeding to analysis.
              </p>
            </div>
          </div>
        </div>

        {/* Uploaded Proposals List */}
        {uploadedProposals.length > 0 && (
          <div className="mb-6 bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Uploaded Proposals ({uploadedProposals.length})
            </h3>
            <div className="space-y-2">
              {uploadedProposals.map((company, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-md"
                >
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-900">{company}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload Form */}
        <div className="bg-white rounded-lg border p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {uploadedProposals.length === 0 ? 'Add First Proposal' : 'Add Another Proposal'}
          </h3>
          <ProposalUploadForm
            tenderId={tenderId}
            onUpload={handleProposalUpload}
          />
        </div>

        {/* Proceed Button */}
        {uploadedProposals.length > 0 && (
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">
                  Ready to analyze {uploadedProposals.length} proposal{uploadedProposals.length > 1 ? 's' : ''}?
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  You can always add more proposals later
                </p>
              </div>
              <button
                onClick={handleProceedToAnalysis}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
              >
                Proceed to Analysis
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
