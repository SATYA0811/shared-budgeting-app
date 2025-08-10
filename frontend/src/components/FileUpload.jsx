/**
 * File Upload Component - Shared Budgeting App
 * 
 * Allows users to upload bank statements (PDF, CSV, Excel) for
 * automatic transaction parsing and import.
 */

import React, { useState, useRef } from 'react';
import api from '../services/api';

export default function FileUpload({ onUploadSuccess, onClose }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const allowedTypes = [
    'application/pdf',
    'text/csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
  ];

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Validate file type
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF, CSV, or Excel file');
      return;
    }

    // Validate file size (10MB max)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      setProgress(20);

      const result = await api.files.uploadStatement(file);
      
      setProgress(100);
      
      // Show success message
      setTimeout(() => {
        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
        handleClose();
      }, 1000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError(null);
    setProgress(0);
    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (onClose) {
      onClose();
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      // Create a fake event object for handleFileSelect
      const fakeEvent = {
        target: {
          files: [droppedFile]
        }
      };
      handleFileSelect(fakeEvent);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Upload Bank Statement</h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* File Drop Zone */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center mb-4 transition-colors ${
            file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-indigo-300 hover:bg-indigo-50'
          }`}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="text-green-700">
              <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-green-600">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
            </div>
          ) : (
            <div className="text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="font-medium mb-1">Drop file here or click to upload</p>
              <p className="text-sm">PDF, CSV, or Excel files (max 10MB)</p>
            </div>
          )}
        </div>

        {/* File Input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf,.csv,.xlsx,.xls"
          className="hidden"
        />

        {/* Browse Button */}
        {!file && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 mb-4"
          >
            Browse Files
          </button>
        )}

        {/* Progress Bar */}
        {uploading && (
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-1">
              <span>Uploading...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleClose}
            className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex-1 py-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>

        {/* Supported Formats */}
        <div className="mt-4 text-xs text-gray-500 text-center">
          Supported formats: PDF bank statements, CSV files, Excel spreadsheets
        </div>
      </div>
    </div>
  );
}