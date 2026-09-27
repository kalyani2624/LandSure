import React from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  HelpCircle, 
  Loader2, 
  Copy, 
  Users, 
  Scale, 
  XCircle 
} from 'lucide-react';

const StatusBadge = ({ status }) => {
  let badgeStyles = "";
  let icon = null;
  let label = status;

  switch (status) {
    case 'Verified':
      badgeStyles = "bg-emerald-50 text-emerald-700 border-emerald-200";
      icon = <CheckCircle size={14} />;
      label = "Verified";
      break;
    case 'Processing':
      badgeStyles = "bg-blue-50 text-blue-700 border-blue-200";
      icon = <Loader2 size={14} className="animate-spin" />;
      label = "Processing...";
      break;
    case 'Pending Review':
      badgeStyles = "bg-amber-50 text-amber-700 border-amber-200";
      icon = <HelpCircle size={14} />;
      label = "Pending Review";
      break;
    case 'Low Confidence':
      badgeStyles = "bg-orange-50 text-orange-700 border-orange-200";
      icon = <AlertTriangle size={14} />;
      label = "Low Confidence";
      break;
    case 'Duplicate':
      badgeStyles = "bg-slate-100 text-slate-700 border-slate-300";
      icon = <Copy size={14} />;
      label = "Duplicate Warning";
      break;
    case 'Area Mismatch':
      badgeStyles = "bg-rose-50 text-rose-700 border-rose-200";
      icon = <Scale size={14} />;
      label = "Area Mismatch";
      break;
    case 'Owner Conflict':
      badgeStyles = "bg-red-50 text-red-700 border-red-200";
      icon = <Users size={14} />;
      label = "Owner Conflict";
      break;
    case 'Error':
    case 'Rejected':
      badgeStyles = "bg-red-100 text-red-800 border-red-300";
      icon = <XCircle size={14} />;
      label = "Rejected / Error";
      break;
    default:
      badgeStyles = "bg-gray-50 text-gray-700 border-gray-200";
      icon = <HelpCircle size={14} />;
      break;
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeStyles}`}>
      {icon}
      <span>{label}</span>
    </span>
  );
};

export default StatusBadge;
