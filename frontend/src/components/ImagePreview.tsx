import { useState } from 'react';
import { AnalysisResult } from '../types/analysis';
import { Ruler, ZoomIn, ZoomOut, Crosshair, Sparkles } from 'lucide-react';
import CrackComparatorCard from './CrackComparatorCard';

interface ImagePreviewProps {
  analysis: AnalysisResult;
  imageUrl: string;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ analysis, imageUrl }) => {
  const [viewMode, setViewMode] = useState<'overlay' | 'split' | 'original'>('overlay');
  const [showComparator, setShowComparator] = useState<boolean>(true);
  const [isZoomed, setIsZoomed] = useState<boolean>(false);
  const [hoveredPolygon, setHoveredPolygon] = useState<number | null>(null);

  const hasCrack = analysis.status === 'crack_detected';
  const hasPolygons = (analysis.normalized_polygons && analysis.normalized_polygons.length > 0) ||
                      (analysis.polygons && analysis.polygons.length > 0);

  // Render authentic SVG polygonal contours
  const renderPolygonOverlay = () => {
    if (!hasCrack) return null;

    if (analysis.normalized_polygons && analysis.normalized_polygons.length > 0) {
      return (
        <svg
          className="absolute inset-0 w-full h-full pointer-events-auto"
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
        >
          <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>
          {analysis.normalized_polygons.map((poly, pIdx) => {
            const pointsStr = poly
              .map(([nx, ny]) => `${Math.round(nx * 1000)},${Math.round(ny * 1000)}`)
              .join(' ');
            const isHovered = hoveredPolygon === pIdx;

            return (
              <g 
                key={pIdx} 
                onMouseEnter={() => setHoveredPolygon(pIdx)}
                onMouseLeave={() => setHoveredPolygon(null)}
                className="cursor-crosshair group"
              >
                {/* Outer Glow contour */}
                <polygon
                  points={pointsStr}
                  className={`transition-all duration-150 ${
                    isHovered
                      ? 'fill-orange-500/50 stroke-orange-400 stroke-[3]'
                      : 'fill-safetyOrange/30 stroke-safetyOrange stroke-2'
                  }`}
                  style={{ vectorEffect: 'non-scaling-stroke' }}
                />

                {/* Centerline accent */}
                <polygon
                  points={pointsStr}
                  fill="none"
                  className="stroke-amber-300 stroke-1 opacity-70"
                  style={{ vectorEffect: 'non-scaling-stroke' }}
                />
              </g>
            );
          })}
        </svg>
      );
    }

    // Fallback: If no polygons present but crack detected, show CAD wireframe pattern
    return (
      <div className="absolute inset-0 pointer-events-none bg-[url('/crack-pattern.svg')] bg-cover mix-blend-screen opacity-90" />
    );
  };

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
                <div className="bg-slate-800 text-white font-mono text-[10px] px-2.5 py-1 font-bold flex items-center justify-between">
                  <span>RAW SURFACE ORTHOMOSAIC</span>
                  <span className="text-slate-400">UNPROCESSED</span>
                </div>
                <img
                  src={imageUrl}
                  alt="Raw surface"
                  className="w-full h-auto max-h-[380px] object-contain mx-auto"
                />
              </div>

              <div className="border-2 border-slate-300 rounded-lg overflow-hidden bg-white shadow-xs relative">
                <div className="bg-safetyOrange text-white font-mono text-[10px] px-2.5 py-1 font-bold flex items-center justify-between">
                  <span>SEGMENTED DEFECT TRACE</span>
                  <span className="bg-slate-900/40 px-1.5 py-0.2 rounded text-[9px]">
                    {analysis.has_segmentation ? 'YOLOv8-SEG' : 'CAD VECTOR'}
                  </span>
                </div>
                <div className="relative overflow-hidden flex items-center justify-center bg-slate-950">
                  <img
                    src={imageUrl}
                    alt="Segmented surface"
                    className="w-full h-auto max-h-[380px] object-contain mx-auto"
                  />
                  {renderPolygonOverlay()}
                </div>
              </div>
            </div>
          ) : (
            /* Standard Viewport with Technical Crosshairs */
            <div className="border-2 border-slate-400 rounded-lg overflow-hidden bg-slate-900 shadow-md relative">
              {/* Technical HUD Overlay Bar */}
              <div className="absolute top-2 left-2 z-10 bg-slate-950/85 text-white font-mono text-[10px] px-2.5 py-1 rounded border border-slate-700 flex items-center gap-2 backdrop-blur-xs">
                <Crosshair className="h-3.5 w-3.5 text-safetyOrange" />
                <span className="font-bold">FIELD SCAN • {analysis.crack_type.toUpperCase()}</span>
                {analysis.has_segmentation && (
                  <span className="bg-safetyOrange/20 text-orange-300 border border-safetyOrange/40 px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1">
                    <Sparkles className="h-2.5 w-2.5" />
                    {analysis.defect_count ?? 1} DEFECT MASK{(analysis.defect_count ?? 1) > 1 ? 'S' : ''}
                  </span>
                )}
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

                {/* Polygonal Contour Overlay */}
                {viewMode === 'overlay' && renderPolygonOverlay()}
              </div>

              {/* Bottom Calibrated Status Footer */}
              <div className="bg-slate-900 border-t border-slate-800 text-slate-300 px-3 py-1.5 font-mono text-[10px] flex flex-wrap items-center justify-between gap-2">
                <div>
                  Estimated Aperture: <strong className="text-safetyOrange font-bold">{analysis.estimated_width}</strong>
                </div>
                <div className="hidden sm:inline">
                  Defect Area: <strong>{analysis.affected_area}</strong>
                </div>
                <div>
                  Confidence: <strong>{analysis.confidence.toFixed(1)}%</strong>
                </div>
                {analysis.inference_time_ms !== undefined && (
                  <div className="text-slate-400">
                    Latency: <span className="text-emerald-400">{analysis.inference_time_ms} ms</span>
                  </div>
                )}
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
