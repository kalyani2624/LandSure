import React from 'react';
import { CheckCircle2, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { authService } from '../services/api';
import { useSidebar } from '../context/SidebarContext';

const Navbar = () => {
  const user = authService.getCurrentUser();
  const { isCollapsed, toggleSidebar } = useSidebar();
  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <header className="bg-white border-b border-gray-200 h-[70px] pl-3 sm:pl-4 pr-6 sm:pr-8 flex items-center justify-between shadow-xs sticky top-0 z-40 w-full">
      {/* Top Left Brand Logo */}
      <div className="flex items-center shrink-0">
        <img 
          src="/landsure-logo-transparent.png" 
          alt="LandSure Cadastral Intelligence" 
          className="h-12 w-auto object-contain cursor-pointer transition-transform hover:scale-[1.02]" 
        />
      </div>

      {/* Right Header: Status, Date & User Profile */}
      <div className="flex items-center gap-4 sm:gap-6">
        {/* Connection Status */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
          <CheckCircle2 size={15} className="animate-pulse text-emerald-600" />
          <span className="hidden sm:inline">System Online</span>
          <span className="sm:hidden">Online</span>
        </div>

        {/* Date Display */}
        <div className="text-xs text-gray-600 font-semibold bg-gray-100 px-3.5 py-1.5 rounded-lg border border-gray-200 hidden lg:block">
          {today}
        </div>

        {/* User Profile Pill with Small Circle */}
        {user && (
          <div className="flex items-center gap-3 pl-3.5 border-l border-slate-200">
            <div className="w-9 h-9 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-xs shadow-xs shrink-0 ring-2 ring-emerald-100">
              {user.username ? user.username.substring(0, 2).toUpperCase() : 'RO'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-sm font-bold text-slate-900 leading-tight flex items-center gap-1.5">
                <span>{user.username || 'revenue_officer'}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              </div>
              <p className="text-[11px] text-slate-400 font-semibold leading-tight capitalize mt-0.5">
                {user.role || 'Revenue Officer'}
              </p>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
