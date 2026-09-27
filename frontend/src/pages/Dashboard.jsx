import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  ShieldAlert, 
  ArrowRight, 
  TrendingUp, 
  Clock, 
  ChevronRight, 
  UploadCloud, 
  Search, 
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import { dashboardService } from '../services/api';
import StatusBadge from '../components/StatusBadge';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await dashboardService.getStats();
      setStats(data);
      setError("");
    } catch (err) {
      console.error("Failed to fetch dashboard stats:", err);
      setError("Failed to fetch dashboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-4">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600"></div>
        <p className="text-xs font-semibold text-slate-500">Loading LandSure cadastral dashboard metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-rose-600 bg-white border border-rose-200 rounded-2xl max-w-xl mx-auto mt-12 shadow-sm space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mx-auto font-bold">
          !
        </div>
        <p className="font-bold text-slate-900">{error}</p>
        <button
          onClick={fetchStats}
          className="bg-slate-900 text-white text-xs font-bold py-2.5 px-5 rounded-xl hover:bg-slate-800 transition cursor-pointer"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const kpis = stats?.kpis || {
    total_documents: 0,
    digitized_records: 0,
    pending_review: 0,
    detected_anomalies: 0,
    total_area_acres: 0
  };

  const status_distribution = stats?.status_distribution || {
    "Verified": 0,
    "Pending Review": 0,
    "Low Confidence": 0,
    "Owner Conflict": 0,
    "Area Mismatch": 0,
    "Duplicate": 0
  };

  const recent_activity = stats?.recent_activity || stats?.recent_documents || [];

  const kpiCards = [
    { 
      label: "Total Uploaded Documents", 
      value: kpis.total_documents ?? 0, 
      icon: FileText, 
      color: "bg-blue-50 text-blue-600 border-blue-100", 
      desc: "All historical uploaded files",
      action: () => navigate('/upload'),
      actionLabel: "Upload Deed"
    },
    { 
      label: "Verified Digital Records", 
      value: kpis.digitized_records ?? 0, 
      icon: CheckCircle, 
      color: "bg-emerald-50 text-emerald-600 border-emerald-100", 
      desc: "Digitized records stored in db",
      action: () => navigate('/search'),
      actionLabel: "Search Records"
    },
    { 
      label: "Awaiting Officer Review", 
      value: kpis.pending_review ?? 0, 
      icon: AlertTriangle, 
      color: "bg-amber-50 text-amber-600 border-amber-100", 
      desc: "Requires human-in-the-loop review",
      action: () => navigate('/verification'),
      actionLabel: "Review Queue"
    },
    { 
      label: "Active Validation Anomalies", 
      value: kpis.detected_anomalies ?? 0, 
      icon: ShieldAlert, 
      color: "bg-rose-50 text-rose-600 border-rose-100", 
      desc: "Unresolved logic flags & conflicts",
      action: () => navigate('/verification'),
      actionLabel: "Resolve Flags"
    }
  ];

  const distributionValues = Object.values(status_distribution);
  const maxCount = distributionValues.length > 0 ? Math.max(...distributionValues, 1) : 1;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-950 p-8 rounded-2xl text-white shadow-md border border-slate-700/80 relative overflow-hidden">
        <div className="absolute right-0 top-0 opacity-10 pointer-events-none transform translate-x-12 -translate-y-6">
          <TrendingUp size={240} />
        </div>
        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
            <Sparkles size={14} />
            <span>AI Cadastral Intelligence Active</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
            Intelligent Land Record Digitization & Validation
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
            Monitor, validate, and verify historical Indian land record digitizations across Indic scripts. 
            All extractions are validated against state cadastral standards and cryptographically sealed.
          </p>

          {/* Quick Actions */}
          <div className="flex items-center gap-3 pt-2 flex-wrap">
            <button
              onClick={() => navigate('/upload')}
              className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xs transition cursor-pointer"
            >
              <UploadCloud size={16} />
              <span>Upload New Deed</span>
            </button>
            <button
              onClick={() => navigate('/verification')}
              className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold py-2.5 px-4 rounded-xl border border-slate-600 transition cursor-pointer"
            >
              <ShieldCheck size={16} />
              <span>Open Review Queue</span>
            </button>
            <button
              onClick={() => navigate('/search')}
              className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold py-2.5 px-4 rounded-xl border border-slate-600 transition cursor-pointer"
            >
              <Search size={16} />
              <span>Search Registry</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div 
              key={index} 
              onClick={card.action}
              className="p-6 rounded-2xl border border-slate-200/90 bg-white shadow-xs flex flex-col justify-between transition-all hover:shadow-md hover:border-slate-300 cursor-pointer group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <p className="text-[11px] text-slate-500 font-bold uppercase tracking-wider">{card.label}</p>
                  <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{card.value}</h3>
                </div>
                <div className={`p-3.5 rounded-xl border ${card.color} shrink-0`}>
                  <Icon size={22} />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold">
                <span className="text-slate-400 font-medium">{card.desc}</span>
                <span className="text-emerald-600 font-bold inline-flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                  {card.actionLabel}
                  <ChevronRight size={13} />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Analytics & Queue split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-xs lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900">
              Digitization Status Distribution
            </h3>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Real-time
            </span>
          </div>

          <div className="space-y-4 pt-1">
            {Object.entries(status_distribution).map(([status, count]) => {
              const percentage = Math.round((count / maxCount) * 100);
              let barColor = "bg-blue-600";
              if (status === 'Verified') barColor = "bg-emerald-600";
              else if (status === 'Pending Review' || status === 'Pending') barColor = "bg-amber-500";
              else if (status === 'Low Confidence') barColor = "bg-orange-500";
              else if (['Duplicate', 'Area Mismatch', 'Owner Conflict', 'Error', 'Rejected'].includes(status)) barColor = "bg-rose-600";

              return (
                <div key={status} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs font-semibold">
                    <span className="text-slate-700 font-medium">{status}</span>
                    <span className="text-slate-900 font-bold">{count}</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden border border-slate-200/60">
                    <div 
                      className={`${barColor} h-full rounded-full transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Activity Table */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs lg:col-span-2 flex flex-col justify-between overflow-hidden">
          <div>
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Clock size={16} className="text-emerald-600" />
                Recent Digitization Activity
              </h3>
              <button 
                onClick={() => navigate('/search')}
                className="text-xs text-emerald-700 hover:text-emerald-800 font-bold flex items-center gap-1 cursor-pointer"
              >
                View Registry
                <ChevronRight size={14} />
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-semibold">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 text-[10px] font-bold uppercase border-b border-slate-100">
                    <th className="px-6 py-3.5">File Name</th>
                    <th className="px-6 py-3.5">Language</th>
                    <th className="px-6 py-3.5">Confidence</th>
                    <th className="px-6 py-3.5">Status</th>
                    <th className="px-6 py-3.5">Uploaded</th>
                    <th className="px-6 py-3.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {recent_activity.map((activity) => {
                    const knownUnDigitizedDeeds = [
                      'komaripati', 'venkateswara', 'cj 475829', '216/2',
                      'hiteshbhai', 'amrutlal', 'gj 361245',
                      'arun kumar', 'ramasamy', 'tn 685214',
                      'mohan lal', 'harishchandra', 'bk 125678', '145/1'
                    ];
                    const fn = (activity.original_filename || activity.filename || '').toLowerCase();
                    const isUndigitized = knownUnDigitizedDeeds.some(t => fn.includes(t));

                    return (
                      <tr key={activity.id} className="hover:bg-slate-50/60 transition">
                        <td className="px-6 py-4 font-bold text-slate-900 truncate max-w-[180px]">
                          {activity.original_filename || activity.filename || `Document #${activity.id}`}
                        </td>
                        <td className="px-6 py-4 text-slate-500 font-medium capitalize">
                          {activity.language || "Indic"}
                        </td>
                        <td className="px-6 py-4">
                          {!isUndigitized && activity.confidence_score > 0 ? (
                            <span className={`text-xs font-bold ${
                              activity.confidence_score >= 80 ? "text-emerald-600" :
                              activity.confidence_score >= 60 ? "text-amber-600" : "text-rose-600"
                            }`}>
                              {activity.confidence_score}%
                            </span>
                          ) : (
                            <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                              N/A
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={isUndigitized ? 'Pending' : activity.status} />
                        </td>
                      <td className="px-6 py-4 text-xs text-slate-400 font-medium">
                        {activity.created_at ? new Date(activity.created_at).toLocaleDateString('en-IN') : 'Recent'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => {
                            if (activity.status === 'Verified') {
                              navigate(`/processing/${activity.id}`);
                            } else {
                              navigate(`/verify/${activity.id}`);
                            }
                          }}
                          className="text-xs text-slate-800 font-bold bg-slate-100 hover:bg-slate-200 hover:text-slate-900 py-1.5 px-3 rounded-lg border border-slate-200 inline-flex items-center gap-1 transition cursor-pointer shadow-xs"
                        >
                          Review
                          <ArrowRight size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                  {recent_activity.length === 0 && (
                    <tr>
                      <td colSpan="6" className="text-center py-10 text-slate-400 font-medium text-xs">
                        No recent activity recorded yet. Upload a land document to begin.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          <div className="p-4 bg-slate-50/70 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-500 font-medium">
              LandSure AI performs OCR extraction and anomaly checks automatically. Documents requiring officer sign-off appear in the Review Queue.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
