import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileStack, 
  Eye, 
  Download, 
  UploadCloud, 
  CheckCircle2, 
  AlertTriangle,
  X 
} from 'lucide-react';

const SampleRecords = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('digitized'); // 'digitized' | 'undigitized'
  const [selectedImage, setSelectedImage] = useState(null);

  // 1. Digitalized Records
  const digitizedRecords = [
    {
      id: 'dig-1',
      title: 'Andhra Pradesh (Telugu Deed)',
      imageUrl: '/sample_records/digitized/andhra_pradesh.jpg',
      downloadName: 'Andhra_Pradesh_Sample.jpg',
      language: 'Telugu'
    },
    {
      id: 'dig-2',
      title: 'Gujarat (Gujarati Deed)',
      imageUrl: '/sample_records/digitized/gujarat.jpg',
      downloadName: 'Gujarat_Sample.jpg',
      language: 'Gujarati'
    },
    {
      id: 'dig-3',
      title: 'Maharashtra (Marathi Deed)',
      imageUrl: '/sample_records/digitized/maharashtra.jpg',
      downloadName: 'Maharashtra_Sample.jpg',
      language: 'Marathi'
    },
    {
      id: 'dig-4',
      title: 'Karnataka (Kannada Deed)',
      imageUrl: '/sample_records/digitized/karnataka.jpg',
      downloadName: 'Karnataka_Sample.jpg',
      language: 'Kannada'
    },
    {
      id: 'dig-5',
      title: 'Uttar Pradesh (Hindi Deed)',
      imageUrl: '/sample_records/digitized/uttar_pradesh.jpg',
      downloadName: 'Uttar_Pradesh_Sample.jpg',
      language: 'Hindi'
    }
  ];

  // 2. Undigitalized Records (User's legacy records not in govt database)
  const undigitizedRecords = [
    {
      id: 'undig-1',
      title: 'Telangana (Telugu Deed)',
      imageUrl: '/sample_records/undigitized/telangana.jpg',
      downloadName: 'Telangana_Sample.jpg',
      language: 'Telugu'
    },
    {
      id: 'undig-2',
      title: 'Gujarat (Gujarati Deed)',
      imageUrl: '/sample_records/undigitized/gujarat.jpg',
      downloadName: 'Gujarat_Sample.jpg',
      language: 'Gujarati'
    },
    {
      id: 'undig-3',
      title: 'Tamil Nadu (Tamil Deed)',
      imageUrl: '/sample_records/undigitized/tamil_nadu.jpg',
      downloadName: 'Tamil_Nadu_Sample.jpg',
      language: 'Tamil'
    },
    {
      id: 'undig-4',
      title: 'Uttar Pradesh (Hindi Deed)',
      imageUrl: '/sample_records/undigitized/uttar_pradesh.jpg',
      downloadName: 'Uttar_Pradesh_Sample.jpg',
      language: 'Hindi'
    }
  ];

  const currentList = activeTab === 'digitized' ? digitizedRecords : undigitizedRecords;

  const handleDirectUpload = (item) => {
    if (!item.imageUrl) return;
    navigate('/upload', {
      state: {
        sampleUrl: item.imageUrl,
        sampleName: item.downloadName,
        language: item.language || 'Auto'
      }
    });
  };

  const handleDownload = (imageUrl, downloadName) => {
    if (!imageUrl) return;
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = downloadName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-gray-200 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-slate-900 text-white rounded-xl shadow-xs">
            <FileStack size={22} />
          </div>
          <div>
            <h1 className="text-xl font-black text-slate-900">
              Sample Records
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              View and download sample document images for verification testing.
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate('/upload')}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-3.5 rounded-xl text-xs flex items-center gap-1.5 shadow-xs transition cursor-pointer self-start sm:self-auto"
        >
          <UploadCloud size={15} />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Module Tabs */}
      <div className="flex bg-slate-100 p-1.5 rounded-2xl border border-slate-200 shadow-xs">
        <button
          onClick={() => setActiveTab('digitized')}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
            activeTab === 'digitized'
              ? 'bg-white text-emerald-800 shadow-sm border border-emerald-200 ring-1 ring-emerald-500/20'
              : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <CheckCircle2 size={16} className={activeTab === 'digitized' ? 'text-emerald-600' : 'text-slate-400'} />
          <span className="text-sm">Digitalized Records</span>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
            {digitizedRecords.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('undigitized')}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
            activeTab === 'undigitized'
              ? 'bg-white text-amber-900 shadow-sm border border-amber-300 ring-1 ring-amber-500/20'
              : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <AlertTriangle size={16} className={activeTab === 'undigitized' ? 'text-amber-600' : 'text-slate-400'} />
          <span className="text-sm">Undigitalized Records</span>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
            {undigitizedRecords.length}
          </span>
        </button>
      </div>

      {/* Image Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {currentList.map((item) => (
          <div 
            key={item.id} 
            className="bg-white rounded-2xl border border-gray-200 shadow-xs overflow-hidden flex flex-col hover:shadow-md transition duration-200"
          >
            {/* Title Header */}
            <div className="p-4 border-b border-gray-100 bg-slate-50 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 truncate">
                {item.title}
              </h3>
            </div>

            {/* Document Image Preview */}
            <div className="p-4 bg-slate-900/5 relative group flex items-center justify-center h-80 overflow-hidden">
              {item.imageUrl ? (
                <>
                  <img 
                    src={item.imageUrl} 
                    alt={item.title} 
                    className="max-h-full max-w-full object-contain rounded-lg shadow-sm border border-gray-200 bg-white transition-transform group-hover:scale-102"
                  />
                  {/* Hover Overlay Button to inspect */}
                  <button
                    onClick={() => setSelectedImage(item.imageUrl)}
                    className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1.5 text-white text-xs font-bold backdrop-blur-xs cursor-pointer"
                  >
                    <Eye size={18} />
                    <span>View Full Image</span>
                  </button>
                </>
              ) : (
                <div className="w-full h-full border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center p-4 text-center bg-white/60">
                  <div className="p-3 bg-amber-50 text-amber-600 rounded-full mb-2">
                    <FileStack size={28} />
                  </div>
                  <span className="text-xs font-bold text-slate-700">Image Ready</span>
                  <span className="text-[10px] text-slate-400 mt-1">Waiting for upload image</span>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="p-3.5 border-t border-gray-100 bg-slate-50 flex items-center gap-2">
              {item.imageUrl ? (
                <>
                  <button
                    onClick={() => handleDirectUpload(item)}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs"
                    title="Upload and process this document"
                  >
                    <UploadCloud size={14} />
                    <span>Upload Record</span>
                  </button>
                  <button
                    onClick={() => setSelectedImage(item.imageUrl)}
                    className="p-2 bg-white hover:bg-slate-100 text-slate-700 font-bold rounded-xl text-xs flex items-center justify-center border border-gray-200 transition cursor-pointer shadow-2xs"
                    title="View Full Image"
                  >
                    <Eye size={15} />
                  </button>
                  <button
                    onClick={() => handleDownload(item.imageUrl, item.downloadName)}
                    className="p-2 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl text-xs flex items-center justify-center transition cursor-pointer shadow-2xs"
                    title="Download Image"
                  >
                    <Download size={15} />
                  </button>
                </>
              ) : (
                <button
                  onClick={() => navigate('/upload')}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition cursor-pointer shadow-2xs"
                >
                  <UploadCloud size={14} />
                  <span>Upload Document</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Full Image Zoom Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div 
            className="bg-white rounded-2xl max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl border border-slate-700 flex flex-col relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-slate-50">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                Document Preview
              </h3>
              <button
                onClick={() => setSelectedImage(null)}
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-gray-200 transition cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>
            <div className="p-6 bg-slate-900/5 overflow-auto flex items-center justify-center">
              <img 
                src={selectedImage} 
                alt="Document Preview" 
                className="max-h-[75vh] max-w-full object-contain rounded-lg shadow-md border border-gray-300 bg-white"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SampleRecords;
