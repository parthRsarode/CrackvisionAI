import React from 'react';
import { Ruler, ShieldCheck, Info } from 'lucide-react';

interface CrackComparatorCardProps {
  onClose?: () => void;
  detectedWidth?: string;
  standardCode?: string;
  standardName?: string;
}

const CrackComparatorCard: React.FC<CrackComparatorCardProps> = ({
  onClose,
  detectedWidth,
  standardCode = 'ACI',
  standardName
}) => {
  const codeKey = standardCode.toUpperCase();

  const getStandardInfo = () => {
    switch (codeKey) {
      case 'EUROCODE_2':
        return {
          title: 'Eurocode 2 EN 1992 Comparator',
          ref: 'EN 1992-1-1 / EN 1992-3',
          graduations: [
            { mm: 0.10, stroke: 1.0, note: 'EN 1992-3 Liquid retaining max' },
            { mm: 0.15, stroke: 1.5, note: 'Tight durability threshold' },
            { mm: 0.20, stroke: 2.0, note: 'XD/XS Severe exposure limit' },
            { mm: 0.30, stroke: 3.0, note: 'XC2-XC4 Moist/Soil limit' },
            { mm: 0.40, stroke: 4.0, note: 'XC1 Dry indoor limit' },
            { mm: 0.50, stroke: 5.0, note: 'SLS Serviceability exceeded' },
            { mm: 0.75, stroke: 7.0, note: 'Active routing & injection' },
            { mm: 1.00, stroke: 9.0, note: 'Major structural distress' },
            { mm: 1.50, stroke: 12.0, note: 'Severe separation' },
          ]
        };
      case 'IS_456':
        return {
          title: 'IS 456:2000 Crack Comparator',
          ref: 'IS 456:2000 Cl. 35.3.2',
          graduations: [
            { mm: 0.10, stroke: 1.0, note: 'Liquid-retaining max (IS 456)' },
            { mm: 0.15, stroke: 1.5, note: 'Coastal/Marine spray limit' },
            { mm: 0.20, stroke: 2.0, note: 'Severe / Coastal limit' },
            { mm: 0.30, stroke: 3.0, note: 'Normal / Mild exposure limit' },
            { mm: 0.40, stroke: 4.0, note: 'Service limit exceeded' },
            { mm: 0.50, stroke: 5.0, note: 'Structural repair required' },
            { mm: 0.75, stroke: 7.0, note: 'Pressure epoxy injection' },
            { mm: 1.00, stroke: 9.0, note: 'Major structural crack' },
            { mm: 1.50, stroke: 12.0, note: 'Severe distress' },
          ]
        };
      case 'BS_8110':
        return {
          title: 'BS 8110 / BS 8500 Comparator',
          ref: 'BS 8110 / BS 8500 (UK)',
          graduations: [
            { mm: 0.10, stroke: 1.0, note: 'Water tight structure limit' },
            { mm: 0.15, stroke: 1.5, note: 'Aggressive soil limit' },
            { mm: 0.20, stroke: 2.0, note: 'Severe marine exposure limit' },
            { mm: 0.30, stroke: 3.0, note: 'Standard RC crack limit' },
            { mm: 0.40, stroke: 4.0, note: 'Durability limit exceeded' },
            { mm: 0.50, stroke: 5.0, note: 'Structural repair required' },
            { mm: 0.75, stroke: 7.0, note: 'Epoxy pressure sealing' },
            { mm: 1.00, stroke: 9.0, note: 'Major crack distress' },
            { mm: 1.50, stroke: 12.0, note: 'Severe structural separation' },
          ]
        };
      case 'ACI':
      default:
        return {
          title: 'ACI 224R / CODE-562 Comparator',
          ref: 'ASTM C823 / ACI 224R-01',
          graduations: [
            { mm: 0.10, stroke: 1.0, note: 'Water-retaining max' },
            { mm: 0.15, stroke: 1.5, note: 'Seawater spray max' },
            { mm: 0.20, stroke: 2.0, note: 'Deicing chemical limit' },
            { mm: 0.30, stroke: 3.0, note: 'Humid/soil exposure limit' },
            { mm: 0.40, stroke: 4.0, note: 'Dry air/indoor limit' },
            { mm: 0.50, stroke: 5.0, note: 'Structural repair required' },
            { mm: 0.75, stroke: 7.0, note: 'Active routing & injection' },
            { mm: 1.00, stroke: 9.0, note: 'Major distress' },
            { mm: 1.50, stroke: 12.0, note: 'Severe structural separation' },
          ]
        };
    }
  };

  const cardData = getStandardInfo();

  return (
    <div className="bg-amber-50/95 border-2 border-slate-700 rounded-xl p-4 shadow-xl text-slate-900 max-w-sm w-full font-mono text-xs select-none backdrop-blur-md">
      {/* Card Header resembling physical transparent optical card */}
      <div className="flex items-center justify-between pb-2 mb-3 border-b-2 border-slate-800">
        <div>
          <div className="flex items-center gap-1.5 font-bold tracking-tight text-slate-950 uppercase text-[11px]">
            <Ruler className="h-4 w-4 text-safetyOrange" />
            <span>{cardData.title}</span>
          </div>
          <p className="text-[9px] text-slate-600 font-sans">
            Calibrated Optical Scale • Precision Metric (mm)
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-950 p-1 text-sm font-bold cursor-pointer"
          >
            ✕
          </button>
        )}
      </div>

      {detectedWidth && (
        <div className="mb-3 px-2 py-1.5 bg-safetyOrange/10 border border-safetyOrange/40 rounded text-safetyOrange font-bold text-[11px] flex items-center justify-between">
          <span>AI Estimated Aperture:</span>
          <span className="bg-white px-2 py-0.5 rounded shadow-sm border border-safetyOrange/30 text-slate-950 font-mono">
            {detectedWidth}
          </span>
        </div>
      )}

      {/* Optical Gauge Scale Table */}
      <div className="space-y-2 py-1">
        {cardData.graduations.map((g) => (
          <div key={g.mm} className="flex items-center justify-between gap-3 text-[10px]">
            <span className="font-bold text-slate-950 w-12">{g.mm.toFixed(2)} mm</span>
            
            {/* Visual Calibrated Line */}
            <div className="flex-1 flex items-center">
              <div 
                className="bg-slate-950 rounded-full w-full"
                style={{ height: `${g.stroke}px` }} 
              />
            </div>

            <span className="text-[9px] text-slate-600 w-36 text-right truncate font-sans">
              {g.note}
            </span>
          </div>
        ))}
      </div>

      {/* Card Footer */}
      <div className="mt-3 pt-2 border-t border-slate-300 text-[9px] text-slate-600 flex items-center justify-between font-sans">
        <span>Standard Ref: {cardData.ref}</span>
        <span className="font-bold text-slate-800">Class A Standard</span>
      </div>
    </div>
  );
};

export default CrackComparatorCard;
