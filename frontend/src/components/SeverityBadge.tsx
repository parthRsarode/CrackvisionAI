import React from 'react';

interface SeverityBadgeProps {
  severity: 'low' | 'medium' | 'high';
}

const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const getBadgeConfig = () => {
    switch (severity) {
      case 'high':
        return {
          classes: 'bg-rose-100 text-rose-800 border border-rose-300',
          label: 'GRADE 3: CRITICAL',
        };
      case 'medium':
        return {
          classes: 'bg-amber-100 text-amber-900 border border-amber-400',
          label: 'GRADE 2: MODERATE',
        };
      case 'low':
      default:
        return {
          classes: 'bg-emerald-100 text-emerald-800 border border-emerald-300',
          label: 'GRADE 1: MINOR',
        };
    }
  };

  const config = getBadgeConfig();

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wide ${config.classes}`}>
      {config.label}
    </span>
  );
};

export default SeverityBadge;
