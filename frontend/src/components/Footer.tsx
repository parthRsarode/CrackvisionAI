import React from 'react';
import { HardHat, ShieldCheck, Building2 } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-civilDark text-slate-400 border-t-4 border-safetyOrange mt-16 py-8 text-xs font-mono">
      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 text-white font-bold text-sm font-sans mb-2">
              <Building2 className="h-4 w-4 text-safetyOrange" />
              <span>CrackVision Civil Engineering System</span>
            </div>
            <p className="text-slate-400 text-xs font-sans leading-relaxed">
              Standardized Computer Vision & Quantitative Morphometry for Concrete Infrastructure & Bridge Asset Management.
            </p>
          </div>

          <div>
            <span className="text-slate-200 font-bold uppercase block mb-2 font-mono text-[11px]">
              Governing Technical Standards
            </span>
            <ul className="space-y-1 text-[11px] text-slate-400 font-sans">
              <li>• ACI 224R-01: Control of Cracking in Concrete Structures</li>
              <li>• ASTM C823: Standard Practice for Concrete Examination</li>
              <li>• AASHTO Manual for Bridge Evaluation (MBE, 3rd Ed.)</li>
              <li>• FHWA Bridge Inspector's Reference Manual (BIRM)</li>
            </ul>
          </div>

          <div>
            <span className="text-slate-200 font-bold uppercase block mb-2 font-mono text-[11px]">
              Inspection Compliance Notice
            </span>
            <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
              This terminal provides preliminary optical damage screening and aperture quantification. Final structural remediation stamping must be executed by a licensed Professional Engineer (PE / SE).
            </p>
          </div>
        </div>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500">
          <span>CrackVision Civil &copy; {new Date().getFullYear()} • Operational Structural Health Portal</span>
          <span className="mt-2 sm:mt-0 font-mono">Terminal Engine: Python FastAPI / PyTorch / React 18</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
