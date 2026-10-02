import { useState, useCallback, useRef } from 'react';
import { AnalysisResult, BatchAnalysisResponse } from '../types/analysis';
import {
  Navbar,
  Hero,
  ImageUploader,
  AnalysisLoader,
  AnalysisResults,
  BatchAnalysisView,
  AnalysisHistory,
  Footer,
  HowItWorksModal,
  AboutModal
} from '../components';
import { analyzeImage, analyzeBatchImages, AnalysisMetadata } from '../services/api';
import { SampleImage } from '../data/sampleImages';

const Dashboard: React.FC = () => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [batchResponse, setBatchResponse] = useState<BatchAnalysisResponse | null>(null);
  const [batchThumbnails, setBatchThumbnails] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [presetFile, setPresetFile] = useState<File | null>(null);

  // Modals state
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  const uploadSectionRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = useCallback(async (file: File, metadata?: AnalysisMetadata) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeImage(file, metadata);
      const thumbnail = URL.createObjectURL(file);

      const enhancedResult: AnalysisResult & { thumbnail: string } = {
        ...result,
        thumbnail,
      };

      saveToHistory(enhancedResult);

      setBatchResponse(null);
      setAnalysis(result);
      setImageUrl(thumbnail);

      setTimeout(() => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      setError(err.message || 'Vision inspection failed. Ensure local API service is active on port 8000.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleBatchAnalyze = useCallback(async (files: File[], metadata?: AnalysisMetadata) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await analyzeBatchImages(files, metadata);
      const thumbs = files.map((f) => URL.createObjectURL(f));
      setBatchThumbnails(thumbs);
      setBatchResponse(response);
      setAnalysis(null);
      setImageUrl(null);

      // Save each batch result to local history cache
      response.results.forEach((res, i) => {
        saveToHistory({ ...res, thumbnail: thumbs[i] || '' });
      });

      setTimeout(() => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      setError(err.message || 'Batch survey inspection failed.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSampleSelect = async (sample: SampleImage) => {
    try {
      const file = await sample.createFile();
      setPresetFile(file);
      await handleAnalyze(file);
    } catch (err: any) {
      setError('Could not process benchmark sample: ' + err.message);
    }
  };

  const handleRemoveImage = useCallback(() => {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    batchThumbnails.forEach((t) => URL.revokeObjectURL(t));
    setImageUrl(null);
    setAnalysis(null);
    setBatchResponse(null);
    setBatchThumbnails([]);
    setPresetFile(null);
  }, [imageUrl, batchThumbnails]);

  const saveToHistory = (item: AnalysisResult & { thumbnail: string }) => {
    try {
      const saved = localStorage.getItem('crackvision-history');
      const history = saved ? JSON.parse(saved) : [];
      history.unshift(item);
      const limitedHistory = history.slice(0, 50);
      localStorage.setItem('crackvision-history', JSON.stringify(limitedHistory));
    } catch (err) {
      console.error('Failed to save to history:', err);
    }
  };

  const handleHistoryItemClick = (item: AnalysisResult & { thumbnail: string }) => {
    setAnalysis(item);
    setImageUrl(item.thumbnail);
    window.scrollTo({ top: 100, behavior: 'smooth' });
  };

  const scrollToUpload = () => {
    if (analysis) {
      handleRemoveImage();
    }
    uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-cad-grid text-slate-900 flex flex-col font-sans selection:bg-safetyOrange selection:text-white relative overflow-hidden">
      <div className="ambient-glow"></div>
      
      {/* Top Header */}
      <Navbar
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
        onOpenAbout={() => setIsAboutOpen(true)}
        onHomeClick={() => {
          handleRemoveImage();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
      />

      {/* Main Terminal Container */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-4 relative z-10">
        {/* Field Scope / Hero */}
        <Hero 
          onUploadClick={scrollToUpload} 
          onSelectSample={handleSampleSelect}
        />

        {/* Global Error Banner */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-rose-50 border border-rose-300 text-rose-800 text-xs font-mono flex items-center justify-between shadow-xs">
            <span>ERROR: {error}</span>
            <button 
              onClick={() => setError(null)} 
              className="text-xs font-bold text-rose-700 hover:text-rose-900 ml-4 underline cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Diagnostic Processor */}
        {isLoading && (
          <div className="py-6">
            <AnalysisLoader />
          </div>
        )}

        {/* CAD Dropzone (Visible when ready for new survey) */}
        {!isLoading && !analysis && !batchResponse && (
          <div ref={uploadSectionRef} className="py-2 scroll-mt-20 animate-enter stagger-5">
            <ImageUploader
              onAnalyze={handleAnalyze}
              onBatchAnalyze={handleBatchAnalyze}
              onRemove={handleRemoveImage}
              presetFile={presetFile}
            />
          </div>
        )}

        {/* Multi-Image Batch Summary View (Phase 05 REQ-4.4) */}
        {!isLoading && batchResponse && !analysis && (
          <div className="py-4">
            <BatchAnalysisView
              summary={batchResponse.summary}
              results={batchResponse.results}
              thumbnails={batchThumbnails}
              onSelectResult={(result, thumb) => {
                setAnalysis(result);
                setImageUrl(thumb);
                window.scrollTo({ top: 120, behavior: 'smooth' });
              }}
              onReset={handleRemoveImage}
            />
          </div>
        )}

        {/* SCAR Condition Report View */}
        {!isLoading && analysis && imageUrl && (
          <div className="py-4">
            {batchResponse && (
              <div className="mb-4">
                <button
                  onClick={() => {
                    setAnalysis(null);
                    setImageUrl(null);
                  }}
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-amber-400 font-mono text-xs font-bold rounded flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <span>← Back to Aggregated Batch Survey ({batchResponse.results.length} Elements)</span>
                </button>
              </div>
            )}
            <AnalysisResults
              analysis={analysis}
              imageUrl={imageUrl}
              onReset={handleRemoveImage}
              onUpdateAnalysis={(updated) => {
                setAnalysis(updated);
                saveToHistory({ ...updated, thumbnail: imageUrl });
              }}
            />
          </div>
        )}

        {/* Field Survey Logbook */}
        <div className="py-6">
          <AnalysisHistory
            onHistoryItemClick={handleHistoryItemClick}
            onHistoryDelete={() => {}}
            onHistoryClear={() => {}}
          />
        </div>
      </main>

      {/* Standards & Specs Footer */}
      <Footer />

      {/* Reference Modals */}
      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />
      <AboutModal
        isOpen={isAboutOpen}
        onClose={() => setIsAboutOpen(false)}
      />
    </div>
  );
};

export default Dashboard;
