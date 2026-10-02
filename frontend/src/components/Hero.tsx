import React from 'react';
import { ArrowDownCircle, ShieldCheck, Ruler, ClipboardCheck, Building2, HardHat } from 'lucide-react';
import { SAMPLE_IMAGES, SampleImage } from '../data/sampleImages';

interface HeroProps {
  onUploadClick: () => void;
  onSelectSample: (sample: SampleImage) => void;
}

const Hero: React.FC<HeroProps> = ({ onUploadClick, onSelectSample }) => {
  return (
    <section className="pt-8 pb-6 border-b border-slate-300 mb-6 animate-enter stagger-1">
      {/* Field Inspection Identification Tag */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 animate-enter stagger-2">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 bg-slate-200 text-slate-800 rounded font-mono text-xs font-bold border border-slate-300">
            SURVEY TERMINAL v2.4
          </span>
          <span className="text-xs text-slate-600 font-mono">
            REF: ACI / EC2 / IS 456 / BS 8110
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200 font-medium">
          <ShieldCheck className="h-4 w-4" />
          <span>Calibrated for Structural & Civil Health Audits</span>
        </div>
      </div>

      {/* Main Title */}
      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-3 font-sans animate-enter stagger-3">
        Concrete Crack Survey & Quantitative Aperture Assessment
      </h1>

      {/* Field Scope Description */}
      <p className="text-sm sm:text-base text-slate-700 max-w-4xl mb-6 leading-relaxed animate-enter stagger-4">
        Upload high-resolution field photographs of bridge decks, substructure piers, retaining walls, or concrete pavements. 
        The system isolates micro-fractures, calculates maximum aperture width in millimeters, and cross-references 
        <strong className="text-slate-900"> selected global code exposure thresholds</strong> to prescribe civil repair specifications.
      </p>

      {/* Fast Action Buttons */}
      <div className="flex flex-wrap items-center gap-3 mb-6 animate-enter stagger-5">
        <button
          onClick={onUploadClick}
          className="bg-safetyOrange hover:bg-orange-600 text-white font-bold text-sm px-6 py-2.5 rounded-lg shadow-sm transition-colors duration-200 ease-out active:scale-[0.97] flex items-center gap-2 focus:ring-2 focus:ring-safetyOrange focus:ring-offset-2"
        >
          <ArrowDownCircle className="h-4 w-4" />
          <span>Upload Field Surface Photo</span>
        </button>
      </div>

      {/* Pre-calibrated Field Asset Samples */}
      <div className="bg-slate-100 border border-slate-300 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono flex items-center gap-1.5">
            <Ruler className="h-3.5 w-3.5 text-safetyOrange" />
            Quick Benchmark Assets (Pre-loaded Field Cases):
          </span>
          <span className="text-[11px] text-slate-500 font-sans hidden sm:inline">
            Click any asset to run automated structural evaluation
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {SAMPLE_IMAGES.map((sample, idx) => (
            <button
              key={sample.id}
              onClick={() => onSelectSample(sample)}
              className="flex items-center gap-3 p-2.5 rounded-lg bg-white hover:bg-amber-50/60 border border-slate-300 hover:border-safetyOrange text-left transition-colors duration-200 ease-out active:scale-[0.97] group shadow-sm"
            >
              <img 
                src={sample.thumbnailUrl} 
                alt={sample.title} 
                className="w-12 h-10 rounded object-cover border border-slate-300 shrink-0"
              />
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-slate-900 group-hover:text-safetyOrange transition-colors truncate">
                    {sample.title}
                  </span>
                  <span className="text-[9px] font-mono bg-slate-100 text-slate-700 px-1 rounded">
                    CASE 0{idx + 1}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 truncate">{sample.surface}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Hero;
