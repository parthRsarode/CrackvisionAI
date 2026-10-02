import React, { useState } from 'react';
import { 
  BatchAnalysisSummary, 
  AnalysisResult 
} from '../types/analysis';
import SeverityBadge from './SeverityBadge';
import { 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  Download, 
  ExternalLink, 
  RefreshCw, 
  Ruler, 
  FileSpreadsheet, 
  Building2, 
  ShieldAlert,
  ArrowRight,
  FileCheck
} from 'lucide-react';
import { exportDirectPDF } from '../services/api';

interface BatchAnalysisViewProps {
  summary: BatchAnalysisSummary;
  results: AnalysisResult[];
  thumbnails: string[];
  onSelectResult: (result: AnalysisResult, thumbnail: string) => void;
  onReset: () => void;
}

const BatchAnalysisView: React.FC<BatchAnalysisViewProps> = ({
  summary,
  results,
  thumbnails,
  onSelectResult,
  onReset
}) => {
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleDownloadPDF = async (item: AnalysisResult) => {
    setDownloadingId(item.analysis_id);
    try {
      await exportDirectPDF(item);
    } catch (err: any) {
      alert(`PDF download failed: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleExportBatchCsv = () => {
    if (results.length === 0) return;
    const headers = [
      'Survey_ID', 
      'Distress_Type', 
      'Severity', 
      'Estimated_Width', 
      'Surface_Area', 
      'Defect_Count',
      'Confidence_Pct', 
      'Standard_Code',
      'Timestamp'
    ];
    const rows = results.map((item) => [
      item.analysis_id,
      `"${item.crack_type}"`,
      item.severity,
      `"${item.estimated_width}"`,
      `"${item.affected_area}"`,
      item.defect_count ?? 1,
      item.confidence.toFixed(1),
      item.compliance_details?.standard_code || 'ACI',
      item.created_at,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `batch_inspection_survey_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Batch Overview Header Card */}
      <div className="cad-panel rounded-xl p-6 sm:p-8 border-2 border-slate-400 bg-white shadow-md">
        
        {/* Title & Metadata */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-5 border-b-2 border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="bg-slate-900 text-amber-400 font-mono text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1.5">
                <Layers className="h-3 w-3 text-safetyOrange" />
                MULTI-IMAGE BATCH SURVEY
              </span>
              <span className="text-xs font-mono text-slate-600">
                {summary.total_images} Inspection Image{summary.total_images !== 1 ? 's' : ''} Processed
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight font-sans uppercase">
              Aggregated Structural Condition Survey
            </h2>
            <p className="text-xs text-slate-600 font-sans">
              Autonomous Multi-Element Visual Damage Audit • AI Segmentation & Standard Compliance
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleExportBatchCsv}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-900 text-xs font-mono font-bold rounded border border-slate-300 transition-colors cursor-pointer"
              title="Export all batch records to CSV"
            >
              <FileSpreadsheet className="h-4 w-4 text-safetyOrange" />
              <span>Export Batch CSV</span>
            </button>
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-2 bg-safetyOrange hover:bg-orange-600 text-white text-xs font-mono font-bold rounded transition-colors cursor-pointer"
            >
              <RefreshCw className="h-4 w-4" />
              <span>New Inspection</span>
            </button>
          </div>
        </div>

        {/* Aggregated KPI Cards (REQ-4.4) */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mt-6">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-300">
            <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
              SURFACES SCANNED
            </span>
            <div className="text-2xl font-black text-slate-900 font-mono">
              {summary.total_images}
            </div>
            <span className="text-[11px] text-slate-600 font-sans">
              {summary.defects_detected_count} with detected distress
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-300">
            <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
              MAX APERTURE
            </span>
            <div className="text-2xl font-black text-slate-900 font-mono">
              {summary.max_width_mm.toFixed(2)} <span className="text-xs font-normal">mm</span>
            </div>
            <span className={`text-[11px] font-bold ${summary.max_width_mm >= 0.41 ? 'text-rose-600' : 'text-emerald-700'}`}>
              {summary.max_width_mm >= 0.41 ? 'Exceeds ACI Service Limit' : 'Within Tolerable Limits'}
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-300">
            <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
              TOTAL CRACK EXTENT
            </span>
            <div className="text-2xl font-black text-slate-900 font-mono">
              {summary.total_crack_length_mm >= 1000 
                ? `${(summary.total_crack_length_mm / 1000).toFixed(2)} m`
                : `${summary.total_crack_length_mm.toFixed(0)} mm`}
            </div>
            <span className="text-[11px] text-slate-600 font-sans">
              Cumulative fissure length
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-300">
            <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
              CRITICAL ELEMENTS
            </span>
            <div className={`text-2xl font-black font-mono ${summary.critical_elements_flagged.length > 0 ? 'text-rose-600' : 'text-slate-900'}`}>
              {summary.critical_elements_flagged.length}
            </div>
            <span className="text-[11px] text-slate-600 font-sans">
              High priority review
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-300 col-span-2 lg:col-span-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
              SEVERITY SPREAD
            </span>
            <div className="flex items-center gap-1.5 mt-1 font-mono text-xs">
              <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 font-bold" title="High / Critical">
                {summary.critical_count} High
              </span>
              <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-bold" title="Medium">
                {summary.moderate_count} Med
              </span>
              <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold" title="Low">
                {summary.minor_count} Low
              </span>
            </div>
          </div>
        </div>

        {/* Critical Elements Alert Callout */}
        {summary.critical_elements_flagged.length > 0 && (
          <div className="mt-5 p-3.5 bg-rose-50 border border-rose-300 rounded-lg text-rose-900 text-xs flex items-start gap-3">
            <ShieldAlert className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-bold block uppercase font-mono tracking-tight text-rose-800">
                Structural Priority Alert: Elements Require Immediate PE Site Review
              </strong>
              <p className="mt-0.5 text-rose-700">
                The following inspection images exhibit critical crack widths (≥ 0.40mm) or distress proximate to structural connections:
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {summary.critical_elements_flagged.map((item, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-rose-200 text-rose-900 font-mono font-bold rounded text-[11px]">
                    ⚠️ {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Grid of Inspected Elements */}
      <div className="cad-panel rounded-xl p-6 sm:p-8 border border-slate-300 bg-white shadow-sm">
        <div className="flex items-center justify-between gap-2 mb-4 pb-2 border-b border-slate-200">
          <div>
            <h3 className="text-base font-bold text-slate-900 font-sans uppercase">
              Survey Member Catalog ({results.length} Elements)
            </h3>
            <p className="text-xs text-slate-500 font-mono">
              Click any element card to view in full interactive CAD/SCAR orthomosaic or download the formal PDF report.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((res, index) => {
            const thumb = thumbnails[index] || '';
            const isCritical = res.severity === 'high';

            return (
              <div
                key={res.analysis_id || index}
                className={`flex flex-col justify-between border rounded-lg overflow-hidden bg-slate-50 hover:bg-white transition-all shadow-xs group ${
                  isCritical ? 'border-rose-300 hover:border-rose-500' : 'border-slate-300 hover:border-safetyOrange'
                }`}
              >
                <div>
                  {/* Thumbnail Banner */}
                  <div className="relative aspect-video bg-slate-950 overflow-hidden border-b border-slate-200 cursor-pointer"
                    onClick={() => onSelectResult(res, thumb)}
                  >
                    {thumb ? (
                      <img 
                        src={thumb} 
                        alt="Inspection surface" 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-500 font-mono text-xs">
                        SURVEY IMAGE
                      </div>
                    )}
                    <div className="absolute top-2 left-2 z-10">
                      <SeverityBadge severity={res.severity} />
                    </div>
                    <div className="absolute bottom-2 right-2 z-10 bg-slate-900/80 text-white font-mono text-[10px] px-2 py-0.5 rounded">
                      ID: {res.analysis_id}
                    </div>
                  </div>

                  {/* Body Info */}
                  <div className="p-4">
                    <h4 className="font-bold text-sm text-slate-900 font-sans truncate mb-1">
                      {res.crack_type}
                    </h4>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-700 my-2.5">
                      <div className="bg-white p-2 rounded border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">APERTURE</span>
                        <strong>{res.estimated_width}</strong>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">EXTENT</span>
                        <strong>{res.affected_area}</strong>
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-600 font-sans line-clamp-2">
                      {res.recommendation}
                    </p>
                  </div>
                </div>

                {/* Card Actions */}
                <div className="p-3 bg-slate-100 border-t border-slate-200 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleDownloadPDF(res)}
                    disabled={downloadingId === res.analysis_id}
                    className="flex items-center gap-1 text-xs font-mono font-bold text-slate-700 hover:text-slate-950 p-1.5 rounded hover:bg-slate-200 transition-colors cursor-pointer"
                    title="Download individual SCAR PDF"
                  >
                    <Download className="h-3.5 w-3.5 text-safetyOrange" />
                    <span>{downloadingId === res.analysis_id ? 'PDF...' : 'PDF'}</span>
                  </button>

                  <button
                    onClick={() => onSelectResult(res, thumb)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-civilNavy hover:bg-slate-800 text-white text-xs font-mono font-bold rounded transition-colors cursor-pointer ml-auto"
                  >
                    <span>Inspect CAD</span>
                    <ArrowRight className="h-3.5 w-3.5 text-safetyOrange" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default BatchAnalysisView;
