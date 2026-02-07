"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TenderUploadZone } from '@/components/tenders/TenderUploadZone';
import { useUploadTender } from '@/hooks/useTender';
import { FileText, TrendingUp, CheckCircle, Upload } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const uploadTenderMutation = useUploadTender();
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [tenderId, setTenderId] = useState<string | null>(null);

  const handleTenderUpload = async (file: File) => {
    try {
      const result = await uploadTenderMutation.mutateAsync(file);
      setTenderId(result.tender_id);
      setUploadSuccess(true);
      
      // Redirect to upload proposals page after 2 seconds
      setTimeout(() => {
        router.push(`/tenders/${result.tender_id}/upload`);
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="pt-20 pb-12 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            TenderAnalyzer
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            AI-Powered Tender Proposal Analysis
          </p>
          <p className="text-gray-500 max-w-2xl mx-auto">
            Upload your tender documents and proposals to get comprehensive analysis,
            scoring, and recommendations powered by advanced AI agents.
          </p>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-5xl mx-auto px-6 mb-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<FileText className="w-6 h-6" />}
            title="Automated Analysis"
            description="AI agents analyze tender requirements and proposal compliance automatically"
          />
          <FeatureCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Smart Scoring"
            description="Multi-dimensional scoring across legal, technical, and financial criteria"
          />
          <FeatureCard
            icon={<CheckCircle className="w-6 h-6" />}
            title="Detailed Reports"
            description="Get executive summaries, compliance findings, and visual comparisons"
          />
        </div>
      </div>

      {/* Upload Section */}
      <div className="max-w-2xl mx-auto px-6 pb-20">
        {!uploadSuccess ? (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <Upload className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">
                  Step 1: Upload Tender Document
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Start by uploading the main tender PDF
                </p>
              </div>
            </div>
            
            <TenderUploadZone
              onUpload={handleTenderUpload}
              isUploading={uploadTenderMutation.isPending}
            />
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-green-200">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-green-100 mx-auto mb-4 flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                Tender Uploaded Successfully!
              </h3>
              <p className="text-gray-600 mb-4">
                Tender ID: <span className="font-mono font-semibold">{tenderId}</span>
              </p>
              <p className="text-sm text-gray-500">
                Redirecting to proposal upload...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t bg-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <p className="text-center text-sm text-gray-500">
            © 2026 TenderAnalyzer. Powered by LangGraph & GPT-4
          </p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ 
  icon, 
  title, 
  description 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg p-6 border border-gray-100 hover:shadow-md transition-shadow">
      <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4 text-blue-600">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
