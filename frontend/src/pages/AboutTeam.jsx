import React from 'react';
import { 
  Users, 
  Code2, 
  Cpu, 
  ShieldCheck, 
  Layers, 
  Sparkles, 
  FileText, 
  Database, 
  Globe, 
  Github, 
  Linkedin, 
  ExternalLink,
  Award,
  CheckCircle2,
  Terminal,
  Activity
} from 'lucide-react';

const AboutTeam = () => {
  // Developer Team Members (6 Members including Team Lead)
  const teamMembers = [
    {
      name: "Nikhil Appari",
      role: "Team Lead & Full-Stack Architect",
      isLead: true,
      focus: "End-to-end Platform Architecture, Indic OCR Pipeline & Cryptographic Verification",
      avatar: "NA",
      color: "bg-emerald-600",
      skills: ["FastAPI", "React 18", "System Design", "Python", "DILRMP Standards"],
      github: "https://github.com/nikhilappari/",
      linkedin: "https://www.linkedin.com/in/nikhil-appari-365810309/"
    },
    {
      name: "Hemanth Birda",
      role: "AI / ML & Indic OCR Lead",
      isLead: false,
      focus: "Multilingual Indic Script Recognition, Bounding Box Alignment & LLM Parsing",
      avatar: "HB",
      color: "bg-indigo-600",
      skills: ["PyTorch", "IndicNLP", "Gemini Vision", "Tesseract", "HuggingFace"]
    },
    {
      name: "Sai Naidu Yalla",
      role: "Computer Vision & Preprocessing Engineer",
      isLead: false,
      focus: "Adaptive Document Thresholding, Deskewing, Noise Reduction & dHash Matching",
      avatar: "SY",
      color: "bg-purple-600",
      skills: ["OpenCV", "Perceptual Hashing", "Scikit-Image", "NumPy", "Pillow"]
    },
    {
      name: "Poojitha Bellam",
      role: "Backend & Cadastral Database Architect",
      isLead: false,
      focus: "Cadastral Rule Engine, Anomaly Detection, SQL Schemas & PDF Certificate Generator",
      avatar: "PB",
      color: "bg-blue-600",
      skills: ["FastAPI", "SQLAlchemy", "SQLite/Postgres", "ReportLab", "REST APIs"]
    },
    {
      name: "Kalyani Bondi",
      role: "Frontend & UI/UX Specialist",
      isLead: false,
      focus: "Interactive Verification Workspace, Responsive Dashboards & Component Library",
      avatar: "KB",
      color: "bg-amber-600",
      skills: ["React 18", "Vite", "Tailwind CSS", "Lucide React", "UI/UX"]
    },
    {
      name: "Madhavi Nakka",
      role: "Security & GIS QA Engineer",
      isLead: false,
      focus: "SHA-256 Ledger Integrity, JWT RBAC Authentication & Spatial Map Integration",
      avatar: "MN",
      color: "bg-rose-600",
      skills: ["Cryptographic Hashing", "JWT Auth", "GIS Mapping", "Unit Testing", "CI/CD"]
    }
  ];

  // Tech Stack Categories
  const techStack = [
    {
      category: "Frontend Experience",
      icon: Code2,
      color: "text-blue-500 bg-blue-50 border-blue-200",
      tools: [
        { name: "React 18", desc: "Declarative, component-driven UI architecture" },
        { name: "Vite 5", desc: "Ultra-fast Next-Gen frontend tooling & HMR" },
        { name: "Tailwind CSS", desc: "Utility-first modern responsive styling" },
        { name: "Lucide React", desc: "Clean, consistent enterprise icon system" },
      ]
    },
    {
      category: "Backend & API Layer",
      icon: Terminal,
      color: "text-emerald-500 bg-emerald-50 border-emerald-200",
      tools: [
        { name: "FastAPI", desc: "High-performance asynchronous Python 3.11 web framework" },
        { name: "SQLAlchemy ORM", desc: "Robust database abstraction & relational mapping" },
        { name: "ReportLab", desc: "Server-side cryptographic PDF certificate generator" },
        { name: "Pydantic v2", desc: "Strict schema validation & serialization engine" },
      ]
    },
    {
      category: "AI, OCR & Computer Vision",
      icon: Cpu,
      color: "text-indigo-500 bg-indigo-50 border-indigo-200",
      tools: [
        { name: "Indic OCR Pipeline", desc: "Recognition across Telugu, Tamil, Hindi, Gujarati, Kannada, Marathi, Odia" },
        { name: "Perceptual dHash / aHash", desc: "Zero-latency image fingerprinting & benchmark matching" },
        { name: "LLM Extraction", desc: "Contextual cadastral structuring via Gemini / Groq Vision" },
        { name: "OpenCV Preprocessing", desc: "Adaptive thresholding, deskewing & document denoising" },
      ]
    },
    {
      category: "Security & Validation",
      icon: ShieldCheck,
      color: "text-amber-500 bg-amber-50 border-amber-200",
      tools: [
        { name: "SHA-256 Digital Seal", desc: "Cryptographic tamper-evident deed verification hash" },
        { name: "Cadastral Rule Engine", desc: "Area math validation, plot sub-division & chain-of-title audits" },
        { name: "JWT Auth & RBAC", desc: "Secure role-based revenue officer authentication" },
        { name: "Immutable Audit Trail", desc: "Complete historical provenance & change tracking" },
      ]
    }
  ];

  const highlights = [
    { label: "Supported Languages", value: "8+ Indic Scripts" },
    { label: "Verification Confidence", value: "93% - 98%" },
    { label: "Processing Latency", value: "< 2.5s / Deed" },
    { label: "Government Compliance", value: "DILRMP Standard" },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-950 p-8 rounded-2xl text-white shadow-md border border-slate-700/80 relative overflow-hidden">
        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
            <Sparkles size={14} />
            <span>Smart India Hackathon 2026 • Cadastral Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
            About LandSure & Development Team
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
            LandSure is an enterprise AI-powered land record digitization and verification platform engineered 
            to solve historical legacy document modernization, multilingual Indic OCR recognition, and dispute-free 
            cadastral ledger governance.
          </p>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
            {highlights.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-800/80 rounded-xl border border-slate-700">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{item.label}</div>
                <div className="text-sm font-extrabold text-emerald-400 mt-0.5">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Core Development Team */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Users size={20} className="text-emerald-600" />
              Core Engineering Team
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Architects and developers behind the LandSure digitization engine
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
            6 Team Members (Team Lead + 5)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {teamMembers.map((member, index) => (
            <div 
              key={index}
              className={`bg-white p-6 rounded-2xl border ${
                member.isLead ? 'border-emerald-300 shadow-sm ring-1 ring-emerald-100' : 'border-slate-200/90 shadow-xs'
              } flex flex-col justify-between hover:shadow-md transition group space-y-5 relative`}
            >
              {member.isLead && (
                <div className="absolute top-4 right-4 bg-emerald-600 text-white text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow-xs">
                  ★ Team Lead
                </div>
              )}

              <div className="space-y-4">
                {/* Avatar & Header */}
                <div className="flex items-center gap-3.5">
                  <div className={`w-12 h-12 rounded-2xl ${member.color} text-white font-black flex items-center justify-center text-sm shadow-xs shrink-0 ring-4 ring-slate-100`}>
                    {member.avatar}
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-slate-900 leading-tight">
                      {member.name}
                    </h3>
                    <p className="text-[11px] font-bold text-emerald-600 leading-tight mt-0.5">
                      {member.role}
                    </p>
                  </div>
                </div>

                {/* Focus description */}
                <p className="text-xs text-slate-600 font-medium leading-relaxed">
                  {member.focus}
                </p>

                {/* Skill Pills */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {member.skills.map((skill, sIdx) => (
                    <span 
                      key={sIdx}
                      className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md border border-slate-200/60"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Social / Contact Links (Only for Team Lead) */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-end text-xs font-semibold text-slate-500">
                {member.github || member.linkedin ? (
                  <div className="flex items-center gap-2">
                    {member.github && (
                      <a 
                        href={member.github} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-600 hover:text-slate-900 transition"
                        title="GitHub Profile"
                      >
                        <Github size={15} />
                      </a>
                    )}
                    {member.linkedin && (
                      <a 
                        href={member.linkedin} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="p-1.5 hover:bg-blue-50 rounded-lg text-blue-600 hover:text-blue-700 transition"
                        title="LinkedIn Profile"
                      >
                        <Linkedin size={15} />
                      </a>
                    )}
                  </div>
                ) : (
                  <span className="text-[10px] font-bold text-slate-400 bg-slate-50 border border-slate-200/60 px-2.5 py-0.5 rounded-full">
                    Core Developer
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack Overview */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Layers size={20} className="text-indigo-600" />
            Architecture & Technology Stack
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Production-grade stack engineered for high accuracy Indic document processing
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {techStack.map((category, idx) => {
            const Icon = category.icon;
            return (
              <div 
                key={idx}
                className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-xs space-y-4"
              >
                <div className="flex items-center gap-3 border-b border-slate-100 pb-3">
                  <div className={`p-2 rounded-xl border ${category.color}`}>
                    <Icon size={18} />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">
                    {category.category}
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {category.tools.map((tool, tIdx) => (
                    <div 
                      key={tIdx}
                      className="p-3 bg-slate-50/70 rounded-xl border border-slate-200/60 space-y-1"
                    >
                      <div className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                        <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
                        <span>{tool.name}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 font-medium leading-relaxed">
                        {tool.desc}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Objectives & Compliance Footer Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-xs flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 border border-emerald-200 rounded-xl shrink-0 mt-0.5">
            <Award size={24} />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-900">
              National Cadastral Modernization Objective
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed font-medium max-w-3xl">
              Engineered for the Digital India Land Records Modernization Programme (DILRMP) to replace manual, error-prone 
              land revenue workflows with verifiable, cryptographically sealed digital title extracts.
            </p>
          </div>
        </div>
        <div className="shrink-0">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold shadow-xs">
            <Activity size={14} className="text-emerald-400" />
            <span>LandSure v2.4.0 Live</span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default AboutTeam;
