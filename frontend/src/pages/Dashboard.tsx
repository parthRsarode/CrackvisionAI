import { useState, useCallback, useRef } from 'react';
import { AnalysisResult } from '../types/analysis';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import ImageUploader from '../components/ImageUploader';
import AnalysisLoader from '../components/AnalysisLoader';
import AnalysisResults from '../components/AnalysisResults';
import AnalysisHistory from '../components/AnalysisHistory';
import Footer from '../components/Footer';
import HowItWorksModal from '../components/HowItWorksModal';
import AboutModal from '../components/AboutModal';
import { analyzeImage } from '../services/api';
import { SampleImage } from '../data/sampleImages';

const Dashboard: React.FC = () => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [presetFile, setPresetFile] = useState<File | null>(null);

  // Modals state
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  const uploadSectionRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeImage(file);
      const thumbnail = URL.createObjectURL(file);

      const enhancedResult: AnalysisResult & { thumbnail: string } = {
        ...result,
        thumbnail,
      };

      saveToHistory(enhancedResult);

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
    setImageUrl(null);
    setAnalysis(null);
    setPresetFile(null);
  }, [imageUrl]);

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
    setAnalysis({
      analysis_id: item.analysis_id,
      status: item.status,
      confidence: item.confidence,
      crack_type: item.crack_type,
      severity: item.severity,
      estimated_width: item.estimated_width,
      affected_area: item.affected_area,
      recommendation: item.recommendation,
      inspection_note: item.inspection_note,
      annotated_image_note: item.annotated_image_note,
      created_at: item.created_at,
    });
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
    <div className="min-h-screen bg-cad-grid text-slate-900 flex flex-col font-sans selection:bg-safetyOrange selection:text-white">
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
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-4">
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
              className="text-xs font-bold text-rose-700 hover:text-rose-900 ml-4 underline"
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
        {!isLoading && !analysis && (
          <div ref={uploadSectionRef} className="py-2 scroll-mt-20">
            <ImageUploader
              onAnalyze={handleAnalyze}
              onRemove={handleRemoveImage}
              presetFile={presetFile}
            />
          </div>
        )}

        {/* SCAR Condition Report View */}
        {!isLoading && analysis && imageUrl && (
          <div className="py-4">
            <AnalysisResults
              analysis={analysis}
              imageUrl={imageUrl}
              onReset={handleRemoveImage}
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
