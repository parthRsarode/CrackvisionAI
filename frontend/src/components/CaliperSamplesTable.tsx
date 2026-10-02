import React from 'react';
import { CaliperSample } from '../types/analysis';
import { Gauge, Trash2, Download, AlertCircle, CheckCircle } from 'lucide-react';

interface CaliperSamplesTableProps {
  samples: CaliperSample[];
  standardCode: string;
  permissibleLimitMm: number;
  onDeleteSample: (id: string) => void;
  onClearAll: () => void;
}

const CaliperSamplesTable: React.FC<CaliperSamplesTableProps> = ({
  samples,
  standardCode,
  permissibleLimitMm,
  onDeleteSample,
  onClearAll,
}) => {
  if (samples.length === 0) {
    return (
      <div className="bg-slate-900/90 border border-slate-700 rounded-lg p-3 text-slate-300 text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-400">
          <Gauge className="h-4 w-4 text-safetyOrange" />
          <span>No digital caliper samples recorded yet. Click on the crack fissure to take localized aperture readings.</span>
        </div>
      </div>
    );
  }

  const widths = samples.map((s) => s.width_mm);
  const minWidth = Math.min(...widths);
  const maxWidth = Math.max(...widths);
  const avgWidth = widths.reduce((a, b) => a + b, 0) / widths.length;
  const exceedCount = samples.filter((s) => s.width_mm > permissibleLimitMm).length;

  const exportCSV = () => {
    const headers = ['Sample ID', 'Measured Width (mm)', 'Pixel Span (px)', 'Standard Limit (mm)', 'Status', 'Timestamp'];
    const rows = samples.map((s) => [
      s.id,
      s.width_mm.toFixed(3),
      s.width_px.toFixed(1),
      permissibleLimitMm.toFixed(2),
      s.width_mm > permissibleLimitMm ? 'EXCEEDS_LIMIT' : 'WITHIN_LIMIT',
      s.timestamp,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `caliper_sampling_log_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-slate-950 border border-slate-700 rounded-lg overflow-hidden text-xs font-mono shadow-md">
      {/* Header */}
      <div className="bg-slate-900 px-3 py-2 border-b border-slate-700 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-safetyOrange" />
          <span className="font-bold text-white uppercase tracking-wider">
            Digital Caliper Sampling Log ({samples.length})
          </span>
          <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[10px] border border-slate-700">
            {standardCode} Limit: {permissibleLimitMm.toFixed(2)} mm
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportCSV}
            className="flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-600 transition-colors text-[11px] font-bold cursor-pointer"
          >
            <Download className="h-3 w-3 text-safetyOrange" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={onClearAll}
            className="flex items-center gap-1 px-2 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-300 rounded border border-rose-800 transition-colors text-[11px] cursor-pointer"
          >
            <Trash2 className="h-3 w-3" />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-2.5 bg-slate-900/60 border-b border-slate-800 text-[11px]">
        <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
          <span className="text-slate-400 block text-[10px]">MIN APERTURE</span>
          <span className="text-white font-bold">{minWidth.toFixed(2)} mm</span>
        </div>
        <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
          <span className="text-slate-400 block text-[10px]">MEAN APERTURE</span>
          <span className="text-white font-bold">{avgWidth.toFixed(2)} mm</span>
        </div>
        <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
          <span className="text-slate-400 block text-[10px]">MAX APERTURE</span>
          <span className="text-safetyOrange font-bold">{maxWidth.toFixed(2)} mm</span>
        </div>
        <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
          <span className="text-slate-400 block text-[10px]">EXCEEDANCES</span>
          <span className={`font-bold ${exceedCount > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {exceedCount} / {samples.length} ({Math.round((exceedCount / samples.length) * 100)}%)
          </span>
        </div>
      </div>

      {/* Samples Table */}
      <div className="max-h-48 overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900/90 text-slate-400 text-[10px] border-b border-slate-800 uppercase">
              <th className="py-1.5 px-3">Sample ID</th>
              <th className="py-1.5 px-3">Measured Width</th>
              <th className="py-1.5 px-3">Pixel Span</th>
              <th className="py-1.5 px-3">Compliance ({standardCode})</th>
              <th className="py-1.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {samples.map((s) => {
              const exceeds = s.width_mm > permissibleLimitMm;
              return (
                <tr key={s.id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-1.5 px-3 font-bold text-amber-400">{s.id}</td>
                  <td className="py-1.5 px-3 text-white font-bold">{s.width_mm.toFixed(3)} mm</td>
                  <td className="py-1.5 px-3 text-slate-400">{s.width_px.toFixed(1)} px</td>
                  <td className="py-1.5 px-3">
                    {exceeds ? (
                      <span className="inline-flex items-center gap-1 text-rose-400 font-bold bg-rose-950/60 px-1.5 py-0.5 rounded text-[10px] border border-rose-800">
                        <AlertCircle className="h-3 w-3" />
                        EXCEEDS (+{(s.width_mm - permissibleLimitMm).toFixed(2)} mm)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-bold bg-emerald-950/60 px-1.5 py-0.5 rounded text-[10px] border border-emerald-800">
                        <CheckCircle className="h-3 w-3" />
                        PERMISSIBLE
                      </span>
                    )}
                  </td>
                  <td className="py-1.5 px-3 text-right">
                    <button
                      onClick={() => onDeleteSample(s.id)}
                      className="text-slate-500 hover:text-rose-400 p-1 rounded hover:bg-slate-800 transition-colors cursor-pointer"
                      title="Delete sample"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CaliperSamplesTable;
