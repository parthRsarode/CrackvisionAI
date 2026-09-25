import { useState } from 'react';
import { AnalysisResult } from '../types/analysis';
import { Ruler, Eye, SplitSquareVertical, ZoomIn, ZoomOut, Compass, Crosshair } from 'lucide-react';
import CrackComparatorCard from './CrackComparatorCard';

interface ImagePreviewProps {
  analysis: AnalysisResult;
  imageUrl: string;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ analysis, imageUrl }) => {
  const [viewMode, setViewMode] = useState<'overlay' | 'split' | 'original'>('overlay');
  const [showComparator, setShowComparator] = useState<boolean>(true);
  const [isZoomed, setIsZoomed] = useState<boolean>(false);

  const hasCrack = analysis.status === 'crack_detected';

  return (
    <div className="space-y-4">
      {/* CAD Inspection Toolbar */}
      <div className="bg-slate-100 border border-slate-300 p-2.5 rounded-lg flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
        {/* Mode Selector */}
        <div className="flex items-center gap-1 bg-white p-1 rounded border border-slate-300">
          <button
            onClick={() => setViewMode('overlay')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
              viewMode === 'overlay'
                ? 'bg-civilNavy text-white'
                : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Defect Contour
          </button>
          <button
            onClick={() => setViewMode('split')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
              viewMode === 'split'
                ? 'bg-civilNavy text-white'
                : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Split Verification
          </button>
          <button
            onClick={() => setViewMode('original')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
              viewMode === 'original'
                ? 'bg-civilNavy text-white'
                : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Raw Surface
          </button>
        </div>

        {/* Crack Comparator Card Toggle */}
        <button
          onClick={() => setShowComparator(!showComparator)}
          className={`px-3 py-1.5 rounded text-xs font-bold flex items-center gap-1.5 transition-colors border ${
            showComparator 
              ? 'bg-amber-100 text-amber-900 border-amber-400' 
              : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
          }`}
        >
          <Ruler className="h-3.5 w-3.5 text-safetyOrange" />
          <span>{showComparator ? 'Hide ACI Comparator Card' : 'Show ACI Comparator Card'}</span>
        </button>

        {/* Zoom controls */}
        <button
          onClick={() => setIsZoomed(!isZoomed)}
          className="px-2.5 py-1.5 bg-white border border-slate-300 rounded text-slate-700 hover:bg-slate-50 flex items-center gap-1 font-bold"
        >
          {isZoomed ? <ZoomOut className="h-3.5 w-3.5" /> : <ZoomIn className="h-3.5 w-3.5" />}
          <span>{isZoomed ? 'Normal View' : 'Magnify (1.25x)'}</span>
        </button>
      </div>

      {/* Main Inspection Viewport Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Image Frame */}
        <div className={showComparator ? 'lg:col-span-8' : 'lg:col-span-12'}>
          {viewMode === 'split' ? (
            /* Split Screen */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="border-2 border-slate-300 rounded-lg overflow-hidden bg-white shadow-xs">
                <div className="bg-slate-800 text-white font-mono text-[10px] px-2.5 py-1 font-bold">
                  RAW SURFACE ORTHOMOSAIC
                </div>
                <img
                  src={imageUrl}
                  alt="Raw surface"
                  className="w-full h-auto max-h-[380px] object-contain mx-auto"
                />
              </div>

              <div className="border-2 border-slate-300 rounded-lg overflow-hidden bg-white shadow-xs relative">
                <div className="bg-safetyOrange text-white font-mono text-[10px] px-2.5 py-1 font-bold">
                  SEGMENTED DEFECT TRACE
                </div>
                <img
                  src={imageUrl}
                  alt="Segmented surface"
                  className="w-full h-auto max-h-[380px] object-contain mx-auto"
                />
                {hasCrack && (
                  <div className="absolute inset-0 top-6 pointer-events-none bg-[url('/crack-pattern.svg')] bg-cover mix-blend-multiply opacity-90" />
                )}
              </div>
            </div>
          ) : (
            /* Standard Viewport with Technical Crosshairs */
            <div className="border-2 border-slate-400 rounded-lg overflow-hidden bg-slate-900 shadow-md relative">
              {/* Technical HUD Overlay Bar */}
              <div className="absolute top-2 left-2 z-10 bg-slate-950/80 text-white font-mono text-[10px] px-2 py-0.5 rounded border border-slate-700 flex items-center gap-1.5">
                <Crosshair className="h-3 w-3 text-safetyOrange" />
                <span>FIELD SCAN • {analysis.crack_type.toUpperCase()}</span>
              </div>

              <div className="relative overflow-hidden flex items-center justify-center min-h-[340px] bg-slate-950">
                <img
                  src={imageUrl}
                  alt="Concrete surface inspection"
                  className={`max-w-full max-h-[460px] object-contain mx-auto transition-transform ${
                    isZoomed ? 'scale-125 cursor-zoom-out' : 'cursor-zoom-in'
                  }`}
                  onClick={() => setIsZoomed(!isZoomed)}
                />

                {/* Red Contour Overlay */}
                {viewMode === 'overlay' && hasCrack && (
                  <div className="absolute inset-0 pointer-events-none bg-[url('/crack-pattern.svg')] bg-cover mix-blend-screen opacity-90" />
                )}
              </div>

              {/* Bottom Calibrated Status Footer */}
              <div className="bg-slate-900 border-t border-slate-800 text-slate-300 px-3 py-1.5 font-mono text-[10px] flex items-center justify-between">
                <span>Estimated Aperture: <strong className="text-safetyOrange font-bold">{analysis.estimated_width}</strong></span>
                <span className="hidden sm:inline">Defect Area: <strong>{analysis.affected_area}</strong></span>
                <span>Certainty: <strong>{analysis.confidence.toFixed(1)}%</strong></span>
              </div>
            </div>
          )}
        </div>

        {/* Side Panel: Authentic ACI Crack Comparator Card */}
        {showComparator && (
          <div className="lg:col-span-4 flex flex-col justify-start">
            <CrackComparatorCard 
              onClose={() => setShowComparator(false)} 
              detectedWidth={analysis.estimated_width}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ImagePreview;
