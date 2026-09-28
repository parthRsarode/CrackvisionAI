import { useState, useRef } from 'react';
import { Upload, XCircle, AlertTriangle, Check, Crosshair, MapPin, Sliders, Edit3, ShieldAlert, Layers, Activity, BookOpen } from 'lucide-react';
import { SAMPLE_IMAGES, SampleImage } from '../data/sampleImages';
import { AnalysisMetadata } from '../services/api';

interface ImageUploaderProps {
  onAnalyze: (file: File, metadata?: AnalysisMetadata) => Promise<void>;
  onRemove: () => void;
  presetFile?: File | null;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onAnalyze, onRemove, presetFile }) => {
  const [file, setFile] = useState<File | null>(presetFile || null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(
    presetFile ? URL.createObjectURL(presetFile) : null
  );
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // User-Friendly & Engineering Context State
  const [componentSelect, setComponentSelect] = useState('Floor / Ceiling / Concrete Slab');
  const [customComponent, setCustomComponent] = useState('');
  
  const [environmentSelect, setEnvironmentSelect] = useState('Normal Indoor / Outdoor Surface (Standard)');
  const [customEnvironment, setCustomEnvironment] = useState('');

  const [locationNote, setLocationNote] = useState('');

  // Enhanced Engineering Parameters
  const [elementCriticality, setElementCriticality] = useState('primary');
  const [proximityToSupports, setProximityToSupports] = useState('near_support');
  const [visibleSpalling, setVisibleSpalling] = useState(false);
  const [visibleCorrosion, setVisibleCorrosion] = useState(false);
  const [crackDepthStatus, setCrackDepthStatus] = useState('unknown');
  const [previousWidthMm, setPreviousWidthMm] = useState<string>('');
  
  // Multi-Standard Code Selector (ACI, Eurocode 2, IS 456, BS 8110)
  const [standardCode, setStandardCode] = useState('ACI');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSizeInBytes = 15 * 1024 * 1024; // 15MB

  const effectiveComponent = componentSelect === 'custom' 
    ? (customComponent.trim() || 'Custom Surface')
    : componentSelect;

  const effectiveEnvironment = environmentSelect === 'custom'
    ? (customEnvironment.trim() || 'Custom Environment')
    : environmentSelect;

  const handleFile = (newFile: File) => {
    if (!validTypes.includes(newFile.type)) {
      setError('Unsupported file format. Please upload a standard photo (JPG, PNG, or WEBP).');
      return;
    }
    if (newFile.size > maxSizeInBytes) {
      setError(`File size exceeds 15MB limit.`);
      return;
    }
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setError(null);
    setFile(newFile);
    setPreviewUrl(URL.createObjectURL(newFile));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
    e.target.value = '';
  };

  const handleDropEvent = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemove = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl(null);
    setError(null);
    onRemove();
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);

    const prevWidthNum = previousWidthMm.trim() ? parseFloat(previousWidthMm) : null;

    const metadata: AnalysisMetadata = {
      memberType: effectiveComponent,
      environment: effectiveEnvironment,
      elementCriticality,
      proximityToSupports,
      visibleSpalling,
      visibleCorrosion,
      crackDepthStatus,
      previousWidthMm: prevWidthNum && !isNaN(prevWidthNum) ? prevWidthNum : null,
      standardCode
    };

    try {
      await onAnalyze(file, metadata);
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Ensure the AI vision server is active.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="cad-panel rounded-xl border border-slate-300 shadow-md p-6 bg-white mb-8">
      {/* Structural Context Form */}
      <div className="mb-6 pb-5 border-b border-slate-200">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <Sliders className="h-4 w-4 text-safetyOrange" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 font-mono">
              Structural Context & Multi-Factor Parameters
            </h3>
          </div>
          <span className="text-[11px] text-slate-500 font-sans">
            Refine structural inputs and select regional engineering standard
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3.5 mb-3.5">
          {/* Regional Standard Code Benchmark Selector */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase flex items-center gap-1">
              <BookOpen className="h-3 w-3 text-safetyOrange" />
              <span>Benchmark Standard</span>
            </label>
            <select
              value={standardCode}
              onChange={(e) => setStandardCode(e.target.value)}
              className="w-full text-xs bg-amber-50/70 border border-amber-300 font-bold rounded-md p-2 text-slate-900 focus:border-safetyOrange focus:outline-none font-sans"
            >
              <option value="ACI">ACI 224R / CODE-562 (USA)</option>
              <option value="EUROCODE_2">Eurocode 2 EN 1992 (Europe)</option>
              <option value="IS_456">IS 456:2000 (India)</option>
              <option value="BS_8110">BS 8110 / BS 8500 (UK)</option>
            </select>
          </div>

          {/* 1. Structure / Surface Component */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              Surface / Member Type
            </label>
            <select
              value={componentSelect}
              onChange={(e) => setComponentSelect(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md p-2 text-slate-900 focus:border-safetyOrange focus:outline-none font-sans"
            >
              <option value="Floor / Ceiling / Concrete Slab">Floor / Ceiling / Concrete Slab</option>
              <option value="Pillar / Column / Support">Pillar / Column / Support</option>
              <option value="Structural Beam / Girder">Structural Beam / Girder</option>
              <option value="Wall / Plaster / Drywall">Wall / Plaster / Drywall</option>
              <option value="Bridge Abutment / Retaining Wall">Bridge Abutment / Retaining Wall</option>
              <option value="Driveway / Road / Asphalt">Driveway / Road / Asphalt</option>
              <option value="custom">✏️ Other - Type My Own...</option>
            </select>

            {componentSelect === 'custom' && (
              <div className="mt-2 relative">
                <input
                  type="text"
                  value={customComponent}
                  onChange={(e) => setCustomComponent(e.target.value)}
                  placeholder="Enter custom member name..."
                  className="w-full text-xs bg-amber-50/60 border border-safetyOrange rounded-md pl-7 pr-2 py-1.5 text-slate-900 focus:outline-none font-sans"
                />
                <Edit3 className="h-3.5 w-3.5 text-safetyOrange absolute left-2 top-2" />
              </div>
            )}
          </div>

          {/* 2. Environment / Exposure */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              Environment / Exposure
            </label>
            <select
              value={environmentSelect}
              onChange={(e) => setEnvironmentSelect(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md p-2 text-slate-900 focus:border-safetyOrange focus:outline-none font-sans"
            >
              <option value="Normal Indoor / Outdoor Surface (Standard)">Normal Indoor / Outdoor (Standard)</option>
              <option value="Humid / Moisture / Soil Contact">Humid / Moisture / Soil Contact</option>
              <option value="Severe (Deicing Salts / Marine Splash)">Severe (Salt / Marine Splash)</option>
              <option value="custom">✏️ Other - Type My Own...</option>
            </select>

            {environmentSelect === 'custom' && (
              <div className="mt-2 relative">
                <input
                  type="text"
                  value={customEnvironment}
                  onChange={(e) => setCustomEnvironment(e.target.value)}
                  placeholder="Describe environment..."
                  className="w-full text-xs bg-amber-50/60 border border-safetyOrange rounded-md pl-7 pr-2 py-1.5 text-slate-900 focus:outline-none font-sans"
                />
                <Edit3 className="h-3.5 w-3.5 text-safetyOrange absolute left-2 top-2" />
              </div>
            )}
          </div>

          {/* 3. Photo Location Note */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              Location / Asset Tag <span className="text-slate-400 font-normal lowercase">(optional)</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={locationNote}
                onChange={(e) => setLocationNote(e.target.value)}
                placeholder="e.g. Beam B-12 Near Support A"
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md pl-7 pr-2 py-2 text-slate-900 font-sans focus:border-safetyOrange focus:outline-none"
              />
              <MapPin className="h-3.5 w-3.5 text-slate-400 absolute left-2 top-2.5" />
            </div>
          </div>
        </div>

        {/* Section 1-4 Additional Engineering Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-slate-50/80 p-3 rounded-lg border border-slate-200 text-xs font-sans">
          <div>
            <label className="block text-[10px] font-bold uppercase text-slate-600 font-mono mb-1">
              Element Criticality
            </label>
            <select
              value={elementCriticality}
              onChange={(e) => setElementCriticality(e.target.value)}
              className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-800"
            >
              <option value="primary">Primary Load-Bearing</option>
              <option value="secondary">Secondary / Non-Structural</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold uppercase text-slate-600 font-mono mb-1">
              Proximity to Support
            </label>
            <select
              value={proximityToSupports}
              onChange={(e) => setProximityToSupports(e.target.value)}
              className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-800"
            >
              <option value="near_support">Near Support / Connection</option>
              <option value="mid_span">Mid-Span Region</option>
              <option value="opening">Near Opening / Cutout</option>
              <option value="unspecified">Unspecified Location</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold uppercase text-slate-600 font-mono mb-1">
              Depth Condition
            </label>
            <select
              value={crackDepthStatus}
              onChange={(e) => setCrackDepthStatus(e.target.value)}
              className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-800 font-semibold"
            >
              <option value="unknown">Unknown (2D RGB Surface Only)</option>
              <option value="measured_externally">Measured Externally (NDT)</option>
              <option value="further_investigation_required">Investigation Required</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold uppercase text-slate-600 font-mono mb-1">
              Previous Inspection (mm)
            </label>
            <input
              type="number"
              step="0.05"
              value={previousWidthMm}
              onChange={(e) => setPreviousWidthMm(e.target.value)}
              placeholder="e.g. 0.35"
              className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-800"
            />
          </div>

          <div className="sm:col-span-4 flex flex-wrap items-center gap-4 pt-1">
            <label className="inline-flex items-center gap-1.5 text-xs text-slate-800 cursor-pointer font-medium">
              <input
                type="checkbox"
                checked={visibleSpalling}
                onChange={(e) => setVisibleSpalling(e.target.checked)}
                className="rounded text-safetyOrange focus:ring-safetyOrange"
              />
              <span>Visible Concrete Spalling / Flaking</span>
            </label>

            <label className="inline-flex items-center gap-1.5 text-xs text-slate-800 cursor-pointer font-medium">
              <input
                type="checkbox"
                checked={visibleCorrosion}
                onChange={(e) => setVisibleCorrosion(e.target.checked)}
                className="rounded text-safetyOrange focus:ring-safetyOrange"
              />
              <span>Visible Rust / Corrosion Indicators</span>
            </label>
          </div>
        </div>
      </div>

      {/* Inspection Dropzone */}
      <div
        onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); }}
        onDragEnter={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); }}
        onDrop={handleDropEvent}
        className={`relative border-2 rounded-lg p-6 sm:p-8 text-center transition-all ${
          isDragging 
            ? 'border-safetyOrange bg-amber-50/70' 
            : file 
            ? 'border-slate-300 bg-slate-50' 
            : 'border-dashed border-slate-300 hover:border-slate-400 bg-slate-50/50'
        }`}
      >
        {file && previewUrl ? (
          /* Preview State */
          <div className="flex flex-col items-center">
            <div className="relative mb-4 max-w-lg w-full group border border-slate-300 rounded-lg overflow-hidden bg-white shadow-sm">
              <div className="absolute top-2 left-2 z-10 bg-slate-900/80 text-white font-mono text-[10px] px-2 py-0.5 rounded flex items-center gap-1">
                <Crosshair className="h-3 w-3 text-safetyOrange" />
                <span>SURFACE: {effectiveComponent} ({standardCode})</span>
              </div>

              <img
                src={previewUrl}
                alt="Selected surface"
                className="w-full max-h-[360px] object-contain mx-auto"
              />

              <button
                onClick={handleRemove}
                className="absolute top-2 right-2 bg-slate-900/80 hover:bg-rose-600 text-white p-1.5 rounded-full transition-colors cursor-pointer"
                title="Discard image"
              >
                <XCircle className="h-4 w-4" />
              </button>
            </div>

            {/* Field Metadata Chips */}
            <div className="flex flex-wrap items-center justify-center gap-2 mb-5 text-xs font-mono text-slate-700">
              <span className="px-2.5 py-1 bg-white border border-slate-300 rounded shadow-xs">
                File: {file.name}
              </span>
              <span className="px-2.5 py-1 bg-white border border-slate-300 rounded shadow-xs">
                Standard: {standardCode}
              </span>
              {locationNote && (
                <span className="px-2.5 py-1 bg-amber-50 text-amber-900 border border-amber-300 rounded font-sans">
                  Location: {locationNote}
                </span>
              )}
              <span className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-300 rounded flex items-center gap-1 font-bold">
                <Check className="h-3.5 w-3.5" /> Ready for Scan
              </span>
            </div>

            {/* Run Analysis Action Button */}
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="bg-safetyOrange hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-md shadow-md transition-colors flex items-center gap-2.5 text-sm uppercase tracking-wider font-mono disabled:opacity-50 cursor-pointer"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Executing YOLO Multi-Factor Assessment...</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  <span>Execute Structural Condition Assessment</span>
                </>
              )}
            </button>
          </div>
        ) : (
          /* Empty Dropzone State */
          <div>
            <div className="w-12 h-12 rounded-full bg-amber-100 text-safetyOrange flex items-center justify-center mx-auto mb-3">
              <Upload className="h-6 w-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-900 font-mono uppercase mb-1">
              Upload Concrete or Asphalt Inspection Image
            </h4>
            <p className="text-xs text-slate-600 mb-4 max-w-md mx-auto font-sans">
              Drag & drop a high-resolution photo or select a sample benchmark file below (JPG, PNG, WEBP up to 15MB).
            </p>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold font-mono py-2 px-4 rounded border border-slate-700 transition-colors cursor-pointer"
            >
              Select Image File
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Benchmark Samples */}
            <div className="mt-6 pt-5 border-t border-slate-200">
              <span className="text-[11px] font-mono font-bold text-slate-500 uppercase block mb-2.5">
                Or choose a preset benchmark case:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 max-w-2xl mx-auto">
                {SAMPLE_IMAGES.map((sample) => (
                  <button
                    key={sample.id}
                    onClick={async () => {
                      try {
                        const res = await fetch(sample.url);
                        const blob = await res.blob();
                        const sampleFile = new File([blob], `${sample.id}.jpg`, { type: 'image/jpeg' });
                        handleFile(sampleFile);
                      } catch (err) {
                        setError('Failed to load benchmark sample.');
                      }
                    }}
                    className="p-2 border border-slate-200 hover:border-safetyOrange bg-white rounded text-left transition-all hover:shadow-xs group cursor-pointer"
                  >
                    <div className="aspect-video bg-slate-100 rounded mb-1.5 overflow-hidden">
                      <img src={sample.url} alt={sample.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                    </div>
                    <p className="text-[11px] font-bold text-slate-800 truncate font-mono">{sample.title}</p>
                    <p className="text-[9px] text-slate-500 font-sans">{sample.severity.toUpperCase()} Distress</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-rose-50 border border-rose-300 rounded text-rose-800 text-xs flex items-center justify-center gap-2">
            <AlertTriangle className="h-4 w-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUploader;
