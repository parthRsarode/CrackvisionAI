import { useState, useEffect } from 'react';
import { Crosshair, Ruler, CheckCircle2, ShieldCheck, HardHat } from 'lucide-react';

const AnalysisLoader: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { code: 'CALIB', title: 'Optical GSD Spatial Calibration', desc: 'Normalizing surface lighting & millimeter scale reference' },
    { code: 'MORPH', title: 'Fissure Axis Segmentation', desc: 'Isolating structural crack path from surface staining & texture' },
    { code: 'WIDTH', title: 'Aperture Metric Calculation', desc: 'Measuring peak and mean fissure width across orthogonal vectors' },
    { code: 'ACI-224', title: 'ACI 224R Structural Compliance Check', desc: 'Evaluating serviceability limits for designated exposure condition' },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 400);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="cad-panel rounded-xl p-6 sm:p-8 max-w-2xl mx-auto border-2 border-slate-400 shadow-lg bg-white font-mono">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-5 border-b border-slate-300">
        <div className="flex items-center gap-2">
          <HardHat className="h-4 w-4 text-safetyOrange" />
          <span className="text-xs font-bold text-slate-900 uppercase">
            Field Diagnostic Processor Running
          </span>
        </div>
        <span className="text-[10px] text-slate-500">
          Module: YOLOv8-Seg / ACI-224R
        </span>
      </div>

      {/* Industrial Progress Indicator */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-slate-700 font-bold mb-1.5">
          <span>Processing Step {currentStep + 1} of {steps.length}</span>
          <span>{Math.round(((currentStep + 1) / steps.length) * 100)}%</span>
        </div>
        <div className="w-full bg-slate-200 h-3 rounded overflow-hidden border border-slate-300">
          <div
            className="bg-safetyOrange h-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Technical Process Steps */}
      <div className="space-y-2.5 text-left">
        {steps.map((s, idx) => {
          const isDone = currentStep > idx;
          const isCurrent = currentStep === idx;
          return (
            <div
              key={s.code}
              className={`p-3 rounded-md border text-xs transition-colors ${
                isCurrent
                  ? 'bg-amber-50 border-safetyOrange font-semibold text-slate-900'
                  : isDone
                  ? 'bg-emerald-50/60 border-emerald-300 text-slate-700'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold flex items-center gap-1.5">
                  <span className="text-[10px] px-1 bg-slate-200 text-slate-800 rounded">
                    [{s.code}]
                  </span>
                  <span>{s.title}</span>
                </span>
                {isDone ? (
                  <span className="text-emerald-700 font-bold text-[10px] flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5" /> DONE
                  </span>
                ) : isCurrent ? (
                  <span className="text-safetyOrange font-bold text-[10px] animate-pulse">
                    PROCESSING...
                  </span>
                ) : (
                  <span className="text-slate-400 text-[10px]">QUEUED</span>
                )}
              </div>
              <p className="text-[11px] text-slate-600 font-sans pl-1">
                {s.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AnalysisLoader;
