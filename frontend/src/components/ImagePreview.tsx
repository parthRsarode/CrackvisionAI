import React, { useState, useRef, useEffect, useCallback } from 'react';
import { AnalysisResult, CaliperSample } from '../types/analysis';
import { 
  Ruler, 
  ZoomIn, 
  ZoomOut, 
  Crosshair, 
  Sparkles, 
  CheckCircle2, 
  Gauge, 
  Sliders, 
  RotateCcw, 
  Tag, 
  Info,
  Check,
  AlertTriangle
} from 'lucide-react';
import CrackComparatorCard from './CrackComparatorCard';
import CaliperSamplesTable from './CaliperSamplesTable';

interface ImagePreviewProps {
  analysis: AnalysisResult;
  imageUrl: string;
  onUpdateAnalysis?: (updated: AnalysisResult) => void;
}

interface ImageBounds {
  left: number;
  top: number;
  width: number;
  height: number;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ analysis, imageUrl, onUpdateAnalysis }) => {
  const [viewMode, setViewMode] = useState<'overlay' | 'split' | 'original'>('overlay');
  const [showComparator, setShowComparator] = useState<boolean>(true);
  const [isZoomed, setIsZoomed] = useState<boolean>(false);
  const [hoveredPolygon, setHoveredPolygon] = useState<number | null>(null);
  
  const [imageBounds, setImageBounds] = useState<ImageBounds | null>(null);

  // Phase 04: Interactive Spatial Calibration States
  const [activeTool, setActiveTool] = useState<'inspect' | 'calibrate' | 'caliper'>('inspect');
  const [calibPoints, setCalibPoints] = useState<[number, number][]>([]);
  const [isCalibModalOpen, setIsCalibModalOpen] = useState<boolean>(false);
  const [calibDistanceInput, setCalibDistanceInput] = useState<string>('50.0');
  const [calibUnit, setCalibUnit] = useState<'mm' | 'in'>('mm');

  // Scale factor: mm per pixel
  const initialMmPerPx = analysis.calibration?.mm_per_pixel || 0.234;
  const [mmPerPixel, setMmPerPixel] = useState<number>(initialMmPerPx);
  const [scaleMethod, setScaleMethod] = useState<string>(analysis.calibration?.method || 'default_macro');

  // Digital Caliper States
  const [caliperMode, setCaliperMode] = useState<'probe' | 'span'>('probe');
  const [caliperTempPoints, setCaliperTempPoints] = useState<[number, number][]>([]);
  const [caliperSamples, setCaliperSamples] = useState<CaliperSample[]>(analysis.caliper_samples || []);
  const [hoveredSampleId, setHoveredSampleId] = useState<string | null>(null);
  const [showCaliperLog, setShowCaliperLog] = useState<boolean>(true);

  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const hasCrack = analysis.status === 'crack_detected';
  const currentStandardCode = analysis.compliance_details?.standard_code || 
                              analysis.multi_factor_metrics?.standard_code || 
                              'ACI';

  // Standard permissible limit in mm for compliance checks
  const getStandardPermissibleLimit = useCallback((): number => {
    switch (currentStandardCode) {
      case 'IS456':
        return 0.20;
      case 'EC2':
        return 0.30;
      case 'BS8110':
        return 0.30;
      case 'ACI':
      default:
        return 0.30;
    }
  }, [currentStandardCode]);

  const allowableLimitMm = getStandardPermissibleLimit();

  const updateImageBounds = useCallback(() => {
    if (!imgRef.current || !containerRef.current) return;
    const img = imgRef.current;
    const container = containerRef.current;

    const containerRect = container.getBoundingClientRect();
    const imgRect = img.getBoundingClientRect();

    if (imgRect.width === 0 || imgRect.height === 0) return;

    setImageBounds({
      left: imgRect.left - containerRect.left,
      top: imgRect.top - containerRect.top,
      width: imgRect.width,
      height: imgRect.height,
    });
  }, []);

  useEffect(() => {
    updateImageBounds();
    window.addEventListener('resize', updateImageBounds);
    return () => window.removeEventListener('resize', updateImageBounds);
  }, [updateImageBounds, isZoomed, viewMode]);

  // Convert mouse click on viewport to 0-1 normalized image coordinates
  const getNormalizedClick = (e: React.MouseEvent<HTMLDivElement>): [number, number] | null => {
    if (!imgRef.current) return null;
    const rect = imgRef.current.getBoundingClientRect();
    const clientX = e.clientX;
    const clientY = e.clientY;

    if (
      clientX < rect.left || 
      clientX > rect.right || 
      clientY < rect.top || 
      clientY > rect.bottom
    ) {
      return null;
    }

    const normX = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const normY = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));

    return [normX, normY];
  };

  // Localized crack aperture probe calculation (normal distance across closest polygon)
  const probeApertureLocally = (normClick: [number, number]): CaliperSample | null => {
    if (!analysis.normalized_polygons || analysis.normalized_polygons.length === 0) return null;
    if (!imgRef.current) return null;

    const naturalWidth = imgRef.current.naturalWidth || 1000;
    const naturalHeight = imgRef.current.naturalHeight || 1000;

    const clickPx: [number, number] = [normClick[0] * naturalWidth, normClick[1] * naturalHeight];

    // Find nearest polygon and segment
    let bestDist = Infinity;
    let bestPoly: number[][] | null = null;
    let bestTangent: [number, number] = [1, 0];

    for (const poly of analysis.normalized_polygons) {
      const n = poly.length;
      for (let i = 0; i < n; i++) {
        const p1 = [poly[i][0] * naturalWidth, poly[i][1] * naturalHeight];
        const p2 = [poly[(i + 1) % n][0] * naturalWidth, poly[(i + 1) % n][1] * naturalHeight];

        const seg = [p2[0] - p1[0], p2[1] - p1[1]];
        const segLen = Math.hypot(seg[0], seg[1]);
        if (segLen < 1e-4) continue;

        const u = Math.max(0, Math.min(1, ((clickPx[0] - p1[0]) * seg[0] + (clickPx[1] - p1[1]) * seg[1]) / (segLen * segLen)));
        const proj = [p1[0] + u * seg[0], p1[1] + u * seg[1]];
        const dist = Math.hypot(clickPx[0] - proj[0], clickPx[1] - proj[1]);

        if (dist < bestDist) {
          bestDist = dist;
          bestPoly = poly;
          bestTangent = [seg[0] / segLen, seg[1] / segLen];
        }
      }
    }

    if (!bestPoly || bestDist > 80) {
      return null;
    }

    // Normal vector
    const norm = [-bestTangent[1], bestTangent[0]];

    // Approximate thickness from local contour or polygon bounds
    const samplePxWidth = Math.max(bestDist * 2.0, 3.5);
    const halfSpan = samplePxWidth / 2.0;

    const spanP1: [number, number] = [clickPx[0] - norm[0] * halfSpan, clickPx[1] - norm[1] * halfSpan];
    const spanP2: [number, number] = [clickPx[0] + norm[0] * halfSpan, clickPx[1] + norm[1] * halfSpan];

    const normP1: [number, number] = [spanP1[0] / naturalWidth, spanP1[1] / naturalHeight];
    const normP2: [number, number] = [spanP2[0] / naturalWidth, spanP2[1] / naturalHeight];

    const widthMm = Number((samplePxWidth * mmPerPixel).toFixed(3));
    const nextIdx = caliperSamples.length + 1;
    const sampleId = `CAL-${String(nextIdx).padStart(2, '0')}`;

    return {
      id: sampleId,
      x: clickPx[0],
      y: clickPx[1],
      width_px: Number(samplePxWidth.toFixed(1)),
      width_mm: widthMm,
      points: [spanP1, spanP2],
      normalized_points: [normP1, normP2],
      timestamp: new Date().toLocaleTimeString(),
      compliance_status: widthMm <= allowableLimitMm ? 'within_limit' : 'exceeds_limit',
    };
  };

  // Handle click on the image viewport
  const handleViewportClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const norm = getNormalizedClick(e);
    if (!norm) return;

    if (activeTool === 'calibrate') {
      if (calibPoints.length === 0) {
        setCalibPoints([norm]);
      } else if (calibPoints.length === 1) {
        setCalibPoints([calibPoints[0], norm]);
        setIsCalibModalOpen(true);
      }
    } else if (activeTool === 'caliper') {
      if (caliperMode === 'probe') {
        const probed = probeApertureLocally(norm);
        if (probed) {
          const updated = [...caliperSamples, probed];
          setCaliperSamples(updated);
          if (onUpdateAnalysis) {
            onUpdateAnalysis({ ...analysis, caliper_samples: updated });
          }
        }
      } else {
        // Two-point caliper span mode
        if (caliperTempPoints.length === 0) {
          setCaliperTempPoints([norm]);
        } else if (caliperTempPoints.length === 1) {
          const p1 = caliperTempPoints[0];
          const p2 = norm;
          const naturalWidth = imgRef.current?.naturalWidth || 1000;
          const naturalHeight = imgRef.current?.naturalHeight || 1000;

          const pxDist = Math.hypot((p2[0] - p1[0]) * naturalWidth, (p2[1] - p1[1]) * naturalHeight);
          const widthMm = Number((pxDist * mmPerPixel).toFixed(3));
          const nextIdx = caliperSamples.length + 1;
          const sampleId = `CAL-${String(nextIdx).padStart(2, '0')}`;

          const newSample: CaliperSample = {
            id: sampleId,
            x: ((p1[0] + p2[0]) / 2) * naturalWidth,
            y: ((p1[1] + p2[1]) / 2) * naturalHeight,
            width_px: Number(pxDist.toFixed(1)),
            width_mm: widthMm,
            points: [
              [p1[0] * naturalWidth, p1[1] * naturalHeight],
              [p2[0] * naturalWidth, p2[1] * naturalHeight],
            ],
            normalized_points: [p1, p2],
            timestamp: new Date().toLocaleTimeString(),
            compliance_status: widthMm <= allowableLimitMm ? 'within_limit' : 'exceeds_limit',
          };

          const updated = [...caliperSamples, newSample];
          setCaliperSamples(updated);
          setCaliperTempPoints([]);
          if (onUpdateAnalysis) {
            onUpdateAnalysis({ ...analysis, caliper_samples: updated });
          }
        }
      }
    }
  };

  // Apply Two-Point Millimeter Calibration
  const applyTwoPointCalibration = () => {
    if (calibPoints.length < 2 || !imgRef.current) return;
    const naturalWidth = imgRef.current.naturalWidth || 1000;
    const naturalHeight = imgRef.current.naturalHeight || 1000;

    const p1 = calibPoints[0];
    const p2 = calibPoints[1];

    const distPx = Math.hypot((p2[0] - p1[0]) * naturalWidth, (p2[1] - p1[1]) * naturalHeight);
    if (distPx < 1) return;

    let targetMm = parseFloat(calibDistanceInput);
    if (isNaN(targetMm) || targetMm <= 0) targetMm = 50.0;
    if (calibUnit === 'in') targetMm = targetMm * 25.4;

    const newScale = Number((targetMm / distPx).toFixed(4));
    setMmPerPixel(newScale);
    setScaleMethod('manual_two_point');

    // Rescale all existing caliper samples
    const rescaledSamples = caliperSamples.map((s) => {
      const rescaledWidth = Number((s.width_px * newScale).toFixed(3));
      return {
        ...s,
        width_mm: rescaledWidth,
        compliance_status: rescaledWidth <= allowableLimitMm ? ('within_limit' as const) : ('exceeds_limit' as const),
      };
    });
    setCaliperSamples(rescaledSamples);

    setIsCalibModalOpen(false);
    setCalibPoints([]);
    setActiveTool('inspect');

    // Recompute estimated width string
    const ratio = newScale / initialMmPerPx;
    let updatedWidthStr = analysis.estimated_width;
    const parts = analysis.estimated_width.split('-');
    if (parts.length === 2) {
      const w1 = parseFloat(parts[0]) * ratio;
      const w2 = parseFloat(parts[1]) * ratio;
      updatedWidthStr = `${w1.toFixed(2)} - ${w2.toFixed(2)} mm`;
    }

    if (onUpdateAnalysis) {
      onUpdateAnalysis({
        ...analysis,
        estimated_width: updatedWidthStr,
        calibration: {
          calibration_status: 'user_two_point_calibrated',
          method: 'manual_two_point',
          mm_per_pixel: newScale,
          assumed_field_width_m: Number(((newScale * naturalWidth) / 1000).toFixed(4)),
          confidence: 100.0,
        },
        caliper_samples: rescaledSamples,
      });
    }
  };

  // Reset scale to auto-detected fiducial or default macro
  const resetScale = () => {
    const defaultScale = analysis.calibration?.mm_per_pixel || 0.234;
    setMmPerPixel(defaultScale);
    setScaleMethod(analysis.calibration?.method || 'default_macro');
    setCalibPoints([]);
    setIsCalibModalOpen(false);

    // Rescale caliper samples
    const rescaled = caliperSamples.map((s) => ({
      ...s,
      width_mm: Number((s.width_px * defaultScale).toFixed(3)),
    }));
    setCaliperSamples(rescaled);

    if (onUpdateAnalysis) {
      onUpdateAnalysis({
        ...analysis,
        caliper_samples: rescaled,
      });
    }
  };

  const deleteCaliperSample = (id: string) => {
    const updated = caliperSamples.filter((s) => s.id !== id);
    setCaliperSamples(updated);
    if (onUpdateAnalysis) {
      onUpdateAnalysis({ ...analysis, caliper_samples: updated });
    }
  };

  const clearAllCaliperSamples = () => {
    setCaliperSamples([]);
    if (onUpdateAnalysis) {
      onUpdateAnalysis({ ...analysis, caliper_samples: [] });
    }
  };

  // SVG Overlay Renderer
  const renderSVGOverlay = () => {
    const svgStyle: React.CSSProperties = imageBounds
      ? {
          position: 'absolute',
          left: `${imageBounds.left}px`,
          top: `${imageBounds.top}px`,
          width: `${imageBounds.width}px`,
          height: `${imageBounds.height}px`,
          pointerEvents: 'auto',
        }
      : {
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'auto',
        };

    return (
      <svg
        style={svgStyle}
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
        className="overflow-visible"
      >
        <defs>
          <filter id="hudGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* 1. Detected ArUco Fiducial Marker Box (REQ-3.2) */}
        {analysis.calibration?.normalized_corners && analysis.calibration.normalized_corners.length === 4 && (
          <g className="fiducial-hud">
            {(() => {
              const corners = analysis.calibration.normalized_corners!;
              const ptsStr = corners
                .map(([nx, ny]) => `${Math.round(nx * 1000)},${Math.round(ny * 1000)}`)
                .join(' ');
              const minX = Math.min(...corners.map((c) => c[0] * 1000));
              const minY = Math.min(...corners.map((c) => c[1] * 1000));

              return (
                <>
                  <polygon
                    points={ptsStr}
                    className="fill-cyan-400/20 stroke-cyan-400 stroke-2"
                    strokeDasharray="6 3"
                    filter="url(#hudGlow)"
                  />
                  {corners.map(([nx, ny], cIdx) => (
                    <circle
                      key={cIdx}
                      cx={nx * 1000}
                      cy={ny * 1000}
                      r="4"
                      className="fill-cyan-300 stroke-slate-950 stroke-1"
                    />
                  ))}
                  <g transform={`translate(${minX}, ${Math.max(minY - 14, 15)})`}>
                    <rect x="0" y="-12" width="160" height="16" rx="3" className="fill-slate-950/90 stroke-cyan-400 stroke-1" />
                    <text x="6" y="0" className="fill-cyan-300 font-mono text-[10px] font-bold">
                      ARUCO #{analysis.calibration?.marker_id ?? 0} • 50mm REF
                    </text>
                  </g>
                </>
              );
            })()}
          </g>
        )}

        {/* 2. Detected Crack Polygons */}
        {hasCrack &&
          analysis.normalized_polygons &&
          analysis.normalized_polygons.map((poly, pIdx) => {
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
                <polygon
                  points={pointsStr}
                  className={`transition-all duration-150 ${
                    isHovered
                      ? 'fill-orange-500/60 stroke-orange-400 stroke-[3]'
                      : 'fill-safetyOrange/40 stroke-safetyOrange stroke-2'
                  }`}
                  style={{ vectorEffect: 'non-scaling-stroke' }}
                />
                <polygon
                  points={pointsStr}
                  fill="none"
                  className="stroke-amber-300 stroke-1 opacity-80"
                  style={{ vectorEffect: 'non-scaling-stroke' }}
                />
              </g>
            );
          })}

        {/* 3. Scale Calibration Line (REQ-3.1) */}
        {calibPoints.length > 0 && (
          <g className="calibration-drafting-line">
            {calibPoints.map(([nx, ny], idx) => (
              <g key={idx}>
                <circle cx={nx * 1000} cy={ny * 1000} r="6" className="fill-amber-400 stroke-slate-950 stroke-2" />
                <circle cx={nx * 1000} cy={ny * 1000} r="2" className="fill-white" />
                <line x1={nx * 1000 - 12} y1={ny * 1000} x2={nx * 1000 + 12} y2={ny * 1000} className="stroke-amber-400 stroke-1" />
                <line x1={nx * 1000} y1={ny * 1000 - 12} x2={nx * 1000} y2={ny * 1000 + 12} className="stroke-amber-400 stroke-1" />
                <text x={nx * 1000 + 8} y={ny * 1000 - 8} className="fill-amber-300 font-mono text-[11px] font-bold drop-shadow">
                  POINT {idx === 0 ? 'A' : 'B'}
                </text>
              </g>
            ))}
            {calibPoints.length === 2 && (
              <>
                <line
                  x1={calibPoints[0][0] * 1000}
                  y1={calibPoints[0][1] * 1000}
                  x2={calibPoints[1][0] * 1000}
                  y2={calibPoints[1][1] * 1000}
                  className="stroke-amber-400 stroke-2"
                  strokeDasharray="4 2"
                />
                <g
                  transform={`translate(${((calibPoints[0][0] + calibPoints[1][0]) / 2) * 1000}, ${
                    ((calibPoints[0][1] + calibPoints[1][1]) / 2) * 1000 - 12
                  })`}
                >
                  <rect x="-45" y="-12" width="90" height="18" rx="3" className="fill-slate-950/90 stroke-amber-400 stroke-1" />
                  <text x="0" y="1" textAnchor="middle" className="fill-amber-300 font-mono text-[10px] font-bold">
                    CALIBRATE
                  </text>
                </g>
              </>
            )}
          </g>
        )}

        {/* 4. Active Caliper Temp Measurement Line (REQ-3.3) */}
        {caliperTempPoints.length === 1 && (
          <circle
            cx={caliperTempPoints[0][0] * 1000}
            cy={caliperTempPoints[0][1] * 1000}
            r="6"
            className="fill-safetyOrange stroke-white stroke-2 animate-ping"
          />
        )}

        {/* 5. Placed Caliper Measurement Callouts (REQ-3.3) */}
        {caliperSamples.map((sample) => {
          if (!sample.normalized_points || sample.normalized_points.length < 2) return null;
          const [p1, p2] = sample.normalized_points;
          const x1 = p1[0] * 1000;
          const y1 = p1[1] * 1000;
          const x2 = p2[0] * 1000;
          const y2 = p2[1] * 1000;

          const midX = (x1 + x2) / 2;
          const midY = (y1 + y2) / 2;
          const dx = x2 - x1;
          const dy = y2 - y1;
          const len = Math.hypot(dx, dy) || 1;
          const nx = -dy / len;
          const ny = dx / len;

          const jawLen = 14;
          const exceeds = sample.width_mm > allowableLimitMm;
          const isHovered = hoveredSampleId === sample.id;

          const strokeColor = exceeds ? 'stroke-rose-400' : 'stroke-emerald-400';
          const fillColor = exceeds ? 'fill-rose-400' : 'fill-emerald-400';

          return (
            <g
              key={sample.id}
              className="cursor-pointer group"
              onMouseEnter={() => setHoveredSampleId(sample.id)}
              onMouseLeave={() => setHoveredSampleId(null)}
              onClick={(e) => {
                e.stopPropagation();
                deleteCaliperSample(sample.id);
              }}
            >
              {/* Caliper Jaw 1 */}
              <line
                x1={x1 - nx * jawLen}
                y1={y1 - ny * jawLen}
                x2={x1 + nx * jawLen}
                y2={y1 + ny * jawLen}
                className={`${strokeColor} stroke-2`}
              />
              {/* Caliper Jaw 2 */}
              <line
                x1={x2 - nx * jawLen}
                y1={y2 - ny * jawLen}
                x2={x2 + nx * jawLen}
                y2={y2 + ny * jawLen}
                className={`${strokeColor} stroke-2`}
              />
              {/* Caliper Dimension Bar */}
              <line x1={x1} y1={y1} x2={x2} y2={y2} className={`${strokeColor} stroke-2`} />

              {/* Callout Badge */}
              <g transform={`translate(${midX}, ${Math.max(midY - 14, 15)})`}>
                <rect
                  x="-42"
                  y="-12"
                  width="84"
                  height="16"
                  rx="3"
                  className={`fill-slate-950/95 stroke-1 transition-all ${
                    isHovered ? 'stroke-amber-400 fill-slate-900' : exceeds ? 'stroke-rose-500' : 'stroke-emerald-500'
                  }`}
                />
                <circle cx="-32" cy="-4" r="3" className={fillColor} />
                <text x="-24" y="-1" className="fill-white font-mono text-[9px] font-bold">
                  {sample.id}: {sample.width_mm.toFixed(2)} mm
                </text>
              </g>
            </g>
          );
        })}
      </svg>
    );
  };

  // Graphical CAD Scale Bar Width Calculation
  const calculateScaleBarWidth = (): { barLengthMm: number; widthPx: number } => {
    // Choose appropriate scale interval (5mm, 10mm, 20mm, or 50mm)
    const containerWidth = imageBounds?.width || 600;
    const targetPx = 100; // desired scale bar pixel length on screen
    const rawMm = targetPx * mmPerPixel;

    let barLengthMm = 10;
    if (rawMm > 35) barLengthMm = 50;
    else if (rawMm > 15) barLengthMm = 20;
    else if (rawMm < 4) barLengthMm = 2;
    else if (rawMm < 8) barLengthMm = 5;

    const widthPx = Math.round(barLengthMm / mmPerPixel);
    return { barLengthMm, widthPx: Math.max(widthPx, 40) };
  };

  const scaleBarInfo = calculateScaleBarWidth();

  return (
    <div className="space-y-4">
      {/* CAD Inspection & Calibration Toolbar */}
      <div className="bg-slate-100 border border-slate-300 p-2.5 rounded-lg flex flex-wrap items-center justify-between gap-3 text-xs font-mono shadow-xs">
        {/* View Mode Selector */}
        <div className="flex items-center gap-1 bg-white p-1 rounded border border-slate-300">
          <button
            onClick={() => setViewMode('overlay')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors cursor-pointer ${
              viewMode === 'overlay' ? 'bg-civilNavy text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Defect Contour
          </button>
          <button
            onClick={() => setViewMode('split')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors cursor-pointer ${
              viewMode === 'split' ? 'bg-civilNavy text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Split Verification
          </button>
          <button
            onClick={() => setViewMode('original')}
            className={`px-3 py-1 rounded text-xs font-bold transition-colors cursor-pointer ${
              viewMode === 'original' ? 'bg-civilNavy text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            Raw Surface
          </button>
        </div>

        {/* Phase 04 Interactive Tools Group */}
        <div className="flex items-center gap-1 bg-white p-1 rounded border border-slate-300">
          {/* Two-Point Calibration Toggle */}
          <button
            onClick={() => {
              if (activeTool === 'calibrate') {
                setActiveTool('inspect');
                setCalibPoints([]);
              } else {
                setActiveTool('calibrate');
                setCalibPoints([]);
              }
            }}
            className={`px-2.5 py-1 rounded text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              activeTool === 'calibrate'
                ? 'bg-amber-500 text-slate-950 font-black shadow-xs'
                : 'text-slate-700 hover:bg-slate-100'
            }`}
            title="Set known 2-point millimeter distance (e.g. across a ruler or reference card)"
          >
            <Ruler className="h-3.5 w-3.5" />
            <span>{activeTool === 'calibrate' ? 'Calibrating...' : 'Set Scale (2-Pt)'}</span>
          </button>

          {/* Digital Caliper Mode Toggle */}
          <button
            onClick={() => {
              if (activeTool === 'caliper') {
                setActiveTool('inspect');
                setCaliperTempPoints([]);
              } else {
                setActiveTool('caliper');
                setCaliperTempPoints([]);
              }
            }}
            className={`px-2.5 py-1 rounded text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              activeTool === 'caliper'
                ? 'bg-safetyOrange text-white font-black shadow-xs'
                : 'text-slate-700 hover:bg-slate-100'
            }`}
            title="Measure localized crack width aperture"
          >
            <Crosshair className="h-3.5 w-3.5" />
            <span>{activeTool === 'caliper' ? 'Caliper Active' : 'Digital Caliper'}</span>
          </button>
        </div>

        {/* Crack Comparator Card Toggle */}
        <button
          onClick={() => setShowComparator(!showComparator)}
          className={`px-3 py-1.5 rounded text-xs font-bold flex items-center gap-1.5 transition-colors border cursor-pointer ${
            showComparator
              ? 'bg-amber-100 text-amber-900 border-amber-400'
              : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
          }`}
        >
          <Sliders className="h-3.5 w-3.5 text-safetyOrange" />
          <span>{showComparator ? 'Hide Comparator' : 'Show Comparator'}</span>
        </button>

        {/* Zoom controls */}
        <button
          onClick={() => setIsZoomed(!isZoomed)}
          className="px-2.5 py-1.5 bg-white border border-slate-300 rounded text-slate-700 hover:bg-slate-50 flex items-center gap-1 font-bold cursor-pointer"
        >
          {isZoomed ? <ZoomOut className="h-3.5 w-3.5" /> : <ZoomIn className="h-3.5 w-3.5" />}
          <span>{isZoomed ? '1.0x' : '1.25x'}</span>
        </button>
      </div>

      {/* Active Mode Technical Instruction Banner */}
      {activeTool === 'calibrate' && (
        <div className="bg-amber-500/15 border-2 border-amber-500/60 rounded-lg p-2.5 text-amber-950 font-mono text-xs flex items-center justify-between gap-3 animate-enter">
          <div className="flex items-center gap-2">
            <Ruler className="h-4 w-4 text-amber-600 shrink-0" />
            <span>
              <strong>Two-Point Scale Calibration:</strong> Click two reference points with a known real-world dimension (e.g. 0 mm and 50 mm marks on a pocket scale).
              {calibPoints.length === 1 && <strong className="text-amber-800 ml-2">Point 1 selected. Click Point 2.</strong>}
            </span>
          </div>
          <button
            onClick={() => {
              setActiveTool('inspect');
              setCalibPoints([]);
            }}
            className="text-[11px] underline font-bold hover:text-amber-800 cursor-pointer"
          >
            Cancel
          </button>
        </div>
      )}

      {activeTool === 'caliper' && (
        <div className="bg-safetyOrange/15 border-2 border-safetyOrange/60 rounded-lg p-2.5 text-slate-900 font-mono text-xs flex flex-wrap items-center justify-between gap-3 animate-enter">
          <div className="flex items-center gap-2">
            <Crosshair className="h-4 w-4 text-safetyOrange shrink-0" />
            <span>
              <strong>Digital Caliper Mode:</strong>{' '}
              {caliperMode === 'probe'
                ? 'Click anywhere on a segmented crack fissure to auto-probe localized width normal to the fissure.'
                : 'Click 2 points across crack fissure lips to measure localized aperture.'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex bg-white rounded border border-slate-300 p-0.5 text-[11px]">
              <button
                onClick={() => setCaliperMode('probe')}
                className={`px-2 py-0.5 rounded cursor-pointer ${
                  caliperMode === 'probe' ? 'bg-safetyOrange text-white font-bold' : 'text-slate-700'
                }`}
              >
                1-Click Probe
              </button>
              <button
                onClick={() => setCaliperMode('span')}
                className={`px-2 py-0.5 rounded cursor-pointer ${
                  caliperMode === 'span' ? 'bg-safetyOrange text-white font-bold' : 'text-slate-700'
                }`}
              >
                2-Point Span
              </button>
            </div>
            <button
              onClick={() => {
                setActiveTool('inspect');
                setCaliperTempPoints([]);
              }}
              className="text-[11px] underline font-bold hover:text-rose-600 cursor-pointer ml-2"
            >
              Exit Caliper
            </button>
          </div>
        </div>
      )}

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
                  {renderSVGOverlay()}
                </div>
              </div>
            </div>
          ) : (
            /* Standard Viewport with Technical Crosshairs */
            <div className="border-2 border-slate-400 rounded-lg overflow-hidden bg-slate-900 shadow-md relative">
              {/* Technical HUD Overlay Bar */}
              <div className="absolute top-2 left-2 z-10 bg-slate-950/85 text-white font-mono text-[10px] px-2.5 py-1 rounded border border-slate-700 flex flex-wrap items-center gap-2 backdrop-blur-xs">
                <Crosshair className="h-3.5 w-3.5 text-safetyOrange" />
                <span className="font-bold">FIELD SCAN • {analysis.crack_type.toUpperCase()}</span>
                {analysis.has_segmentation && (
                  <span className="bg-safetyOrange/20 text-orange-300 border border-safetyOrange/40 px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1">
                    <Sparkles className="h-2.5 w-2.5" />
                    {analysis.defect_count ?? 1} DEFECT MASK{(analysis.defect_count ?? 1) > 1 ? 'S' : ''}
                  </span>
                )}
                {/* Calibration Status Badge */}
                {scaleMethod === 'aruco_fiducial' ? (
                  <span className="bg-cyan-950 text-cyan-300 border border-cyan-500/50 px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1">
                    <CheckCircle2 className="h-2.5 w-2.5 text-cyan-400" />
                    ARUCO FIDUCIAL CALIBRATED
                  </span>
                ) : scaleMethod === 'manual_two_point' ? (
                  <span className="bg-amber-950 text-amber-300 border border-amber-500/50 px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1">
                    <CheckCircle2 className="h-2.5 w-2.5 text-amber-400" />
                    2-POINT SCALE CALIBRATED
                  </span>
                ) : (
                  <span className="bg-slate-800 text-slate-300 border border-slate-600 px-1.5 py-0.5 rounded text-[9px] font-mono">
                    MACRO FIELD SPEC (0.15m)
                  </span>
                )}
              </div>

              {/* Viewport Canvas */}
              <div
                ref={containerRef}
                onClick={handleViewportClick}
                className={`relative overflow-hidden flex items-center justify-center min-h-[340px] bg-slate-950 ${
                  activeTool === 'calibrate' || activeTool === 'caliper' ? 'cursor-crosshair' : ''
                }`}
              >
                <img
                  ref={imgRef}
                  src={imageUrl}
                  alt="Concrete surface inspection"
                  onLoad={updateImageBounds}
                  className={`max-w-full max-h-[460px] object-contain mx-auto transition-transform ${
                    isZoomed ? 'scale-125' : ''
                  }`}
                />

                {/* SVG Contours, Caliper, and Calibration HUD */}
                {viewMode === 'overlay' && renderSVGOverlay()}

                {/* CAD Drafting Scale Bar HUD (Bottom-Left) */}
                <div className="absolute bottom-2 left-2 z-10 bg-slate-950/85 backdrop-blur-xs border border-slate-700 px-2 py-1 rounded text-white font-mono text-[9px]">
                  <div className="flex items-center gap-2 mb-0.5 text-slate-400">
                    <span>1 px = {mmPerPixel.toFixed(3)} mm</span>
                    {scaleMethod !== 'default_macro' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          resetScale();
                        }}
                        className="text-amber-400 hover:underline flex items-center gap-0.5 cursor-pointer"
                        title="Reset scale"
                      >
                        <RotateCcw className="h-2.5 w-2.5" />
                        <span>Reset</span>
                      </button>
                    )}
                  </div>
                  {/* Visual CAD Scale Bar */}
                  <div className="flex items-center gap-1">
                    <div
                      style={{ width: `${scaleBarInfo.widthPx}px` }}
                      className="h-2 border border-white flex overflow-hidden bg-white"
                    >
                      <div className="w-1/2 h-full bg-slate-900 border-r border-white"></div>
                      <div className="w-1/2 h-full bg-white"></div>
                    </div>
                    <span className="text-white font-bold">{scaleBarInfo.barLengthMm} mm</span>
                  </div>
                </div>
              </div>

              {/* Bottom Calibrated Status Footer */}
              <div className="bg-slate-900 border-t border-slate-800 text-slate-300 px-3 py-1.5 font-mono text-[10px] flex flex-wrap items-center justify-between gap-2">
                <div>
                  Calibrated Aperture: <strong className="text-safetyOrange font-bold">{analysis.estimated_width}</strong>
                </div>
                <div className="hidden sm:inline">
                  Defect Area: <strong>{analysis.affected_area}</strong>
                </div>
                <div>
                  Benchmark: <strong className="text-white font-bold">{currentStandardCode}</strong>
                </div>
                <div>
                  Scale Factor: <strong className="text-emerald-400 font-bold">{mmPerPixel.toFixed(3)} mm/px</strong>
                </div>
                {caliperSamples.length > 0 && (
                  <div>
                    Caliper Samples: <strong className="text-amber-400">{caliperSamples.length} taken</strong>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Caliper Sampling Table (REQ-3.3) */}
          <div className="mt-4">
            <CaliperSamplesTable
              samples={caliperSamples}
              standardCode={currentStandardCode}
              permissibleLimitMm={allowableLimitMm}
              onDeleteSample={deleteCaliperSample}
              onClearAll={clearAllCaliperSamples}
            />
          </div>
        </div>

        {/* Side Panel: Dynamic Benchmark Crack Comparator Card */}
        {showComparator && (
          <div className="lg:col-span-4 flex flex-col justify-start">
            <CrackComparatorCard
              onClose={() => setShowComparator(false)}
              detectedWidth={analysis.estimated_width}
              standardCode={currentStandardCode}
              standardName={analysis.compliance_details?.standard_name}
            />
          </div>
        )}
      </div>

      {/* Two-Point Calibration Measurement Modal (REQ-3.1) */}
      {isCalibModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border-2 border-amber-500 rounded-xl max-w-md w-full p-5 text-white font-mono shadow-2xl animate-enter">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Ruler className="h-5 w-5 text-amber-400" />
                <h3 className="font-bold text-sm uppercase tracking-wider">Two-Point Optical Calibration</h3>
              </div>
              <button
                onClick={() => {
                  setIsCalibModalOpen(false);
                  setCalibPoints([]);
                }}
                className="text-slate-400 hover:text-white cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs">
              <p className="text-slate-300">
                You selected two reference points across the inspection field. Enter the known physical distance between these points to calibrate all pixel measurements.
              </p>

              <div>
                <label className="block text-slate-400 mb-1 font-bold">KNOWN REFERENCE DISTANCE</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={calibDistanceInput}
                    onChange={(e) => setCalibDistanceInput(e.target.value)}
                    placeholder="e.g. 50.0"
                    className="flex-1 bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white font-mono text-sm focus:border-amber-400 focus:outline-hidden"
                  />
                  <div className="flex bg-slate-950 rounded border border-slate-700 p-0.5">
                    <button
                      type="button"
                      onClick={() => setCalibUnit('mm')}
                      className={`px-3 py-1 rounded font-bold cursor-pointer ${
                        calibUnit === 'mm' ? 'bg-amber-500 text-slate-950' : 'text-slate-400'
                      }`}
                    >
                      mm
                    </button>
                    <button
                      type="button"
                      onClick={() => setCalibUnit('in')}
                      className={`px-3 py-1 rounded font-bold cursor-pointer ${
                        calibUnit === 'in' ? 'bg-amber-500 text-slate-950' : 'text-slate-400'
                      }`}
                    >
                      in
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-slate-950 p-2.5 rounded border border-slate-800 text-[11px] text-slate-400 space-y-1">
                <div>Standard targets:</div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setCalibDistanceInput('50.0');
                      setCalibUnit('mm');
                    }}
                    className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded cursor-pointer"
                  >
                    50 mm (Card Width)
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setCalibDistanceInput('100.0');
                      setCalibUnit('mm');
                    }}
                    className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded cursor-pointer"
                  >
                    100 mm (Pocket Rule)
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setCalibDistanceInput('1.0');
                      setCalibUnit('in');
                    }}
                    className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded cursor-pointer"
                  >
                    1.0 inch
                  </button>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => {
                  setIsCalibModalOpen(false);
                  setCalibPoints([]);
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={applyTwoPointCalibration}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded text-xs font-black flex items-center gap-1.5 shadow-md cursor-pointer"
              >
                <Check className="h-4 w-4" />
                <span>Apply Calibration</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImagePreview;
