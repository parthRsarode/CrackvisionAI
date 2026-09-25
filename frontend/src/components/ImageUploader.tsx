import { useState, useRef } from 'react';
import { Upload, XCircle, AlertTriangle, FileImage, Check, Crosshair, MapPin, Compass } from 'lucide-react';
import { SAMPLE_IMAGES, SampleImage } from '../data/sampleImages';

interface ImageUploaderProps {
  onAnalyze: (file: File) => Promise<void>;
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

  // Field Asset Metadata State
  const [assetType, setAssetType] = useState('Bridge Pier / Abutment');
  const [exposureCondition, setExposureCondition] = useState('Humidity, moist air, soil contact (ACI max 0.30 mm)');
  const [stationId, setStationId] = useState('STN-BR-04');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSizeInBytes = 15 * 1024 * 1024; // 15MB

  const handleFile = (newFile: File) => {
    if (!validTypes.includes(newFile.type)) {
      setError('Unsupported file type. Please upload a standard field photo (JPG, PNG, or WEBP).');
      return;
    }
    if (newFile.size > maxSizeInBytes) {
      setError(`File size exceeds 15MB field limit.`);
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
    try {
      await onAnalyze(file);
    } catch (err: any) {
      setError(err.message || 'Inspection analysis failed. Ensure the local vision server is active.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="cad-panel rounded-xl border border-slate-300 shadow-md p-6 bg-white mb-8">
      {/* Field Inspection Asset Form */}
      <div className="mb-6 pb-5 border-b border-slate-200">
        <div className="flex items-center gap-2 mb-3">
          <Compass className="h-4 w-4 text-safetyOrange" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 font-mono">
            Field Inspection Survey Configuration
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          {/* Asset Category */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              Structure Component
            </label>
            <select
              value={assetType}
              onChange={(e) => setAssetType(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md p-2 text-slate-900 focus:border-safetyOrange focus:outline-none"
            >
              <option>Bridge Pier / Abutment</option>
              <option>Prestressed / RC Girder</option>
              <option>Suspended Deck Slab</option>
              <option>Concrete Retaining Wall</option>
              <option>Highway Rigid Pavement</option>
              <option>Foundation Footing</option>
            </select>
          </div>

          {/* ACI 224R Exposure */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              ACI 224R Exposure Environment
            </label>
            <select
              value={exposureCondition}
              onChange={(e) => setExposureCondition(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md p-2 text-slate-900 focus:border-safetyOrange focus:outline-none"
            >
              <option>Humidity, moist air, soil contact (ACI max 0.30 mm)</option>
              <option>Dry air or protective membrane (ACI max 0.41 mm)</option>
              <option>Deicing chemicals / industrial (ACI max 0.18 mm)</option>
              <option>Seawater spray splash zone (ACI max 0.15 mm)</option>
              <option>Water-retaining containment (ACI max 0.10 mm)</option>
            </select>
          </div>

          {/* Station / Chainage */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1 font-mono uppercase">
              Station / Chainage ID
            </label>
            <input
              type="text"
              value={stationId}
              onChange={(e) => setStationId(e.target.value)}
              placeholder="e.g., CH 14+250 or PIER-02"
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md p-2 text-slate-900 font-mono focus:border-safetyOrange focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* CAD Inspection Dropzone */}
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
              {/* Drafting crosshairs corner markers */}
              <div className="absolute top-2 left-2 z-10 bg-slate-900/80 text-white font-mono text-[10px] px-2 py-0.5 rounded flex items-center gap-1">
                <Crosshair className="h-3 w-3 text-safetyOrange" />
                <span>SURFACE VIEW: {assetType}</span>
              </div>

              <img
                src={previewUrl}
                alt="Selected structural surface"
                className="w-full max-h-[360px] object-contain mx-auto"
              />

              <button
                onClick={handleRemove}
                className="absolute top-2 right-2 bg-slate-900/80 hover:bg-rose-600 text-white p-1.5 rounded-full transition-colors"
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
                Size: {(file.size / 1024).toFixed(0)} KB
              </span>
              <span className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-300 rounded flex items-center gap-1 font-bold">
                <Check className="h-3.5 w-3.5" /> Ready for Optical Measurement
              </span>
            </div>

            {/* Run Analysis Action Button */}
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="bg-safetyOrange hover:bg-orange-600 text-white font-bold text-sm py-3 px-8 rounded-lg shadow-sm transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  <span>Computing Aperture Widths & Defect Geometry...</span>
                </>
              ) : (
                <>
                  <Crosshair className="h-4 w-4" />
                  <span>Execute Structural Condition Assessment</span>
                </>
              )}
            </button>
          </div>
        ) : (
          /* Empty CAD Dropzone */
          <div className="flex flex-col items-center py-6">
            <div className="w-12 h-12 rounded-lg bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-600 mb-3">
              <Upload className="h-6 w-6 text-safetyOrange" />
            </div>

            <h4 className="text-base font-bold text-slate-900 mb-1 font-sans">
              Select or Drop Concrete Surface Photo
            </h4>
            <p className="text-xs text-slate-600 max-w-md mx-auto mb-4 font-sans">
              Position high-resolution orthographic surface photo perpendicular to plane of defect (JPG, PNG, or WEBP up to 15MB)
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              className="hidden"
              onChange={handleFileSelect}
            />

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs py-2 px-5 rounded-md shadow-xs transition-colors"
            >
              Browse Local Inspection Files
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-rose-50 border border-rose-300 text-rose-800 text-xs rounded-lg flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
