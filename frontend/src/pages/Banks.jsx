/**
 * Banks & Files Page - Shared Budgeting App
 * 
 * Manage bank account information, upload bank statements,
 * file management, and data import/export functionality.
 */

import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Upload, 
  Download, 
  FileText, 
  CreditCard,
  Plus,
  Edit3,
  Trash2,
  CheckCircle,
  AlertCircle,
  Clock,
  Eye,
  RefreshCw,
  Search,
  Filter,
  Calendar,
  DollarSign,
  Paperclip,
  X,
  ExternalLink,
  Database,
  Shield,
  Zap
} from 'lucide-react';
import api from '../services/api';
import FileUploadModal from '../components/FileUploadModal';

export default function Banks() {
  const [activeTab, setActiveTab] = useState('accounts');
  const [bankAccounts, setBankAccounts] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showPDFUpload, setShowPDFUpload] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load bank accounts and files in parallel
      const [banksResponse, filesResponse] = await Promise.all([
        api.banks.getAccounts(),
        api.files.getUploadedFiles()
      ]);

      // Process bank accounts
      const banksData = banksResponse?.accounts || [];
      setBankAccounts(banksData);

      // Transform file data to match component expectations
      const filesData = filesResponse.data?.files || [];
      const transformedFiles = filesData.map(file => ({
        id: file.id,
        fileName: file.filename || 'Unknown File',
        bankName: file.bank_name || 'Unknown Bank',
        uploadDate: file.uploaded_at || new Date().toISOString(),
        fileSize: file.file_size || '0 KB',
        status: file.status || 'unknown',
        transactionsFound: file.transactions_found || 0,
        type: file.file_type || 'unknown',
        error: file.error_message
      }));
      
      setUploadedFiles(transformedFiles);
    } catch (error) {
      console.error('Error loading bank data:', error);
      // Fallback to empty arrays if API fails
      setBankAccounts([]);
      setUploadedFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => {
    setShowPDFUpload(true);
  };

  const handleUploadSuccess = (result) => {
    console.log('Upload successful:', result);
    loadData(); // Reload data after successful upload
  };

  const handleEditAccount = (account) => {
    console.log('Edit account:', account);
    // TODO: Implement edit account functionality
    alert(`Edit functionality for ${account.bank_name} account coming soon!`);
  };

  const handleSyncAccount = async (account) => {
    console.log('Sync account:', account);
    // TODO: Implement sync account functionality
    alert(`Sync functionality for ${account.bank_name} account coming soon!`);
  };

  const toggleFileSelection = (fileId) => {
    setSelectedFiles(prev =>
      prev.includes(fileId)
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'accounts', name: 'Bank Accounts', icon: Building2, count: bankAccounts.length },
    { id: 'files', name: 'Uploaded Files', icon: FileText, count: uploadedFiles.length },
    { id: 'upload', name: 'Upload Center', icon: Upload },
    { id: 'integration', name: 'Bank Integration', icon: Zap }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Banks & Files</h2>
          <p className="text-gray-600">Manage bank accounts and upload financial documents</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Sync All
          </button>
          <button 
            onClick={() => setShowAddAccount(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Account
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
                {tab.count !== undefined && (
                  <span className="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'accounts' && (
          <div>
            {bankAccounts.length === 0 ? (
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-12 text-center border border-indigo-100">
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Building2 className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">No Banks Added Yet</h3>
                <p className="text-gray-600 mb-8 max-w-lg mx-auto text-lg leading-relaxed">
                  Get started by uploading your bank statements or CSV files. 
                  We'll automatically detect your bank and organize your transactions.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                  <button 
                    onClick={() => setActiveTab('upload')}
                    className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 flex items-center gap-3"
                  >
                    <Upload className="h-5 w-5" />
                    Upload First Statement
                  </button>
                  <span className="text-gray-400 hidden sm:block">or</span>
                  <button 
                    onClick={() => setShowAddAccount(true)}
                    className="bg-white hover:bg-gray-50 text-gray-700 px-8 py-4 rounded-xl font-semibold border-2 border-gray-200 hover:border-gray-300 transition-all duration-200 flex items-center gap-3"
                  >
                    <Plus className="h-5 w-5" />
                    Add Account Manually
                  </button>
                </div>
                <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span>Supports PDF, CSV, Excel</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span>Auto bank detection</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span>Secure processing</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {bankAccounts.map((account) => (
                  <BankAccountCard 
                    key={account.id} 
                    account={account} 
                    onEdit={handleEditAccount}
                    onSync={handleSyncAccount}
                  />
                ))}
                
                {/* Add Account Card */}
                <div 
                  onClick={() => setShowAddAccount(true)}
                  className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-indigo-300 hover:bg-indigo-50 cursor-pointer transition-colors"
                >
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                    <Plus className="h-6 w-6 text-indigo-600" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Add Manual Account</h3>
                  <p className="text-sm text-gray-600">Manually add a bank account for tracking</p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'files' && (
          <>
            {/* File Management Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="text"
                      placeholder="Search files..."
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    <option value="">All Files</option>
                    <option value="processed">Processed</option>
                    <option value="processing">Processing</option>
                    <option value="error">Error</option>
                  </select>
                </div>

                {selectedFiles.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {selectedFiles.length} selected
                    </span>
                    <button className="btn-secondary text-sm">
                      <Download className="h-4 w-4 mr-1" />
                      Export
                    </button>
                    <button className="btn-danger text-sm">
                      <Trash2 className="h-4 w-4 mr-1" />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Files List */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="divide-y divide-gray-200">
                {uploadedFiles.map((file) => (
                  <FileRow
                    key={file.id}
                    file={file}
                    selected={selectedFiles.includes(file.id)}
                    onSelect={() => toggleFileSelection(file.id)}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* Upload Area */}
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
                  <Upload className="h-8 w-8 text-indigo-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Upload Bank Statements
                </h3>
                <p className="text-gray-600 mb-6 max-w-md">
                  Upload your PDF bank statements, CSV files, or Excel documents.
                  We'll automatically detect your bank and create accounts for you.
                  Supported formats: PDF, CSV, Excel
                </p>
                
                <button
                  onClick={handleUploadClick}
                  className="btn-primary flex items-center gap-2"
                >
                  <Upload className="h-5 w-5" />
                  Upload Statement
                </button>
              </div>
            </div>

            {/* Upload Instructions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">PDF Statements</h3>
                <p className="text-sm text-gray-600">
                  Upload monthly bank statements in PDF format. We'll automatically detect your bank and extract transactions.
                </p>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Database className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">CSV Files</h3>
                <p className="text-sm text-gray-600">
                  Import transaction data from CSV exports. Ensure columns include date, amount, and description.
                </p>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Secure Processing</h3>
                <p className="text-sm text-gray-600">
                  All files are processed securely and deleted after transaction extraction.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integration' && (
          <div className="space-y-6">
            {/* Integration Status */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Bank Integration Status</h3>
              <div className="space-y-4">
                <IntegrationStatus bank="CIBC" status="connected" />
                <IntegrationStatus bank="Royal Bank of Canada (RBC)" status="connected" />
                <IntegrationStatus bank="American Express Canada" status="connected" />
                <IntegrationStatus bank="TD Canada Trust" status="error" />
                <IntegrationStatus bank="Bank of Montreal (BMO)" status="available" />
                <IntegrationStatus bank="Scotiabank" status="available" />
                <IntegrationStatus bank="Tangerine" status="available" />
              </div>
            </div>

            {/* Available Integrations */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'Plaid Integration', description: 'Connect 11,000+ banks automatically', icon: '🔗' },
                { name: 'Open Banking', description: 'European bank account access', icon: '🏦' },
                { name: 'Manual Upload', description: 'Upload statements manually', icon: '📁' },
                { name: 'API Integration', description: 'Custom bank API connections', icon: '⚡' },
                { name: 'CSV Import', description: 'Bulk import transaction data', icon: '📊' },
                { name: 'Real-time Sync', description: 'Automatic transaction updates', icon: '🔄' }
              ].map((integration, index) => (
                <div key={index} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="text-2xl mb-3">{integration.icon}</div>
                  <h3 className="font-semibold text-gray-900 mb-2">{integration.name}</h3>
                  <p className="text-sm text-gray-600 mb-4">{integration.description}</p>
                  <button className="btn-secondary w-full text-sm">
                    Learn More
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* File Upload Modal */}
      {showPDFUpload && (
        <FileUploadModal
          title="Upload Bank Statement"
          supportedTypes={["PDF", "CSV", "Excel"]}
          onUploadSuccess={handleUploadSuccess}
          onClose={() => setShowPDFUpload(false)}
        />
      )}
    </div>
  );
}

// Helper Components
function BankAccountCard({ account, onEdit, onSync }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'needs_attention': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return CheckCircle;
      case 'needs_attention': return AlertCircle;
      default: return Clock;
    }
  };

  const StatusIcon = getStatusIcon(account.status);

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className="text-2xl mr-3">{account.logo}</div>
          <div>
            <h3 className="font-semibold text-gray-900">{account.bank_name}</h3>
            <p className="text-sm text-gray-600">{account.account_type} {account.account_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(account.status)}`}>
            <StatusIcon className="w-3 h-3 mr-1" />
            {account.status.replace('_', ' ')}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Balance</span>
          <span className={`font-semibold ${account.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {account.balance >= 0 ? '' : '-'}${Math.abs(account.balance).toLocaleString('en-CA', { minimumFractionDigits: 2 })} {account.currency || 'CAD'}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Last Sync</span>
          <span className="text-sm text-gray-900">
            {new Date(account.last_sync).toLocaleString('en-CA', {
              year: 'numeric',
              month: '2-digit', 
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>

        {account.discovered_from_uploads && (
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Files Uploaded</span>
            <span className="text-sm text-gray-900">{account.files_uploaded || 0}</span>
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-6">
        <button 
          onClick={() => onSync?.(account)}
          className="flex-1 btn-secondary text-sm hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-1" />
          Sync
        </button>
        <button 
          onClick={() => onEdit?.(account)}
          className="flex-1 btn-secondary text-sm hover:bg-gray-50 transition-colors"
        >
          <Edit3 className="h-4 w-4 mr-1" />
          Edit
        </button>
      </div>
    </div>
  );
}

function FileRow({ file, selected, onSelect }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing': return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'error': return <AlertCircle className="h-5 w-5 text-red-500" />;
      default: return <FileText className="h-5 w-5 text-gray-400" />;
    }
  };

  const getFileTypeIcon = (type) => {
    switch (type) {
      case 'bank_statement': return '📄';
      case 'credit_statement': return '💳';
      case 'csv': return '📊';
      default: return '📁';
    }
  };

  return (
    <div className="p-6 hover:bg-gray-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selected}
            onChange={onSelect}
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-4"
          />
          
          <div className="flex items-center">
            <div className="text-2xl mr-4">{getFileTypeIcon(file.type)}</div>
            <div>
              <div className="flex items-center">
                <h3 className="font-medium text-gray-900 mr-3">{file.fileName}</h3>
                {getStatusIcon(file.status)}
              </div>
              <div className="flex items-center text-sm text-gray-500 mt-1">
                <span>{file.bankName}</span>
                <span className="mx-2">•</span>
                <span>{file.fileSize}</span>
                <span className="mx-2">•</span>
                <span>{new Date(file.uploadDate).toLocaleDateString('en-CA', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit'
                })}</span>
              </div>
              {file.error && (
                <p className="text-sm text-red-600 mt-1">{file.error}</p>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {file.transactionsFound > 0 && (
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {file.transactionsFound} transactions
              </div>
              <div className="text-xs text-gray-500">extracted</div>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-400 hover:text-indigo-600">
              <Eye className="h-4 w-4" />
            </button>
            <button className="p-2 text-gray-400 hover:text-indigo-600">
              <Download className="h-4 w-4" />
            </button>
            <button className="p-2 text-gray-400 hover:text-red-600">
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function IntegrationStatus({ bank, status }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-50';
      case 'error': return 'text-red-600 bg-red-50';
      case 'available': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'error': return 'Connection Error';
      case 'available': return 'Available';
      default: return 'Unknown';
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
      <div className="flex items-center">
        <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
          <Building2 className="h-5 w-5 text-gray-600" />
        </div>
        <div>
          <h3 className="font-medium text-gray-900">{bank}</h3>
          <p className={`text-sm px-2 py-1 rounded-full inline-flex items-center ${getStatusColor(status)}`}>
            {getStatusText(status)}
          </p>
        </div>
      </div>
      
      <div className="flex gap-2">
        {status === 'connected' && (
          <button className="btn-secondary text-sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            Sync
          </button>
        )}
        {status === 'error' && (
          <button className="btn-secondary text-sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            Reconnect
          </button>
        )}
        {status === 'available' && (
          <button className="btn-primary text-sm">
            <Plus className="h-4 w-4 mr-1" />
            Connect
          </button>
        )}
      </div>
    </div>
  );
}