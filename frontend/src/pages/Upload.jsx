import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  FileText, 
  ArrowRight, 
  HelpCircle, 
  Loader2, 
  CheckCircle2, 
  ChevronRight,
  Info,
  Layers,
  Sparkles,
  Upload as UploadIcon,
  Languages,
  FileStack
} from 'lucide-react';
import { documentService } from '../services/api';
import FileUploader from '../components/FileUploader';

const Upload = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [uploading, setUploading] = useState(false);
  const [docId, setDocId] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(0); // 0: Idle, 1: Preprocessing, 2: Classification, 3: OCR, 4: NLP, 5: Validation, 6: Finished
  const [selectedLanguage, setSelectedLanguage] = useState("Auto");
  const autoUploadedRef = useRef(false);

  const stepsList = [
    { label: "Document Uploaded", desc: "Original scanned file saved securely" },
    { label: "Image Preprocessing", desc: "OpenCV deskewing, noise reduction, and binarization" },
    { label: "OCR & Character Mapping", desc: "Extracting text, word tokens, and bounding boxes" },
    { label: "Document Classification", desc: "Detecting document type, language, and script format" },
    { label: "Multilingual Field Extraction", desc: "Parsing fields: Owner, Survey No, Extent, Mandal, Village" },
    { label: "Validation Engine Check", desc: "Checking area consistency, duplicates, and conflicts" }
  ];

  const handleFileSelect = async (file, langOverride = null) => {
    setUploading(true);
    setPipelineStep(1); // Started preprocessing
    
    const langToUse = langOverride !== null ? langOverride : selectedLanguage;
    try {
      const response = await documentService.upload(file, langToUse === "Auto" ? "" : langToUse);
      const newDocId = response.document_id || response.id;
      setDocId(newDocId);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to initiate document upload.");
      setUploading(false);
      setPipelineStep(0);
    }
  };

  // Automatically load and upload sample document if navigated from Sample Records
  useEffect(() => {
    if (location.state?.sampleUrl && !autoUploadedRef.current) {
      autoUploadedRef.current = true;
      const sampleState = { ...location.state };
      window.history.replaceState({}, document.title);
      
      setUploading(true);
      setPipelineStep(0);
      
      const loadAndUploadSample = async () => {
        try {
          const sampleLang = sampleState.language || "Auto";
          setSelectedLanguage(sampleLang);
          const res = await fetch(sampleState.sampleUrl);
          const blob = await res.blob();
          const file = new File(
            [blob], 
            sampleState.sampleName || 'sample_record.jpg', 
            { type: blob.type || 'image/jpeg' }
          );
          await handleFileSelect(file, sampleLang);
        } catch (err) {
          console.error("Auto-upload of sample failed:", err);
          setUploading(false);
          setPipelineStep(0);
          alert("Failed to load sample document: " + err.message);
        }
      };
      loadAndUploadSample();
    }
  }, [location.state]);

  // Poll for document status
  useEffect(() => {
    if (!docId) return;

    const checkStatus = async () => {
      try {
        const details = await documentService.getDetails(docId);
        const status = details.document.status;
        const stage = details.document.processing_stage;
        
        // Map backend stage to stepsList index
        if (stage === "UPLOADED") {
          setPipelineStep(0);
        } else if (stage === "PREPROCESSING") {
          setPipelineStep(1);
        } else if (stage === "OCR_PROCESSING" || stage === "CLASSIFYING") {
          setPipelineStep(2);
        } else if (stage === "AI_ANALYSIS" || stage === "EXTRACTING") {
          setPipelineStep(3);
        } else if (stage === "VALIDATING" || stage === "NORMALIZING") {
          setPipelineStep(4);
        }

        if (status !== 'Processing') {
          clearInterval(poll);
          setPipelineStep(6); // Finished
          
          // Wait briefly before redirecting
          setTimeout(() => {
            if (status === 'Verified') {
              navigate(`/processing/${docId}`);
            } else {
              navigate(`/verify/${docId}`);
            }
          }, 800);
        }
      } catch (err) {
        console.error("Error polling document status:", err);
      }
    };

    // Run first check immediately, then poll every 1.2s
    checkStatus();
    const poll = setInterval(checkStatus, 1200);

    return () => {
      clearInterval(poll);
    };
  }, [docId, navigate]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Upload Box */}
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-1 flex items-center gap-2">
              <UploadIcon className="text-emerald-600" size={22} />
              Upload Land Registry Document
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Upload scanned land deeds or registry records for automated cadastral extraction and verification.
            </p>
          </div>
          <button
            type="button"
            onClick={() => navigate('/sample-records')}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2.5 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer self-start sm:self-auto shrink-0"
            title="Browse official digitalized and undigitalized sample records"
          >
            <FileStack size={16} />
            <span>Sample Records</span>
          </button>
        </div>

        {!uploading && (
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <label className="block text-xs font-bold text-slate-700 uppercase flex items-center gap-1">
              <Languages size={14} className="text-indigo-600" />
              Document Language (or Auto-Detect)
            </label>
            <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-2">
              {['Auto', 'Telugu', 'Tamil', 'Hindi', 'Gujarati', 'Kannada', 'Marathi', 'Odia', 'English'].map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setSelectedLanguage(lang)}
                  className={`py-2 px-2 rounded-lg text-xs font-bold transition cursor-pointer border text-center ${
                    selectedLanguage === lang
                      ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Drag & Drop Upload Zone */}
        {!uploading ? (
          <FileUploader onFileSelect={handleFileSelect} isUploading={uploading} />
        ) : (
          <div className="border border-slate-200 bg-white rounded-2xl p-6 shadow-sm space-y-6 animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                  <Sparkles size={20} className="animate-pulse" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Digitization Pipeline Running</h3>
                  <p className="text-xs text-slate-500 mt-0.5 font-medium">Executing multi-stage image enhancement, OCR, and validation audits</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-indigo-600 text-xs font-bold bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
                <Loader2 size={13} className="animate-spin" />
                <span>Processing...</span>
              </div>
            </div>

            {/* Progress Steps Timeline */}
            <div className="space-y-4">
              {stepsList.map((step, index) => {
                const isCompleted = pipelineStep > index;
                const isCurrent = pipelineStep === index;
                
                return (
                  <div 
                    key={index} 
                    className={`flex items-start gap-4 transition-all duration-300 ${
                      isCompleted ? "opacity-100" : isCurrent ? "opacity-100 scale-[1.01]" : "opacity-40"
                    }`}
                  >
                    <div className="flex flex-col items-center">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center border font-bold text-xs ${
                        isCompleted 
                          ? "bg-emerald-500 border-emerald-500 text-white shadow-sm" 
                          : isCurrent 
                            ? "bg-indigo-50 border-indigo-600 text-indigo-700 animate-pulse ring-2 ring-indigo-600/20" 
                            : "bg-white border-slate-300 text-slate-400"
                      }`}>
                        {isCompleted ? <CheckCircle2 size={15} /> : index + 1}
                      </div>
                      {index < stepsList.length - 1 && (
                        <div className={`w-0.5 h-8 my-1 ${
                          isCompleted ? "bg-emerald-500" : "bg-slate-200"
                        }`}></div>
                      )}
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold leading-none ${
                        isCompleted ? "text-slate-900" : isCurrent ? "text-indigo-700" : "text-slate-500"
                      }`}>
                        {step.label}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1 font-medium">{step.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Informational Guidance Panel */}
      <div className="bg-slate-50 border border-slate-200 p-5 rounded-2xl flex items-start gap-3.5 shadow-sm">
        <div className="p-2 bg-slate-900 text-white rounded-xl shrink-0">
          <Info size={18} />
        </div>
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 mb-0.5">Government Compliance Notice</h3>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            This platform complies with the Digital India Land Records Modernization Programme (DILRMP). All automated extractions 
            pass through a certified revenue officer verification checkpoint before being committed to the official state cadastral ledger.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Upload;
