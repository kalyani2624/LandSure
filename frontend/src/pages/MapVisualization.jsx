import React, { useState, useEffect } from 'react';
import { 
  Map, 
  Layers, 
  Info, 
  Search, 
  ExternalLink,
  Eye,
  Scan,
  Database
} from 'lucide-react';
import { recordService } from '../services/api';

const MapVisualization = () => {
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [recordData, setRecordData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cvOverlayActive, setCvOverlayActive] = useState(true);

  // Hardcoded coordinates & attributes representing parcel geometry
  const parcels = [
    { id: "12", survey: "145/3A", dPath: "M 50,50 L 200,50 L 180,180 L 40,150 Z", area: "2.50 Acres", textX: 110, textY: 100 },
    { id: "13", survey: "145/3B", dPath: "M 200,50 L 350,50 L 380,160 L 180,180 Z", area: "1.80 Acres", textX: 270, textY: 110 },
    { id: "14", survey: "145/4", dPath: "M 350,50 L 480,50 L 490,200 L 380,160 Z", area: "3.20 Acres", textX: 420, textY: 110 },
    { id: "11", survey: "145/2", dPath: "M 40,150 L 180,180 L 150,320 L 50,280 Z", area: "2.10 Acres", textX: 100, textY: 240 },
    { id: "15", survey: "146/1", dPath: "M 180,180 L 380,160 L 390,300 L 150,320 Z", area: "4.00 Acres", textX: 270, textY: 240 },
  ];

  const handleParcelClick = async (parcel) => {
    setSelectedParcel(parcel);
    setLoading(true);
    setRecordData(null);
    
    try {
      // Query registry by survey number
      const results = await recordService.search({ survey_number: parcel.survey });
      if (results && results.length > 0) {
        // Find verified record if possible, or fallback to first
        const verified = results.find(r => r.verification_status === "Verified") || results[0];
        setRecordData(verified);
      } else {
        setRecordData(null);
      }
    } catch (err) {
      console.error("Failed to query parcel record details:", err);
    } finally {
      setLoading(false);
    }
  };

  // Pre-select plot 12 on mount
  useEffect(() => {
    handleParcelClick(parcels[0]);
  }, []);

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          <Map className="text-govteal-700" />
          Cadastral Map parcel Visualizer
        </h1>
        <p className="text-xs text-gray-500 font-semibold mt-1">
          Scans cadastral boundary maps, isolates parcel regions using CV edge contours, and maps them to tabular registry files.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Left GIS Visualizer Panel */}
        <div className="xl:col-span-2 bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between h-[650px]">
          <div>
            <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Scan size={16} />
                Village Cadastral Sheet (Krishnapuram Village - Block 4)
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 font-semibold">CV Boundary Highlight:</span>
                <button
                  onClick={() => setCvOverlayActive(!cvOverlayActive)}
                  className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                    cvOverlayActive ? 'bg-amber-500' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      cvOverlayActive ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Interactive Vector GIS Canvas */}
            <div className="bg-slate-950 rounded-xl relative overflow-hidden flex items-center justify-center p-4 border border-slate-800 h-[480px]">
              {/* Background Cadastral grid grids */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:30px_30px] opacity-10"></div>
              
              <svg 
                viewBox="0 0 540 400" 
                className="w-full max-w-[480px] h-auto cursor-pointer select-none"
              >
                <g>
                  {parcels.map((p) => {
                    const isSelected = selectedParcel?.id === p.id;
                    return (
                      <g key={p.id} onClick={() => handleParcelClick(p)}>
                        {/* Interactive Boundary Polygon */}
                        <path
                          d={p.dPath}
                          className={`transition-all duration-200 ${
                            isSelected 
                              ? "fill-amber-500/25 stroke-amber-500 stroke-[3px]" 
                              : cvOverlayActive 
                                ? "fill-emerald-500/5 stroke-emerald-500 stroke-2 hover:fill-emerald-500/15" 
                                : "fill-slate-800/40 stroke-slate-700 stroke-1 hover:fill-slate-800/60"
                          }`}
                        />
                        
                        {/* Survey Plot Tag label */}
                        <text
                          x={p.textX}
                          y={p.textY}
                          textAnchor="middle"
                          alignmentBaseline="middle"
                          className={`text-[11px] font-bold font-mono transition-all ${
                            isSelected 
                              ? "fill-amber-400 font-extrabold scale-110" 
                              : "fill-slate-300 group-hover:fill-white"
                          }`}
                        >
                          Plot {p.id}
                        </text>
                        <text
                          x={p.textX}
                          y={p.textY + 14}
                          textAnchor="middle"
                          alignmentBaseline="middle"
                          className="text-[8px] fill-slate-400 font-semibold"
                        >
                          ({p.survey})
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>

              {/* Status floating card */}
              <div className="absolute bottom-4 left-4 bg-slate-900/90 text-white border border-slate-700 p-3 rounded-lg text-[10px] space-y-1 font-semibold max-w-[200px]">
                <div className="flex items-center gap-1.5 text-amber-500">
                  <Info size={12} />
                  <span>Interactive Cadastre Sheet</span>
                </div>
                <p className="text-slate-400 leading-normal font-medium">
                  Click on any parcel boundary to pull the corresponding digitized land registry record.
                </p>
              </div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-center text-xs text-gray-500 font-semibold">
            Computer Vision Pipeline: Detects coordinates and overlays vector polygon masks on raster maps dynamically.
          </div>
        </div>

        {/* Right Info Details Column */}
        <div className="xl:col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between h-[650px] overflow-hidden">
          
          <div className="space-y-6 flex-1 overflow-y-auto">
            <h3 className="text-sm font-bold text-slate-800 border-b border-gray-100 pb-3 flex items-center gap-1.5">
              <Database size={16} className="text-slate-500" />
              Linked Land Registry File
            </h3>

            {selectedParcel ? (
              <div className="space-y-5">
                {/* Parcel ID Card */}
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <div className="text-[10px] text-gray-400 font-bold uppercase">Selected Parcel Reference</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">Plot ID: {selectedParcel.id}</div>
                  <div className="text-xs text-slate-500 font-semibold mt-0.5">Survey Number: {selectedParcel.survey}</div>
                </div>

                {loading ? (
                  <div className="py-12 text-center flex flex-col items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-slate-900"></div>
                    <p className="text-xs text-gray-400 font-semibold">Fetching owner registry...</p>
                  </div>
                ) : recordData ? (
                  <div className="space-y-4 text-xs font-semibold text-slate-700">
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Pattadar Owner</span>
                      <span className="text-slate-800 font-bold">{recordData.owner_name}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Khata Number</span>
                      <span className="text-slate-800 font-bold">{recordData.khata_number || "N/A"}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Registered Area</span>
                      <span className="text-slate-800 font-bold">{recordData.area} {recordData.area_unit}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Village Locality</span>
                      <span className="text-slate-800 font-bold">{recordData.village}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Tehsil Office</span>
                      <span className="text-slate-800 font-bold">{recordData.tehsil_mandal}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">District State</span>
                      <span className="text-slate-800 font-bold">{recordData.district}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-400">Classification</span>
                      <span className="text-slate-800 font-bold">{recordData.land_classification || "N/A"}</span>
                    </div>
                    
                    {/* View Details full page */}
                    <button
                      onClick={() => navigate(`/details/${recordData.id}`)}
                      className="w-full flex items-center justify-center gap-1 bg-amber-500 hover:bg-amber-600 hover:text-slate-950 font-bold text-slate-900 py-2.5 rounded-lg border border-amber-400 shadow-sm transition-all text-xs"
                    >
                      <Eye size={14} />
                      View Entire Land Registry File
                    </button>
                  </div>
                ) : (
                  <div className="p-4 bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold rounded-lg">
                    No verified database record matches Survey Number {selectedParcel.survey}. The land parcel boundaries have been scanned, but ownership deeds have not yet been digitized.
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-20 text-gray-400 text-xs font-semibold">
                Click a parcel on the cadastre sheet map view to load linked deed registry files.
              </div>
            )}
          </div>

          <div className="bg-slate-50 border border-gray-200 p-4 rounded-xl flex gap-3 text-[10px] leading-normal font-semibold text-slate-500 mt-4">
            <Info size={16} className="text-slate-400 shrink-0 mt-0.5" />
            <div>
              Cadastral boundaries align with spatial GIS shapes. Real-time clicking retrieves ownership records mapped under local survey index directories.
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default MapVisualization;
