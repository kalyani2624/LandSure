import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ChevronLeft, 
  Download, 
  History, 
  FileText, 
  MapPin, 
  Calendar,
  Landmark,
  Scale,
  ShieldCheck,
  Building,
  Layers,
  Sparkles
} from 'lucide-react';
import { recordService, verificationService } from '../services/api';

const RecordDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [record, setRecord] = useState(null);
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      setError("");
      try {
        let recData = null;
        try {
          recData = await recordService.getDetails(id);
        } catch (fetchErr) {
          // If direct ID lookup returned 404, check search query
          const searchRes = await recordService.search();
          recData = searchRes.find(r => String(r.id) === String(id) || String(r.document_id) === String(id));
        }

        const actualRecord = recData.record || recData;
        setRecord(actualRecord);
        
        // Fetch audit logs safely
        try {
          const auditData = await verificationService.getAudits(actualRecord.id || id);
          setAudits(Array.isArray(auditData) ? auditData : []);
        } catch (auditErr) {
          console.warn("Audit logs unavailable for record:", auditErr);
          setAudits([]);
        }
      } catch (err) {
        console.error("Failed to retrieve land record:", err);
        setError(err.response?.data?.detail || err.message || "Failed to retrieve land record details.");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchDetails();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-4">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600"></div>
        <p className="text-xs font-semibold text-slate-500">Retrieving digitized land record...</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="max-w-xl mx-auto mt-16 p-8 bg-white border border-slate-200 rounded-2xl shadow-sm text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mx-auto font-bold">
          !
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">Land Record Retrieval</h3>
          <p className="text-xs text-rose-600 font-medium mt-1">{error || "Record not found in the official registry."}</p>
        </div>
        <button
          onClick={() => navigate('/search')}
          className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 px-5 rounded-xl text-xs transition cursor-pointer shadow-sm"
        >
          <ChevronLeft size={16} />
          Back to Registry Search
        </button>
      </div>
    );
  }

  const handleDownloadPDF = () => {
    window.open(recordService.getExportPDFUrl(record.id), '_blank');
  };

  const getBilingualValue = (field, englishVal) => {
    if (englishVal === null || englishVal === undefined || englishVal === "") return "N/A";
    const regVal = record.regional_values?.[field];
    const nativeVal = typeof regVal === 'object' && regVal !== null ? regVal.original_value : regVal;
    return nativeVal && nativeVal !== String(englishVal) ? `${englishVal} (${nativeVal})` : `${englishVal}`;
  };

  const surveyKhasra = record.survey_number || record.khasra_number || "N/A";

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/search')}
            className="p-2.5 hover:bg-slate-100 rounded-xl text-slate-500 hover:text-slate-900 transition border border-slate-200 cursor-pointer"
            title="Back to Registry Search"
          >
            <ChevronLeft size={18} />
          </button>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                Record: DIG-LR-{String(record.id).padStart(6, '0')}
              </h1>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <ShieldCheck size={13} />
                {(record.verification_status || 'VERIFIED').toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-1">
              Registered Owner: <span className="font-bold text-slate-800">{record.owner_name}</span> • Digitized on {new Date(record.created_at || Date.now()).toLocaleDateString('en-IN')}
            </p>
          </div>
        </div>

        <button
          onClick={handleDownloadPDF}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center gap-2 shadow-sm transition border border-emerald-500 cursor-pointer self-start sm:self-auto"
        >
          <Download size={15} />
          Download Certificate (PDF)
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Land Property Specifications Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Landmark size={18} className="text-emerald-600" />
                Cadastral Property Specifications
              </h3>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Official Extract
              </span>
            </div>

            {/* Structured specifications display */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 text-xs font-medium">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Pattadar / Owner Name</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("owner_name", record.owner_name)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Father / Spouse Name</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("father_name", record.father_name || "N/A")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Survey / Khasra Number</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("survey_number", surveyKhasra)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Khata / Plot Number</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("khata_number", record.khata_number || record.plot_number || "N/A")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Total Registered Extent</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("area", record.area !== null ? `${record.area} ${record.area_unit || 'Acres'}` : "N/A")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Land Classification</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("land_classification", record.land_classification || "Agricultural")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Ownership Category</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("ownership_type", record.ownership_type || "Pattadar / Self-owned")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-slate-500 font-bold">Registration / Stamp No.</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("registration_number", record.registration_number || "N/A")}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100 md:col-span-2">
                <span className="text-slate-500 font-bold">Registration / Execution Date</span>
                <span className="text-slate-900 font-bold text-right">{getBilingualValue("registration_date", record.registration_date || "N/A")}</span>
              </div>
            </div>
          </div>

          {/* Audit Logs Table */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <History size={17} className="text-indigo-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Verification Modifications & Audit Log
                </h3>
              </div>
              <span className="text-[10px] font-bold text-slate-400">
                Immutable Ledger
              </span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-semibold">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 text-[10px] font-bold uppercase border-b border-gray-100">
                    <th className="px-6 py-3.5">Modified Field</th>
                    <th className="px-6 py-3.5">Old Staged Value</th>
                    <th className="px-6 py-3.5">Verified Sealed Value</th>
                    <th className="px-6 py-3.5">Audited User</th>
                    <th className="px-6 py-3.5 text-right">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-slate-700">
                  {audits.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50/50">
                      <td className="px-6 py-3.5 font-bold text-slate-800">
                        {a.field_name}
                      </td>
                      <td className="px-6 py-3.5 text-rose-600 line-through">
                        {a.old_value || "None"}
                      </td>
                      <td className="px-6 py-3.5 text-emerald-600 font-bold">
                        {a.new_value || "None"}
                      </td>
                      <td className="px-6 py-3.5 text-slate-500 font-bold">
                        {a.user_username || "revenue_officer"}
                      </td>
                      <td className="px-6 py-3.5 text-right text-gray-400 font-medium">
                        {new Date(a.timestamp).toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))}
                  {audits.length === 0 && (
                    <tr>
                      <td colSpan="5" className="text-center py-8 text-slate-400 font-medium text-xs">
                        No manual edits have been logged for this record.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Location & Metadata Panel */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm space-y-4">
            <h3 className="text-xs font-bold uppercase text-slate-700 tracking-wider flex items-center gap-1.5">
              <MapPin size={14} className="text-emerald-600" />
              Administrative Jurisdiction
            </h3>
            
            <div className="space-y-3 font-medium text-xs">
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-3">
                <Building size={16} className="text-slate-500 mt-0.5 shrink-0" />
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase">District Boundary</div>
                  <div className="font-bold text-slate-900 mt-0.5">{record.district || "N/A"}</div>
                </div>
              </div>
              
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-3">
                <Building size={16} className="text-slate-500 mt-0.5 shrink-0" />
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase">Tehsil / Mandal Office</div>
                  <div className="font-bold text-slate-900 mt-0.5">{record.tehsil_mandal || "N/A"}</div>
                </div>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-3">
                <MapPin size={16} className="text-slate-500 mt-0.5 shrink-0" />
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase">Revenue Village Area</div>
                  <div className="font-bold text-slate-900 mt-0.5">{record.village || "N/A"}</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Back Action link */}
          {record.document_id && (
            <button
              onClick={() => navigate(`/processing/${record.document_id}`)}
              className="w-full flex items-center justify-center gap-2 bg-slate-50 hover:bg-slate-100 text-slate-800 py-3 rounded-xl border border-slate-200 text-xs font-bold transition shadow-sm cursor-pointer"
            >
              <FileText size={14} className="text-indigo-600" />
              Inspect Original Scanning Result
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecordDetails;
