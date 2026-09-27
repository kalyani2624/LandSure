import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  ShieldCheck, 
  Search, 
  Map, 
  LogOut,
  Users,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  FileStack
} from 'lucide-react';
import { authService } from '../services/api';
import { useSidebar } from '../context/SidebarContext';

const Sidebar = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  const { isCollapsed, toggleSidebar, setIsCollapsed } = useSidebar();

  const handleLogout = (e) => {
    e.stopPropagation();
    authService.logout();
    navigate('/login');
  };

  const handleSidebarClick = (e) => {
    // If currently collapsed, clicking anywhere on the dark sidebar opens it
    if (isCollapsed) {
      setIsCollapsed(false);
    }
  };

  const handleHeaderClick = (e) => {
    e.stopPropagation();
    toggleSidebar();
  };

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, tooltip: 'Dashboard Overview' },
    { to: '/upload', label: 'Upload Document', icon: UploadCloud, tooltip: 'Upload & Process Deed' },
    { to: '/verification', label: 'Review Queue', icon: ShieldCheck, tooltip: 'Review & Verify Records' },
    { to: '/search', label: 'Registry Search', icon: Search, tooltip: 'Search Land Records' },
    { to: '/sample-records', label: 'Sample Records', icon: FileStack, tooltip: 'Sample Cadastral Records' },
    { to: '/about', label: 'About & Team', icon: Users, tooltip: 'Developers & Tech Stack' },
  ];

  return (
    <aside 
      onClick={handleSidebarClick}
      className={`${
        isCollapsed ? 'w-20 cursor-pointer' : 'w-68'
      } bg-slate-900 min-h-[calc(100vh-70px)] flex flex-col justify-between border-r border-slate-800 shadow-md shrink-0 select-none transition-all duration-300 ease-in-out relative`}
    >
      <div className={`p-3 ${isCollapsed ? 'px-2.5' : 'p-4'} space-y-4`}>
        {/* Navigation Menu Header - Click to toggle Open/Closed */}
        <div 
          onClick={handleHeaderClick}
          title={isCollapsed ? "Click dark sidebar to expand" : "Click to collapse sidebar"}
          className={`flex items-center ${
            isCollapsed ? 'justify-center' : 'justify-between px-3'
          } py-1.5 rounded-lg hover:bg-slate-800/60 cursor-pointer transition text-slate-400 hover:text-white`}
        >
          {!isCollapsed && (
            <span className="text-[11px] font-bold uppercase tracking-widest text-slate-400">
              Navigation Menu
            </span>
          )}
          <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 hover:text-emerald-400 transition">
            {isCollapsed ? (
              <ChevronsRight size={16} />
            ) : (
              <>
                <span className="text-[9px] uppercase tracking-wider bg-slate-800/80 px-2 py-0.5 rounded text-slate-400">Hide</span>
                <ChevronsLeft size={16} />
              </>
            )}
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                title={isCollapsed ? item.label : undefined}
                className={({ isActive }) =>
                  `group relative flex items-center ${
                    isCollapsed ? 'justify-center p-3' : 'justify-between px-4 py-3'
                  } rounded-xl text-sm font-bold transition-all ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50 border border-emerald-500'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/90 font-medium'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3.5'}`}>
                      <Icon 
                        size={21} 
                        className={`transition shrink-0 ${
                          isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                        }`} 
                      />
                      {!isCollapsed && (
                        <span className="text-sm font-semibold tracking-tight whitespace-nowrap">
                          {item.label}
                        </span>
                      )}
                    </div>

                    {!isCollapsed && (
                      <ChevronRight 
                        size={16} 
                        className={`transition shrink-0 ${
                          isActive ? 'text-emerald-200 opacity-100' : 'opacity-0 group-hover:opacity-40 text-slate-500'
                        }`} 
                      />
                    )}

                    {/* Floating Tooltip when Collapsed */}
                    {isCollapsed && (
                      <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-950 text-white text-xs font-semibold rounded-lg shadow-xl border border-slate-700 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50 whitespace-nowrap">
                        {item.label}
                      </div>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Section & Logout Action */}
      <div className={`${isCollapsed ? 'p-2.5' : 'p-4'} border-t border-slate-800/80 space-y-3 bg-slate-950/60`}>
        {!isCollapsed && (
          <div className="px-2 flex items-center justify-between text-xs font-medium text-slate-400">
            <span>Portal Session</span>
            <span className="text-[11px] font-bold text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-800/60">
              Encrypted
            </span>
          </div>
        )}

        <button
          onClick={handleLogout}
          title={isCollapsed ? "Sign Out of Portal" : undefined}
          className={`w-full flex items-center ${
            isCollapsed ? 'justify-center p-3' : 'justify-center gap-2.5 px-4 py-3'
          } rounded-xl text-sm font-bold text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 border border-slate-800 hover:border-rose-900/60 transition cursor-pointer group relative`}
        >
          <LogOut size={18} className="shrink-0" />
          {!isCollapsed && <span>Sign Out of Portal</span>}

          {isCollapsed && (
            <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-950 text-rose-300 text-xs font-semibold rounded-lg shadow-xl border border-slate-700 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50 whitespace-nowrap">
              Sign Out
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
