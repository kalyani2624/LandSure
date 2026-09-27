import React from 'react';

const LandSureLogo = ({ className = "h-11", isDark = true }) => {
  const primaryTextColor = isDark ? "#FFFFFF" : "#0F172A";
  const subTextColor = isDark ? "#CBD5E1" : "#64748B";
  const dividerColor = isDark ? "#334155" : "#E2E8F0";
  const roofColor = isDark ? "#FFFFFF" : "#0F172A";
  const emeraldColor = "#10B981";
  const emeraldDark = "#059669";
  const emeraldLight = "#34D399";

  return (
    <div className={`flex items-center gap-3.5 select-none ${className}`}>
      {/* Emblem SVG */}
      <svg 
        viewBox="0 0 100 100" 
        className="h-full w-auto aspect-square shrink-0"
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* House Roof Top */}
        <path 
          d="M 50 12 L 14 42 L 20 46 L 50 22 L 80 46 L 86 42 Z" 
          fill={roofColor} 
        />
        
        {/* 4 Window Panes */}
        <rect x="43" y="30" width="5.5" height="5.5" rx="1" fill={roofColor} />
        <rect x="51.5" y="30" width="5.5" height="5.5" rx="1" fill={roofColor} />
        <rect x="43" y="38" width="5.5" height="5.5" rx="1" fill={roofColor} />
        <rect x="51.5" y="38" width="5.5" height="5.5" rx="1" fill={roofColor} />

        {/* Agricultural Curved Contour Fields (Circular base) */}
        {/* Layer 1: Left green curve */}
        <path 
          d="M 16 52 C 22 51 38 56 49 67 C 32 67 22 62 16 52 Z" 
          fill={emeraldDark} 
        />
        {/* Layer 2: Right green curve */}
        <path 
          d="M 84 52 C 78 51 62 56 51 67 C 68 67 78 62 84 52 Z" 
          fill={emeraldDark} 
        />
        {/* Layer 3: Middle lower field arcs */}
        <path 
          d="M 21 66 C 32 66 45 74 50 86 C 41 83 29 76 21 66 Z" 
          fill={emeraldColor} 
        />
        <path 
          d="M 79 66 C 68 66 55 74 50 86 C 59 83 71 76 79 66 Z" 
          fill={emeraldLight} 
        />
        {/* Outer Circular Boundary Arcs */}
        <path 
          d="M 16 52 C 16 71 31 87 50 87 C 69 87 84 71 84 52 C 77 56 68 60 50 60 C 32 60 23 56 16 52 Z" 
          fill={emeraldColor}
          fillOpacity="0.85"
        />
      </svg>

      {/* Vertical Sleek Divider */}
      <div 
        className="h-8 w-[1.5px] rounded-full self-center" 
        style={{ backgroundColor: dividerColor }}
      />

      {/* Typography */}
      <div className="flex flex-col justify-center">
        <div className="flex items-center text-xl font-black tracking-tight leading-none">
          <span style={{ color: primaryTextColor }}>Land</span>
          <span style={{ color: emeraldColor }} className="ml-0.5">Sure</span>
        </div>
        <span 
          className="text-[9px] font-bold tracking-[0.22em] uppercase mt-1 leading-none"
          style={{ color: subTextColor }}
        >
          Cadastral Intelligence
        </span>
      </div>
    </div>
  );
};

export default LandSureLogo;
