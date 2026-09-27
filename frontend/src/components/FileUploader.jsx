import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle } from 'lucide-react';

const FileUploader = ({ onFileSelect, isUploading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file) => {
    setError("");
    if (!file) return false;

    const allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg'];
    const extension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(extension)) {
      setError("Invalid file format. Please upload a PDF, PNG, or JPG document.");
      return false;
    }

    // Limit to 10MB
    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Maximum size allowed is 10MB.");
      return false;
    }

    return true;
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="w-full">
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all ${
          dragActive 
            ? "border-amber-500 bg-amber-50/50" 
            : "border-slate-300 hover:border-amber-400 bg-slate-50"
        } ${isUploading ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}
        onClick={isUploading ? null : onButtonClick}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          onChange={handleChange}
          disabled={isUploading}
          accept=".pdf,.png,.jpg,.jpeg"
        />

        <div className="p-4 bg-white rounded-full shadow-sm border border-slate-100 text-slate-500 mb-4">
          <UploadCloud size={32} className={isUploading ? "animate-bounce text-amber-500" : ""} />
        </div>

        {isUploading ? (
          <div className="text-center">
            <h3 className="font-semibold text-slate-800 text-base">Uploading Land Document</h3>
            <p className="text-sm text-slate-500 mt-1">Submitting to digitization pipeline...</p>
          </div>
        ) : (
          <div className="text-center">
            <h3 className="font-semibold text-slate-800 text-base">
              Drag & drop your document here
            </h3>
            <p className="text-sm text-slate-500 mt-1">
              or <span className="text-amber-600 font-semibold underline">browse local files</span>
            </p>
            <p className="text-xs text-slate-400 mt-3">
              Supports PDF, PNG, JPG, or JPEG (Max 10MB)
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 flex items-center gap-2 text-rose-600 text-sm bg-rose-50 border border-rose-200 p-3 rounded-lg">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
