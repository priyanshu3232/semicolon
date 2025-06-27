import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { useParseDocument } from '../hooks';

interface UploadFormProps {
  onDocumentParsed?: (document: any) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onDocumentParsed }) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const parseDocument = useParseDocument();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles(acceptedFiles);
    
    // Process each file
    acceptedFiles.forEach((file) => {
      parseDocument.mutate(file, {
        onSuccess: (data) => {
          console.log('Document parsed successfully:', data);
          onDocumentParsed?.(data);
        },
        onError: (error) => {
          console.error('Error parsing document:', error);
        },
      });
    });
  }, [parseDocument, onDocumentParsed]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'text/markdown': ['.md'],
    },
    maxFiles: 5,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Document Upload</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className={`p-4 rounded-full ${isDragActive ? 'bg-primary-100' : 'bg-gray-100'}`}>
            <Upload className={`w-8 h-8 ${isDragActive ? 'text-primary-600' : 'text-gray-600'}`} />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive ? 'Drop files here' : 'Drop files or click to upload'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Supports PDF, TXT, CSV, MD files up to 10MB
            </p>
          </div>
        </div>
      </div>

      {/* Upload Status */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-lg font-medium text-gray-900">Processing Files</h3>
          
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <File className="w-5 h-5 text-gray-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              
              <div className="flex items-center">
                {parseDocument.isPending ? (
                  <Loader className="w-5 h-5 text-blue-600 animate-spin" />
                ) : parseDocument.isSuccess ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : parseDocument.isError ? (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error Message */}
      {parseDocument.isError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-sm font-medium text-red-800">Upload Failed</p>
          </div>
          <p className="text-sm text-red-700 mt-1">
            {parseDocument.error?.message || 'An error occurred while processing the document.'}
          </p>
        </div>
      )}

      {/* Success Message */}
      {parseDocument.isSuccess && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-sm font-medium text-green-800">Document Processed Successfully</p>
          </div>
          <p className="text-sm text-green-700 mt-1">
            Your document has been parsed and is ready for analysis.
          </p>
        </div>
      )}
    </div>
  );
};

export default UploadForm;