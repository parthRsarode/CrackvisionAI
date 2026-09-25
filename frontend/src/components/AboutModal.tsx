import React from 'react';
import { X, ShieldCheck, Scale, Award, ExternalLink } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="glass-panel w-full max-w-2xl rounded-2xl p-6 sm:p-8 relative border border-white/10 shadow-2xl max-h-[90vh] overflow-y-auto"
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
            Academic & Industry Reference
          </span>
          <h2 className="text-2xl font-bold text-text mt-3">About CrackVision AI</h2>
          <p className="text-muted text-sm mt-1">
            Autonomous Structural Defect Classification & Assessment System
          </p>
        </div>

        <div className="space-y-4 text-sm text-muted/90 mb-6 leading-relaxed">
          <p>
            <strong className="text-text">CrackVision AI</strong> is designed for civil and structural engineers, building inspectors, and asset managers to drastically accelerate preliminary damage reconnaissance for bridges, roadways, retaining walls, and commercial infrastructure.
          </p>
          <p>
            The vision pipeline bridges raw computer vision segmentation models (such as YOLOv8-Seg) with real-world civil engineering codifications, including:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs">
            <li><strong className="text-text">ACI 224R-01:</strong> Control of Cracking in Concrete Structures (Permissible width thresholds between 0.1 mm to 0.4 mm).</li>
            <li><strong className="text-text">ASTM C823:</strong> Standard Practice for Examination and Sampling of Hardened Concrete in Constructions.</li>
            <li><strong className="text-text">FHWA Bridge Inspector's Reference Manual:</strong> Severity categorization for longitudinal, shear, and settlement distress.</li>
          </ul>
        </div>

        <div className="border-t border-white/10 pt-4 flex items-center justify-between text-xs text-muted">
          <span>CrackVision AI &copy; {new Date().getFullYear()}</span>
          <button
            onClick={onClose}
            className="bg-accent/20 hover:bg-accent/30 text-accent font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AboutModal;
