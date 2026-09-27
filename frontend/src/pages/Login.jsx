import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, Lock, User, AlertCircle, Loader2, KeyRound } from 'lucide-react';
import { authService } from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authService.login(username, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        "Authentication failed. Please verify credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl overflow-hidden border border-slate-200">
        
        {/* Portal Banner Header */}
        <div className="bg-slate-950 p-8 text-center border-b border-slate-800 flex items-center justify-center">
          <img 
            src="/landsure-logo-dark.png" 
            alt="LandSure Cadastral Intelligence" 
            className="w-56 max-w-full h-auto object-contain" 
          />
        </div>

        <div className="p-8">
          <h2 className="text-lg font-bold text-slate-800 mb-6 text-center">
            Officer Authentication Secure Sign-In
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Input */}
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase mb-2">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                  <User size={16} />
                </span>
                <input
                  type="text"
                  required
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-800 text-sm"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase mb-2">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                  <Lock size={16} />
                </span>
                <input
                  type="password"
                  required
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-800 text-sm"
                />
              </div>
            </div>

            {/* Error Notification */}
            {error && (
              <div className="flex items-center gap-2 text-rose-700 bg-rose-50 border border-rose-200 p-3 rounded-lg text-xs font-semibold">
                <AlertCircle size={16} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-amber-500 hover:bg-slate-950 font-bold py-3 rounded-lg text-sm transition-all shadow flex items-center justify-center gap-2 border border-slate-800 hover:border-amber-500 mt-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <span>Sign In to Portal</span>
              )}
            </button>
          </form>

          {/* Public Access Credentials Box */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-700">
              <div className="flex items-center justify-between mb-2.5">
                <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                  <KeyRound size={14} className="text-amber-600" />
                  Authorized Access Credentials
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                  Ready to Use
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">Username</div>
                  <div className="font-mono font-bold text-slate-900 select-all">revenue_officer</div>
                </div>
                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">Password</div>
                  <div className="font-mono font-bold text-slate-900 select-all">sih2026password</div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  setUsername("revenue_officer");
                  setPassword("sih2026password");
                }}
                className="mt-2.5 w-full py-2 px-3 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <span>Auto-fill Credentials</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
