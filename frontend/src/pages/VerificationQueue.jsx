import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Search, 
  Filter, 
  Download, 
  FileText, 
  Languages, 
  Layers,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { verificationService, documentService } from '../services/api';
import StatusBadge from '../components/StatusBadge';

const VerificationQueue = () => {
  const navigate = useNavigate();
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterTab, setFilterTab] = useState("all"); // all, pending, verified, flagged
  const [searchQuery, setSearchQuery] = useState("");

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const data = await verificationService.getPendingList();
      setQueue(Array.isArray(data) ? data : []);
    } catch (err) {
      setError("Failed to fetch pending review records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const totalCount = queue.length;
  const verifiedCount = queue.filter(item => item.status === 'Verified').length;
  const pendingCount = queue.filter(item => item.status !== 'Verified' && item.anomalies_count === 0).length;
  const flaggedCount = queue.filter(item => item.anomalies_count > 0 || item.status === 'Needs Review' || item.status === 'Low Confidence').length;

  const filteredQueue = queue.filter(item => {
    // Filter by Tab
    if (filterTab === 'verified' && item.status !== 'Verified') return false;
    if (filterTab === 'pending' && (item.status === 'Verified' || item.anomalies_count > 0)) return false;
    if (filterTab === 'flagged' && (item.anomalies_count === 0 && item.status !== 'Needs Review')) return false;

    // Filter by Search Query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const fn = (item.original_filename || '').toLowerCase();
      const owner = (item.land_record?.owner_name || '').toLowerCase();
      const survey = (item.land_record?.survey_number || '').toLowerCase();
      const village = (item.land_record?.village || '').toLowerCase();
      const lang = (item.language || '').toLowerCase();
      return fn.includes(q) || owner.includes(q) || survey.includes(q) || village.includes(q) || lang.includes(q);
    }

    return true;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-4">
        <div className="w-12 h-12 border-4 border-slate-900 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-semibold text-slate-600">Loading Revenue Verification Queue...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="text-emerald-600" size={24} />
            Revenue Officer Review & Verification Queue
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Audit, verify, and seal digitized land records from Indic historical scripts into the official cadastral ledger.
          </p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center gap-2 shadow-sm transition cursor-pointer self-start sm:self-auto"
        >
          <Layers size={15} />
          Upload New Record
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div 
          onClick={() => setFilterTab('all')}
          className={`p-4 rounded-xl border transition cursor-pointer ${filterTab === 'all' ? 'bg-white border-slate-800 shadow-md ring-2 ring-slate-800/10' : 'bg-white border-gray-200 hover:border-gray-300'}`}
        >
          <div className="text-[11px] font-bold uppercase text-slate-500 tracking-wider">All Records</div>
          <div className="text-2xl font-black text-slate-900 mt-1">{totalCount}</div>
          <div className="text-[10px] text-slate-400 font-semibold mt-0.5">Total Uploaded Deeds</div>
        </div>

        <div 
          onClick={() => setFilterTab('verified')}
          className={`p-4 rounded-xl border transition cursor-pointer ${filterTab === 'verified' ? 'bg-emerald-50 border-emerald-600 shadow-md ring-2 ring-emerald-600/10' : 'bg-white border-gray-200 hover:border-emerald-300'}`}
        >
          <div className="text-[11px] font-bold uppercase text-emerald-700 tracking-wider flex items-center gap-1">
            <CheckCircle2 size={13} />
            Verified & Sealed
          </div>
          <div className="text-2xl font-black text-emerald-700 mt-1">{verifiedCount}</div>
          <div className="text-[10px] text-emerald-600 font-semibold mt-0.5">Ready for Certificate</div>
        </div>

        <div 
          onClick={() => setFilterTab('pending')}
          className={`p-4 rounded-xl border transition cursor-pointer ${filterTab === 'pending' ? 'bg-indigo-50 border-indigo-600 shadow-md ring-2 ring-indigo-600/10' : 'bg-white border-gray-200 hover:border-indigo-300'}`}
        >
          <div className="text-[11px] font-bold uppercase text-indigo-700 tracking-wider flex items-center gap-1">
            <Clock size={13} />
            Pending Action
          </div>
          <div className="text-2xl font-black text-indigo-700 mt-1">{pendingCount}</div>
          <div className="text-[10px] text-indigo-600 font-semibold mt-0.5">Awaiting Officer Review</div>
        </div>

        <div 
          onClick={() => setFilterTab('flagged')}
          className={`p-4 rounded-xl border transition cursor-pointer ${filterTab === 'flagged' ? 'bg-amber-50 border-amber-600 shadow-md ring-2 ring-amber-600/10' : 'bg-white border-gray-200 hover:border-amber-300'}`}
        >
          <div className="text-[11px] font-bold uppercase text-amber-700 tracking-wider flex items-center gap-1">
            <AlertTriangle size={13} />
            Flagged Anomalies
          </div>
          <div className="text-2xl font-black text-amber-700 mt-1">{flaggedCount}</div>
          <div className="text-[10px] text-amber-600 font-semibold mt-0.5">Requires Manual Check</div>
        </div>
      </div>

      {/* Main Queue Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        
        {/* Table Toolbar: Filter Tabs + Search */}
        <div className="p-4 border-b border-gray-100 flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-50/50">
          <div className="flex bg-gray-200 p-1 rounded-xl text-xs font-bold w-full md:w-auto">
            <button
              onClick={() => setFilterTab('all')}
              className={`px-3.5 py-1.5 rounded-lg transition cursor-pointer ${filterTab === 'all' ? 'bg-white shadow text-slate-900 font-bold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              All ({totalCount})
            </button>
            <button
              onClick={() => setFilterTab('verified')}
              className={`px-3.5 py-1.5 rounded-lg transition cursor-pointer ${filterTab === 'verified' ? 'bg-white shadow text-emerald-700 font-bold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Verified ({verifiedCount})
            </button>
            <button
              onClick={() => setFilterTab('pending')}
              className={`px-3.5 py-1.5 rounded-lg transition cursor-pointer ${filterTab === 'pending' ? 'bg-white shadow text-indigo-700 font-bold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Pending ({pendingCount})
            </button>
            <button
              onClick={() => setFilterTab('flagged')}
              className={`px-3.5 py-1.5 rounded-lg transition cursor-pointer ${filterTab === 'flagged' ? 'bg-white shadow text-amber-700 font-bold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Flagged ({flaggedCount})
            </button>
          </div>

          <div className="relative w-full md:w-72">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search filename, owner, survey no..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:ring-1 focus:ring-slate-900 outline-none transition"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-bold uppercase text-[10px] border-b border-gray-100">
                <th className="px-5 py-3.5">Document & Script</th>
                <th className="px-5 py-3.5">Status / Confidence</th>
                <th className="px-5 py-3.5">Pattadar / Owner</th>
                <th className="px-5 py-3.5">Survey / Khasra No.</th>
                <th className="px-5 py-3.5">Location & Extent</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 font-medium text-slate-700">
              {filteredQueue.map((item) => {
                const lr = item.land_record || {};
                const docId = item.document_id || item.id;
                const conf = item.confidence_score || 0;

                const knownUnDigitizedDeeds = [
                  'komaripati', 'venkateswara', 'cj 475829', '216/2',
                  'hiteshbhai', 'amrutlal', 'gj 361245',
                  'arun kumar', 'ramasamy', 'tn 685214',
                  'mohan lal', 'harishchandra', 'bk 125678', '145/1'
                ];
                const checkStr = `${item.original_filename || ''} ${lr.owner_name || ''} ${lr.survey_number || ''} ${lr.registration_number || ''}`.toLowerCase();
                const isUndigitized = knownUnDigitizedDeeds.some(t => checkStr.includes(t));

                return (
                  <tr key={docId} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-bold text-slate-900 text-xs truncate max-w-[200px]" title={item.original_filename}>
                        {item.original_filename}
                      </div>
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-500 mt-0.5">
                        <span className="px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 font-semibold">{item.language || 'Telugu'}</span>
                        <span>•</span>
                        <span>Doc #{docId}</span>
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <StatusBadge status={isUndigitized ? 'Pending' : item.status} />
                        {!isUndigitized && conf > 0 ? (
                          <span className="text-[11px] font-bold text-emerald-700">
                            {conf}%
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                            N/A (Un-digitized)
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="font-bold text-slate-900 text-xs">
                        {lr.owner_name || <span className="text-gray-400 italic">Not Detected</span>}
                      </div>
                      {lr.father_name && (
                        <div className="text-[10px] text-slate-500">
                          F: {lr.father_name}
                        </div>
                      )}
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="font-bold text-indigo-700 text-xs">
                        {lr.survey_number || lr.khasra_number || <span className="text-gray-400 italic">Not Detected</span>}
                      </div>
                      {lr.khata_number && (
                        <div className="text-[10px] text-slate-500">
                          Khata: {lr.khata_number}
                        </div>
                      )}
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="text-slate-800 text-xs font-semibold">
                        {lr.village ? `${lr.village}, ${lr.tehsil_mandal || lr.district || ''}` : 'Location Pending'}
                      </div>
                      {lr.area !== null && lr.area !== undefined && (
                        <div className="text-[10px] text-slate-500">
                          {lr.area} {lr.area_unit || 'Acres'}
                        </div>
                      )}
                    </td>

                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/verify/${docId}`)}
                          className="bg-slate-900 hover:bg-slate-800 text-white font-bold py-1.5 px-3 rounded-lg text-[11px] inline-flex items-center gap-1 shadow-sm transition cursor-pointer"
                          title="Open Verification Workspace"
                        >
                          <span>Verify</span>
                          <ArrowRight size={12} />
                        </button>
                        <button
                          onClick={() => window.open(documentService.getCertificateUrl(docId), '_blank')}
                          className="p-1.5 hover:bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg transition cursor-pointer"
                          title="Download Land Certificate"
                        >
                          <Download size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {filteredQueue.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-16 text-slate-400">
                    <ShieldCheck size={36} className="mx-auto mb-2 text-slate-300" />
                    <p className="font-bold text-sm text-slate-600">No documents found matching this filter</p>
                    <p className="text-xs text-slate-400 mt-1">Upload a land record or change filter criteria above.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default VerificationQueue;
