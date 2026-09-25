import React from 'react';
import { X, Camera, Cpu, FileCheck2, ArrowRight } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HowItWorksModal: React.FC<HowItWorksModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const steps = [
    {
      step: '01',
      title: 'High-Res Surface Acquisition',
      desc: 'Upload standard digital photographs of concrete slabs, beams, bridge piers, or asphalt pavements. The engine supports JPEG, PNG, and WEBP formats.',
      icon: Camera,
      badge: 'Input Phase',
    },
    {
      step: '02',
      title: 'Neural Crack Segmentation',
      desc: 'The YOLOv8 / DeepLabV3+ segmentation architecture identifies hairline fissures, shear cracks, and spalling, separating true structural defects from shadows and stains.',
      icon: Cpu,
      badge: 'Inference Phase',
    },
    {
      step: '03',
      title: 'Quantification & Engineering Action',
      desc: 'Pixel-to-metric calibration measures crack aperture width and affected area, cross-referencing ACI 224R standards to deliver actionable civil maintenance steps.',
      icon: FileCheck2,
      badge: 'Decision Support',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="glass-panel w-full max-w-3xl rounded-2xl p-6 sm:p-8 relative border border-white/10 shadow-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-muted hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="mb-6">
          <span className="text-xs uppercase font-bold tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full">
            Engineering Methodology
          </span>
          <h2 className="text-2xl font-bold text-text mt-3">How CrackVision AI Works</h2>
          <p className="text-muted text-sm mt-1">
            End-to-end automated pipeline for computer vision-assisted civil structural health monitoring.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div 
                key={s.step} 
                className="bg-card/70 border border-white/5 rounded-xl p-5 flex flex-col justify-between hover:border-accent/40 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-mono font-bold text-accent/80">{s.step}</span>
                    <span className="text-[10px] text-muted/70 bg-white/5 px-2 py-0.5 rounded">{s.badge}</span>
                  </div>
                  <div className="p-3 bg-accent/10 rounded-lg w-fit text-accent mb-4">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-semibold text-text text-base mb-2">{s.title}</h3>
                  <p className="text-muted text-xs leading-relaxed">{s.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="bg-accent/5 border border-accent/20 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-sm text-muted">
            <strong className="text-text">Ready to run an inspection?</strong> Use a sample image or upload your own concrete photo.
          </div>
          <button
            onClick={onClose}
            className="bg-accent hover:bg-accentHover text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
          >
            Start Analyzing
          </button>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksModal;
