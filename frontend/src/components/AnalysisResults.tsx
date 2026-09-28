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
  Layers,
  HelpCircle,
  Info,
  Shield,
  Activity,
  Check,
  Globe
} from 'lucide-react';

interface AnalysisResultsProps {
  analysis: AnalysisResult;
  imageUrl: string;
  onReset?: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis, imageUrl, onReset }) => {
  const isDetected = analysis.status === 'crack_detected';
  const metrics = analysis.multi_factor_metrics;
  const breakdown = analysis.assessment_breakdown;
  const depthStatus = analysis.crack_depth_status || 'unknown';
  const evidence = analysis.evidence_sufficiency;
  const compliance = analysis.compliance_details;

  const getAciLimit = () => {
    switch (analysis.severity) {
      case 'high':
        return { limit: '0.15 mm', condition: 'Deicing Chemicals & Seawater Spray', compliant: false, delta: 'Exceeded' };
      case 'medium':
        return { limit: '0.30 mm', condition: 'Humidity, Moist Air, Soil Contact', compliant: false, delta: 'Exceeded' };
      case 'low':
      default:
        return { limit: '0.41 mm', condition: 'Dry Air or Protective Membrane', compliant: true, delta: 'Within Limit' };
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
              Autonomous Damage Survey • Multi-Standard Engineering Guidance (ACI, Eurocode 2, IS 456, BS 8110)
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-slate-900 text-amber-400 border border-slate-700">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                {analysis.has_segmentation ? 'Ultralytics YOLOv8-Seg' : 'Simulated Pipeline'}
              </span>
              {analysis.inference_time_ms !== undefined && (
                <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                  ⚡ {analysis.inference_time_ms} ms
                </span>
              )}
              {analysis.defect_count !== undefined && (
                <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                  🎯 {analysis.defect_count} fissure contour{(analysis.defect_count !== 1) ? 's' : ''} delineated
                </span>
              )}
            </div>
          </div>

          <div className="text-right">
            <SeverityBadge severity={analysis.severity} />
            <p className="text-[11px] font-mono text-slate-500 mt-1">
              Date: {new Date(analysis.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Section 4: Evidence Sufficiency Banner */}
        {evidence && (
          <div className={`mt-5 p-3.5 rounded-lg border flex items-start gap-3 text-xs font-sans ${
            evidence.status === 'sufficient_for_surface_assessment'
              ? 'bg-emerald-50/90 border-emerald-300 text-emerald-950'
              : 'bg-amber-50/90 border-amber-300 text-amber-950'
          }`}>
            {evidence.status === 'sufficient_for_surface_assessment' ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-safetyOrange shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2 font-mono font-bold uppercase text-[11px] tracking-wider">
                <span>EVIDENCE SUFFICIENCY AUDIT:</span>
                <span className="underline">
                  {evidence.status === 'sufficient_for_surface_assessment'
                    ? 'SUFFICIENT FOR SURFACE ASSESSMENT'
                    : 'INSUFFICIENT FOR FULL ENGINEERING ASSESSMENT'}
                </span>
              </div>
              <p className="mt-1 leading-relaxed text-slate-800">{evidence.summary}</p>
              {evidence.missing_factors && evidence.missing_factors.length > 0 && (
                <p className="mt-1 text-[11px] font-mono text-slate-600">
                  Missing parameters for full structural verdict: {evidence.missing_factors.join(', ')}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Section 8: Plain-Language User Explanation */}
        {analysis.plain_language_explanation && (
          <div className="mt-4 p-4 rounded-lg bg-sky-50/80 border border-sky-200 text-sky-950">
            <div className="flex items-center gap-2 font-mono font-bold text-xs uppercase mb-1 text-sky-900">
              <Info className="h-4 w-4 text-sky-600" />
              <span>Inspection Summary for Non-Engineers (Plain Language)</span>
            </div>
            <p className="text-xs font-sans leading-relaxed text-sky-900">
              {analysis.plain_language_explanation}
            </p>
          </div>
        )}

        {/* Section 3: Crack Depth / Internal Condition Warning Card */}
        <div className="mt-5 p-4 rounded-lg bg-slate-900 text-white border border-slate-700">
          <div className="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <HelpCircle className="h-4 w-4 text-safetyOrange" />
              <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-amber-400">
                Crack Depth & Internal Condition Status
              </h4>
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 bg-slate-800 rounded text-slate-300">
              State: {depthStatus.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          <p className="text-xs font-sans leading-relaxed text-slate-300">
            {analysis.crack_depth_explanation || 
              `Measured surface crack width: ${analysis.estimated_width}. Crack depth cannot be established from surface RGB image analysis alone. Structural significance cannot be determined from surface width alone.`}
          </p>

          <div className="mt-2.5 p-2 bg-slate-800/90 rounded text-[11px] font-mono text-slate-400 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
            <span>Recommended Depth Assessment: Ultrasonic Pulse Velocity (UPV), Impact-Echo (IE), or Core Drilling.</span>
          </div>
        </div>

        {/* Section 1 & 5: Multi-Factor Morphometry & Assessment Breakdown */}
        {breakdown && (
          <div className="mt-6 bg-slate-50 border border-slate-300 rounded-lg p-4 font-sans text-xs">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-200 font-mono font-bold text-slate-900 uppercase">
              <Activity className="h-4 w-4 text-safetyOrange" />
              <h4>Multi-Factor Structural Reasoning & Context Breakdown</h4>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 mb-4">
              <div className="p-3 bg-white border border-slate-200 rounded">
                <span className="text-[10px] font-mono font-bold text-slate-500 uppercase block mb-1">
                  1. Surface Geometry Observation
                </span>
                <p className="text-slate-900 font-mono text-[11px] leading-relaxed">{breakdown.observation}</p>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded">
                <span className="text-[10px] font-mono font-bold text-slate-500 uppercase block mb-1">
                  2. Structural Context & Role
                </span>
                <p className="text-slate-900 text-[11px] leading-relaxed">{breakdown.context}</p>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded">
                <span className="text-[10px] font-mono font-bold text-slate-500 uppercase block mb-1">
                  3. Deterioration & Historical Indicators
                </span>
                <p className="text-slate-900 text-[11px] leading-relaxed">{breakdown.deterioration}</p>
              </div>

              <div className="p-3 bg-amber-50/70 border border-amber-200 rounded">
                <span className="text-[10px] font-mono font-bold text-amber-900 uppercase block mb-1">
                  4. Engineering Synthesis
                </span>
                <p className="text-amber-950 text-[11px] leading-relaxed">{breakdown.assessment}</p>
              </div>
            </div>

            {/* Metrics Matrix */}
            {metrics && (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border border-slate-300 font-mono bg-white">
                  <thead className="bg-slate-100 text-slate-700 uppercase font-bold border-b border-slate-300">
                    <tr>
                      <th className="p-2 border-r border-slate-300">Max Width</th>
                      <th className="p-2 border-r border-slate-300">Est. Length</th>
                      <th className="p-2 border-r border-slate-300">Pattern</th>
                      <th className="p-2 border-r border-slate-300">Member</th>
                      <th className="p-2 border-r border-slate-300">Spalling / Rust</th>
                      <th className="p-2">Selected Standard</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    <tr>
                      <td className="p-2 font-bold text-safetyOrange border-r border-slate-200">
                        {metrics.crack_width_mm} mm
                      </td>
                      <td className="p-2 border-r border-slate-200">
                        {metrics.crack_length_mm} mm
                      </td>
                      <td className="p-2 border-r border-slate-200">
                        {metrics.crack_pattern}
                      </td>
                      <td className="p-2 border-r border-slate-200 font-sans">
                        {metrics.member_type}
                      </td>
                      <td className="p-2 border-r border-slate-200 font-sans">
                        {metrics.visible_spalling ? 'Spalling' : 'Clean'} / {metrics.visible_corrosion ? 'Corrosion' : 'No Rust'}
                      </td>
                      <td className="p-2 font-bold text-slate-900">
                        {metrics.standard_code || 'ACI'}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Section 6 & 7: Explainable Compliance & Multi-Standard Benchmark Comparison */}
        <div className="mt-6 bg-slate-50 border border-slate-300 rounded-lg p-4">
          <div className="flex items-center justify-between gap-2 mb-3 pb-2 border-b border-slate-200 font-mono font-bold text-slate-900 uppercase">
            <div className="flex items-center gap-2">
              <ClipboardList className="h-4 w-4 text-safetyOrange" />
              <h4>Explainable Standards Compliance Matrix</h4>
            </div>
            {compliance && (
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-slate-900 text-white rounded">
                {compliance.standard_code || 'ACI'} BENCHMARK
              </span>
            )}
          </div>

          {compliance ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-2.5 bg-white border border-slate-200 rounded">
                  <span className="text-[10px] text-slate-500 uppercase block">Selected Standard</span>
                  <strong className="text-slate-900 font-sans text-xs">{compliance.standard_name}</strong>
                </div>

                <div className="p-2.5 bg-white border border-slate-200 rounded">
                  <span className="text-[10px] text-slate-500 uppercase block">Criterion Limit</span>
                  <strong className="text-slate-900 text-xs">{compliance.reference_value}</strong>
                </div>

                <div className="p-2.5 bg-white border border-slate-200 rounded">
                  <span className="text-[10px] text-slate-500 uppercase block">Compliance Status</span>
                  <strong className={`text-xs ${
                    compliance.status === 'verified' || compliance.status === 'provisionally_consistent'
                      ? 'text-emerald-700 font-bold'
                      : 'text-amber-800 font-bold'
                  }`}>
                    {compliance.status.replace('_', ' ').toUpperCase()}
                  </strong>
                </div>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded font-sans text-xs">
                <p className="font-bold text-slate-800 mb-1">Engineering Compliance Reasoning:</p>
                <p className="text-slate-700 leading-relaxed">{compliance.explanation}</p>
                {compliance.missing_information && (
                  <p className="mt-2 text-[11px] font-mono text-slate-500 border-t border-slate-100 pt-1.5">
                    <strong>Missing Information for Final Certification:</strong> {compliance.missing_information}
                  </p>
                )}
              </div>

              {/* Multi-Standard Benchmark Comparison Table */}
              {(compliance as any).multi_standard_comparison && (
                <div className="mt-4 pt-3 border-t border-slate-300">
                  <div className="flex items-center gap-2 mb-2 text-xs font-mono font-bold text-slate-800 uppercase">
                    <Globe className="h-3.5 w-3.5 text-safetyOrange" />
                    <span>Global Benchmark Cross-Comparison</span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                    {Object.entries((compliance as any).multi_standard_comparison).map(([code, std]: [string, any]) => (
                      <div 
                        key={code} 
                        className={`p-2 rounded border text-center ${
                          code === compliance.standard_code 
                            ? 'bg-amber-100/80 border-safetyOrange text-slate-900 font-bold'
                            : 'bg-white border-slate-200 text-slate-700'
                        }`}
                      >
                        <span className="text-[10px] block text-slate-500">{code}</span>
                        <span className="text-[11px] font-bold block">{std.limit_mm} mm max</span>
                        <span className={`text-[10px] ${std.compliant ? 'text-emerald-700' : 'text-rose-700 font-bold'}`}>
                          {std.compliant ? 'WITHIN LIMIT' : 'EXCEEDS'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Legacy Fallback */
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
                  {aciData.compliant ? 'PROVISIONALLY CONSISTENT' : 'LIMIT EXCEEDED (' + aciData.delta + ')'}
                </strong>
              </div>
            </div>
          )}
        </div>

        {/* Engineering Remediation Specification */}
        <div className="mt-6 border-2 border-slate-300 rounded-lg p-4 bg-white">
          <div className="flex items-center gap-2 mb-2">
            <Wrench className="h-4 w-4 text-safetyOrange" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-mono">
              Prescribed Structural Action & Remediation Specification
            </h4>
          </div>
          <p className="text-xs text-slate-800 leading-relaxed font-sans mb-3">
            {analysis.recommendation}
          </p>
          <div className="p-2.5 bg-slate-100 rounded text-[11px] font-mono text-slate-600 border border-slate-200">
            <strong>Standard Material Specification:</strong> For structural cracks &gt; 0.3mm exhibiting distress, execute pressure injection with epoxy resin complying with ASTM C881 Type I/IV Grade 1. For non-structural shrinkage, rout to 6mm×6mm and apply elastomeric polyurethane sealant.
          </div>
        </div>

        {/* Section 10: Engineering Safety Disclaimer */}
        <div className="mt-6 p-3 bg-amber-50/90 border border-amber-300 rounded text-[11px] font-sans text-amber-950">
          <div className="flex items-center gap-1.5 font-bold uppercase font-mono text-amber-900 mb-0.5">
            <Shield className="h-3.5 w-3.5 text-safetyOrange" />
            <span>Engineering Scope & Safety Disclaimer</span>
          </div>
          <p className="leading-relaxed">
            {analysis.unsupported_claims_disclaimer || 
              "Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone. A physical inspection by a Licensed Professional Engineer (PE/SE) is required for structural signoff."}
          </p>
        </div>

        {/* Report Actions */}
        <div className="mt-8 flex flex-col sm:flex-row gap-3 pt-5 border-t border-slate-300 no-print">
          <button
            onClick={() => window.print()}
            className="flex-1 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm py-2.5 px-5 rounded-md shadow-sm transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <Printer className="h-4 w-4" />
            <span>Print Official Structural Report</span>
          </button>

          <button
            onClick={onReset}
            className="flex-1 bg-safetyOrange hover:bg-orange-600 text-white font-bold text-xs sm:text-sm py-2.5 px-5 rounded-md shadow-sm transition-colors flex items-center justify-center gap-2 cursor-pointer"
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
          Use the optical comparator card below to visually cross-verify the crack aperture against physical millimeter graduation lines.
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
