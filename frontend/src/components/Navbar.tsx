import { useState, useEffect } from 'react';
import { Building2, ShieldAlert, BookOpen, HardHat, FileSpreadsheet, Activity } from 'lucide-react';
import { healthCheck } from '../services/api';

interface NavbarProps {
  onOpenHowItWorks: () => void;
  onOpenAbout: () => void;
  onHomeClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onOpenHowItWorks, onOpenAbout, onHomeClick }) => {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    const checkServer = async () => {
      try {
        await healthCheck();
        if (isMounted) setBackendOnline(true);
      } catch {
        if (isMounted) setBackendOnline(false);
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="bg-civilNavy text-white border-b-4 border-safetyOrange shadow-md sticky top-0 z-40">
      {/* Top Engineering Banner Bar */}
      <div className="bg-civilDark/90 border-b border-slate-700/60 px-4 sm:px-8 py-1.5 text-[11px] text-slate-300 font-mono flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 font-semibold text-safetyOrange">
            <HardHat className="h-3.5 w-3.5" />
            <span>DOT & STRUCTURAL HEALTH INSPECTION TERMINAL</span>
          </span>
          <span className="hidden md:inline text-slate-600">|</span>
          <span className="hidden md:inline text-slate-400">Spec: ACI 224R-01 / ASTM C823 / FHWA-BIRM</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className={`inline-block w-2 h-2 rounded-full ${
              backendOnline === true ? 'bg-emerald-400 animate-pulse' : backendOnline === false ? 'bg-rose-500' : 'bg-amber-400'
            }`} />
            <span>{backendOnline === true ? 'Vision Engine Online' : 'Engine Disconnected'}</span>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3 flex items-center justify-between">
        {/* Brand */}
        <button 
          onClick={onHomeClick}
          className="flex items-center space-x-3.5 group text-left focus:outline-none"
        >
          <div className="w-10 h-10 rounded-lg bg-safetyOrange flex items-center justify-center text-slate-950 shadow-md">
            <Building2 className="h-6 w-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-black tracking-tight text-white uppercase font-sans">
                CrackVision <span className="text-safetyOrange font-bold">CIVIL</span>
              </span>
              <span className="text-[10px] font-mono font-bold bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                ACI-224R
              </span>
            </div>
            <p className="text-[11px] text-slate-300 tracking-wide font-sans">
              Concrete Infrastructure Defect & Aperture Analysis
            </p>
          </div>
        </button>

        {/* Practical Civil Field Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={onOpenHowItWorks}
            className="flex items-center space-x-1.5 text-xs sm:text-sm font-semibold text-slate-200 hover:text-white px-3 py-1.5 rounded-md hover:bg-slate-800 transition-colors border border-transparent hover:border-slate-700"
          >
            <BookOpen className="h-4 w-4 text-safetyOrange" />
            <span className="hidden sm:inline">Field Manual</span>
          </button>

          <button
            onClick={onOpenAbout}
            className="flex items-center space-x-1.5 text-xs sm:text-sm font-semibold text-slate-200 hover:text-white px-3 py-1.5 rounded-md hover:bg-slate-800 transition-colors border border-transparent hover:border-slate-700"
          >
            <FileSpreadsheet className="h-4 w-4 text-safetyOrange" />
            <span className="hidden sm:inline">ACI Criteria</span>
          </button>

          <button
            onClick={onHomeClick}
            className="bg-safetyOrange hover:bg-orange-600 text-white font-bold text-xs sm:text-sm px-4 py-1.5 rounded-md shadow-sm transition-colors"
          >
            + New Inspection
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
