"use client";

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, ChevronRight, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProposalUploadFormProps {
  tenderId: string;
  onUpload: (data: {
    contractorId: string;
    companyName: string;
    principalFile: File;
    attachments: File[];
  }) => Promise<void>;
}

type Step = 1 | 2 | 3;

export function ProposalUploadForm({ tenderId, onUpload }: ProposalUploadFormProps) {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [contractorId, setContractorId] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [principalFile, setPrincipalFile] = useState<File | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canProceedStep1 = contractorId.trim() !== '' && companyName.trim() !== '';
  const canProceedStep2 = principalFile !== null;
  const canSubmit = canProceedStep1 && canProceedStep2;

  const handleNextStep = () => {
    if (currentStep === 1 && canProceedStep1) {
      setCurrentStep(2);
    } else if (currentStep === 2 && canProceedStep2) {
      setCurrentStep(3);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep((currentStep - 1) as Step);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await onUpload({
        contractorId,
        companyName,
        principalFile: principalFile!,
        attachments,
      });
      
      // Reset form
      setContractorId('');
      setCompanyName('');
      setPrincipalFile(null);
      setAttachments([]);
      setCurrentStep(1);
    } catch (err: any) {
      setError(err.message || 'Failed to upload proposal');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors',
                    currentStep >= step
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  )}
                >
                  {step}
                </div>
                <span className={cn(
                  'text-xs mt-2 font-medium',
                  currentStep >= step ? 'text-blue-600' : 'text-gray-500'
                )}>
                  {step === 1 && 'Info'}
                  {step === 2 && 'Principal'}
                  {step === 3 && 'Attachments'}
                </span>
              </div>
              {step < 3 && (
                <div
                  className={cn(
                    'flex-1 h-1 mx-2',
                    currentStep > step ? 'bg-blue-600' : 'bg-gray-200'
                  )}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg border p-6">
        {currentStep === 1 && <Step1Content 
          contractorId={contractorId}
          setContractorId={setContractorId}
          companyName={companyName}
          setCompanyName={setCompanyName}
        />}
        
        {currentStep === 2 && <Step2Content 
          principalFile={principalFile}
          setPrincipalFile={setPrincipalFile}
        />}
        
        {currentStep === 3 && <Step3Content 
          attachments={attachments}
          setAttachments={setAttachments}
        />}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 rounded-md bg-red-50 border border-red-200">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Navigation */}
      <div className="mt-6 flex gap-3">
        {currentStep > 1 && (
          <button
            onClick={handlePrevStep}
            disabled={isSubmitting}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
        )}
        
        <div className="flex-1" />
        
        {currentStep < 3 ? (
          <button
            onClick={handleNextStep}
            disabled={
              (currentStep === 1 && !canProceedStep1) ||
              (currentStep === 2 && !canProceedStep2)
            }
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!canSubmit || isSubmitting}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Uploading...' : 'Submit Proposal'}
          </button>
        )}
      </div>
    </div>
  );
}

// Step 1: Contractor Information
function Step1Content({ 
  contractorId, 
  setContractorId, 
  companyName, 
  setCompanyName 
}: {
  contractorId: string;
  setContractorId: (value: string) => void;
  companyName: string;
  setCompanyName: (value: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Contractor Information</h3>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Contractor ID <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={contractorId}
          onChange={(e) => setContractorId(e.target.value)}
          placeholder="e.g., C001"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Company Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., Acme Corporation"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}

// Step 2: Principal File Upload
function Step2Content({ 
  principalFile, 
  setPrincipalFile 
}: {
  principalFile: File | null;
  setPrincipalFile: (file: File | null) => void;
}) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setPrincipalFile(acceptedFiles[0]);
    }
  }, [setPrincipalFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  });

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Principal Proposal File</h3>
      
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive && 'border-blue-500 bg-blue-50',
          !isDragActive && !principalFile && 'border-gray-300 hover:border-gray-400',
          principalFile && 'border-green-500 bg-green-50'
        )}
      >
        <input {...getInputProps()} />
        
        {principalFile ? (
          <div className="flex flex-col items-center gap-3">
            <FileText className="w-12 h-12 text-green-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">{principalFile.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                {(principalFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setPrincipalFile(null);
              }}
              className="mt-2 text-sm text-red-600 hover:text-red-800"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload className="w-12 h-12 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                {isDragActive ? 'Drop the PDF here' : 'Upload principal proposal PDF'}
              </p>
              <p className="text-xs text-gray-500 mt-1">Drag & drop or click to browse</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Step 3: Attachments Upload
function Step3Content({ 
  attachments, 
  setAttachments 
}: {
  attachments: File[];
  setAttachments: (files: File[]) => void;
}) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setAttachments([...attachments, ...acceptedFiles]);
  }, [attachments, setAttachments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 50 * 1024 * 1024,
  });

  const removeAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Attachments (Optional)
      </h3>
      
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-600">
          {isDragActive ? 'Drop files here' : 'Add attachment files (PDFs)'}
        </p>
      </div>

      {/* Attachments List */}
      {attachments.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">
            Attached Files ({attachments.length})
          </p>
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeAttachment(index)}
                className="text-red-600 hover:text-red-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
