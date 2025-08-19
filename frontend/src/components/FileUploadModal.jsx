/**
 * File Upload Modal - Universal file upload component
 * Supports PDF, CSV, and Excel files for bank statements
 * Can be used throughout the application
 */

import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Loader,
  Building2 
} from 'lucide-react';
import api from '../services/api';

export default function FileUploadModal({ onUploadSuccess, onClose, title = "Upload Bank Statement", supportedTypes = ["PDF", "CSV", "Excel"] }) {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedExtensions = ['.pdf', '.csv', '.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError('Please select a PDF, CSV, or Excel file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await api.transactions.uploadPDF(file);
      setUploadResult(result);
      
      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getBankIcon = (bankType) => {
    const bankColors = {
      'CIBC': 'text-red-600',
      'RBC': 'text-blue-600', 
      'AMEX': 'text-green-600',
      'TD': 'text-green-700',
      'BMO': 'text-blue-700'
    };
    
    return (
      <div className={`w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center ${bankColors[bankType] || 'text-gray-600'}`}>
        <Building2 className="h-4 w-4" />
      </div>
    );
  };

  const reset = () => {
    setUploadResult(null);
    setError(null);
    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6">
          {/* Success State */}
          {uploadResult && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">Upload Successful!</p>
                  <p className="text-sm text-green-700">{uploadResult.message}</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Bank Detected:</span>
                  <div className="flex items-center gap-2">
                    {getBankIcon(uploadResult.bank_type)}
                    <span className="font-medium">{uploadResult.bank_type}</span>
                  </div>
                </div>

                {uploadResult.account_info && (
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <span className="text-sm text-blue-700">Account:</span>
                    <div className="text-right">
                      <div className="font-medium text-blue-900">
                        {uploadResult.account_info.account_type} ****{uploadResult.account_info.last_4_digits}
                      </div>
                      <div className="text-xs text-blue-600">
                        {uploadResult.account_info.bank_name}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Transactions Found:</span>
                  <span className="font-medium">{uploadResult.total_transactions_found}</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">New Transactions:</span>
                  <span className="font-medium text-green-600">+{uploadResult.new_transactions_added}</span>
                </div>

                {uploadResult.duplicates_skipped > 0 && (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Duplicates Skipped:</span>
                    <span className="font-medium text-yellow-600">{uploadResult.duplicates_skipped}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={reset}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Upload Another
                </button>
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          )}

          {/* Upload State */}
          {!uploadResult && (
            <div className="space-y-4">
              {/* Upload Statement Button */}
              <div className="text-center py-8">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  className="hidden"
                />
                
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                    <Upload className="h-8 w-8 text-blue-600" />
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Upload Bank Statement
                    </h3>
                    <p className="text-sm text-gray-500 mb-4">
                      Select a {supportedTypes.join(", ")} file from your device
                    </p>
                  </div>
                  
                  <button
                    onClick={handleFileSelect}
                    disabled={uploading}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 mx-auto"
                  >
                    {uploading ? (
                      <>
                        <Loader className="h-5 w-5 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5" />
                        Upload Statement
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Supported Banks */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm font-medium text-blue-900 mb-2">Supported Banks:</p>
                <div className="flex items-center gap-3 text-sm text-blue-700">
                  <span>🏦 CIBC</span>
                  <span>🏦 RBC</span>
                  <span>💳 AMEX</span>
                  <span>🏦 TD</span>
                  <span>🏦 BMO</span>
                  <span>🏦 Scotiabank</span>
                </div>
              </div>

              {/* Error Display */}
              {error && (
                <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}

              {/* Cancel Button */}
              <div className="text-center">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}