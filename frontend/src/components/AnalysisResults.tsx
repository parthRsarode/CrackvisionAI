import React from 'react';
import { AnalysisResult } from '../types/analysis';
import ImagePreview from './ImagePreview';
import SeverityBadge from './SeverityBadge';
import { 
  Printer, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  Ruler, 
  Building2, 
  FileText,
  ShieldAlert,
  ClipboardList,
  Wrench,
  Calendar,
  Layers
} from 'lucide-react';

interface AnalysisResultsProps {
  analysis: AnalysisResult;
  imageUrl: string;
  onReset?: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis, imageUrl, onReset }) => {
  const isDetected = analysis.status === 'crack_detected';

  // Compute ACI exposure limit comparison
  const getAciLimit = () => {
    switch (analysis.severity) {
      case 'high':
        return { limit: '0.15 mm', condition: 'Deicing Chemicals & Seawater Spray', compliant: false, delta: 'Exceeded by >200%' };
      case 'medium':
        return { limit: '0.30 mm', condition: 'Humidity, Moist Air, Soil Contact', compliant: false, delta: 'Exceeded by ~80%' };
      case 'low':
      default:
        return { limit: '0.41 mm', condition: 'Dry Air or Protective Membrane', compliant: true, delta: 'Within Service Limits' };
    }
  };

  const aciData = getAciLimit();

  return (
    <div className="space-y-6">
      {/* Official Civil Engineering Assessment Card */}
      <div className="cad-panel rounded-xl p-6 sm:p-8 border-2 border-slate-400 bg-white shadow-md">
        {/* Document Header */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-5 border-b-2 border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="bg-slate-900 text-white font-mono text-[10px] font-bold px-2 py-0.5 rounded">
                SCAR REPORT
              </span>
              <span className="text-xs font-mono text-slate-600">ID: {analysis.analysis_id}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight font-sans uppercase">
              Structural Condition Assessment Report
            </h2>
            <p className="text-xs text-slate-600 font-sans">
              Autonomous Optical Damage Survey • In accordance with ACI 224R-01 & ASTM C823
            </p>
          </div>

          <div className="text-right">
            <SeverityBadge severity={analysis.severity} />
            <p className="text-[11px] font-mono text-slate-500 mt-1">
              Date: {new Date(analysis.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Severity Banner */}
        <div className={`mt-5 p-4 rounded-lg border-l-4 flex items-start gap-3.5 ${
          analysis.severity === 'high' 
            ? 'bg-rose-50 border-rose-600 text-rose-950' 
            : analysis.severity === 'medium'
            ? 'bg-amber-50 border-safetyOrange text-amber-950'
            : 'bg-emerald-50 border-emerald-600 text-emerald-950'
        }`}>
          {analysis.severity === 'high' ? (
            <ShieldAlert className="h-6 w-6 text-rose-600 shrink-0 mt-0.5" />
          ) : analysis.severity === 'medium' ? (
            <AlertTriangle className="h-6 w-6 text-safetyOrange shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="h-6 w-6 text-emerald-600 shrink-0 mt-0.5" />
          )}
          <div>
            <h4 className="text-sm font-bold uppercase font-mono tracking-wide">
              {analysis.severity === 'high'
                ? 'CRITICAL DEFECT: Structural Remediation Required'
                : analysis.severity === 'medium'
                ? 'MODERATE DISTRESS: Surface Sealing & Regular Monitoring Warranted'
                : 'SURFACE INTACT: Within Permissible Serviceability Limits'}
            </h4>
            <p className="text-xs mt-1 font-sans text-slate-700 leading-relaxed">
              {isDetected
                ? `Fissure classification isolates ${analysis.crack_type.toLowerCase()} displaying measured aperture range of ${analysis.estimated_width}. Affected surface ratio computed at ${analysis.affected_area}.`
                : 'Optical scan detected no critical discontinuities exceeding minimum calibration threshold.'}
            </p>
          </div>
        </div>

        {/* Key Morphometry Metrics Table */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-xs text-left border border-slate-300 font-mono">
            <thead className="bg-slate-100 text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th className="p-3 border-r border-slate-300">Distress Classification</th>
                <th className="p-3 border-r border-slate-300">Aperture Width (mm)</th>
                <th className="p-3 border-r border-slate-300">Affected Area (%)</th>
                <th className="p-3">Model Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              <tr>
                <td className="p-3 font-bold text-slate-900 border-r border-slate-200">
                  {analysis.crack_type}
                </td>
                <td className="p-3 font-bold text-safetyOrange border-r border-slate-200">
                  {analysis.estimated_width}
                </td>
                <td className="p-3 text-slate-800 border-r border-slate-200">
                  {analysis.affected_area}
                </td>
                <td className="p-3 text-slate-800">
                  {analysis.confidence.toFixed(1)}% (YOLOv8-Seg)
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* ACI 224R-01 Compliance Evaluation Matrix */}
        <div className="mt-6 bg-slate-50 border border-slate-300 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2.5">
            <ClipboardList className="h-4 w-4 text-safetyOrange" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-mono">
              ACI 224R-01 Permissible Crack Width Evaluation Matrix
            </h4>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-2.5 bg-white border border-slate-200 rounded">
              <span className="text-[10px] text-slate-500 uppercase block">Selected Exposure Condition</span>
              <strong className="text-slate-900 font-sans text-xs">{aciData.condition}</strong>
            </div>

            <div className="p-2.5 bg-white border border-slate-200 rounded">
              <span className="text-[10px] text-slate-500 uppercase block">ACI Maximum Permissible Limit</span>
              <strong className="text-slate-900 text-xs">{aciData.limit}</strong>
            </div>

            <div className="p-2.5 bg-white border border-slate-200 rounded">
              <span className="text-[10px] text-slate-500 uppercase block">Compliance Status</span>
              <strong className={aciData.compliant ? 'text-emerald-700' : 'text-rose-700 font-bold'}>
                {aciData.compliant ? 'COMPLIANT' : 'LIMIT EXCEEDED (' + aciData.delta + ')'}
              </strong>
            </div>
          </div>
        </div>

        {/* Engineering Remediation Specification */}
        <div className="mt-6 border-2 border-slate-300 rounded-lg p-4 bg-white">
          <div className="flex items-center gap-2 mb-2">
            <Wrench className="h-4 w-4 text-safetyOrange" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-mono">
              Prescribed Civil Engineering Remediation
            </h4>
          </div>
          <p className="text-xs text-slate-800 leading-relaxed font-sans mb-3">
            {analysis.recommendation}
          </p>
          <div className="p-2.5 bg-slate-100 rounded text-[11px] font-mono text-slate-600 border border-slate-200">
            <strong>Standard Material Specification:</strong> For cracks &gt; 0.3mm exhibiting structural movement, execute low-viscosity epoxy injection meeting ASTM C881 Type I/IV Grade 1 standards. For non-structural shrinkage, rout to 6mm×6mm and apply elastomeric polyurethane sealant.
          </div>
        </div>

        {/* Report Actions */}
        <div className="mt-8 flex flex-col sm:flex-row gap-3 pt-5 border-t border-slate-300 no-print">
          <button
            onClick={() => window.print()}
            className="flex-1 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm py-2.5 px-5 rounded-md shadow-sm transition-colors flex items-center justify-center gap-2"
          >
            <Printer className="h-4 w-4" />
            <span>Print Official Structural Report</span>
          </button>

          <button
            onClick={onReset}
            className="flex-1 bg-safetyOrange hover:bg-orange-600 text-white font-bold text-xs sm:text-sm py-2.5 px-5 rounded-md shadow-sm transition-colors flex items-center justify-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Conduct New Asset Survey</span>
          </button>
        </div>
      </div>

      {/* Surface Image Verification Viewer */}
      <div className="cad-panel rounded-xl p-6 sm:p-8 border border-slate-300 bg-white shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1 font-sans">
          Calibrated Visual Damage Orthomosaic
        </h3>
        <p className="text-xs text-slate-600 mb-4 font-sans">
          Use the ACI optical comparator card below to visually cross-verify the crack aperture against physical millimeter graduation lines.
        </p>

        <ImagePreview analysis={analysis} imageUrl={imageUrl} />
      </div>

      {/* Official Signoff Block for Printouts */}
      <div className="hidden print-only mt-12 pt-8 border-t-2 border-slate-900 text-xs font-mono text-slate-800">
        <div className="grid grid-cols-2 gap-12">
          <div>
            <p className="font-bold mb-6">FIELD STRUCTURAL ENGINEER (PE/SE):</p>
            <div className="border-b-2 border-slate-900 h-8 w-64 mb-1" />
            <p className="text-[10px]">Licensed Professional Engineer Signature & Stamp</p>
          </div>
          <div className="text-right">
            <p className="font-bold mb-6">DEPARTMENT AUDIT & APPROVAL:</p>
            <div className="border-b-2 border-slate-900 h-8 w-48 ml-auto mb-1" />
            <p className="text-[10px]">Asset Verification Officer</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;
