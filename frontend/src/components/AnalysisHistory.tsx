import { useState, useEffect, useCallback, useMemo } from 'react';
import { AnalysisHistoryItem, AnalysisResult } from '../types/analysis';
import { 
  FileSpreadsheet, 
  Trash2, 
  X, 
  Download, 
  Search, 
  ChevronRight,
  ClipboardList,
  Database,
  RefreshCw,
  FileCheck,
  CheckCircle2
} from 'lucide-react';
import SeverityBadge from './SeverityBadge';
import { 
  fetchSurveys, 
  deleteSurveyRecord, 
  downloadSurveyPDF, 
  exportDirectPDF 
} from '../services/api';

interface AnalysisHistoryProps {
  onHistoryItemClick: (item: AnalysisHistoryItem) => void;
  onHistoryDelete: (id: string) => void;
  onHistoryClear: () => void;
}

const AnalysisHistory: React.FC<AnalysisHistoryProps> = ({ onHistoryItemClick }) => {
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isDbConnected, setIsDbConnected] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    setIsSyncing(true);

    // 1. Read local storage cache
    let localItems: AnalysisHistoryItem[] = [];
    try {
      const saved = localStorage.getItem('crackvision-history');
      if (saved) {
        const parsed = JSON.parse(saved);
        localItems = parsed.filter(
          (item: any) => item.analysis_id && item.status && typeof item.confidence === 'number'
        );
      }
    } catch {
      localItems = [];
    }

    // 2. Fetch from SQLite backend database
    try {
      const backendSurveys = await fetchSurveys();
      setIsDbConnected(true);

      // Merge: create lookup by analysis_id
      const itemMap = new Map<string, AnalysisHistoryItem>();

      // Put backend surveys into map
      backendSurveys.forEach((b: any) => {
        const id = b.survey_id || b.analysis_id;
        itemMap.set(id, {
          ...b,
          analysis_id: id,
          thumbnail: b.thumbnail || '',
        });
      });

      // Overlay local items (which might have client-side thumbnails)
      localItems.forEach((l) => {
        const existing = itemMap.get(l.analysis_id);
        if (existing) {
          itemMap.set(l.analysis_id, {
            ...existing,
            thumbnail: l.thumbnail || existing.thumbnail || '',
          });
        } else {
          itemMap.set(l.analysis_id, l);
        }
      });

      const merged = Array.from(itemMap.values()).sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

      setHistory(merged);
      localStorage.setItem('crackvision-history', JSON.stringify(merged.slice(0, 50)));
    } catch {
      // Backend unavailable; use local cache
      setIsDbConnected(false);
      setHistory(localItems);
    } finally {
      setIsSyncing(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = async (id: string) => {
    // Optimistic UI update
    const updated = history.filter((item) => item.analysis_id !== id);
    setHistory(updated);
    localStorage.setItem('crackvision-history', JSON.stringify(updated));

    // Try deleting from backend SQLite DB
    try {
      await deleteSurveyRecord(id);
    } catch (e) {
      // Ignore if it only existed locally
    }
  };

  const handleClear = () => {
    setHistory([]);
    localStorage.removeItem('crackvision-history');
    setShowClearConfirm(false);
  };

  const handleDownloadPDF = async (item: AnalysisHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setDownloadingId(item.analysis_id);
    try {
      // First try downloading by survey ID from backend DB
      try {
        await downloadSurveyPDF(item.analysis_id);
      } catch {
        // Fallback to direct export using the client item data
        await exportDirectPDF(item);
      }
    } catch (err: any) {
      alert(`Could not compile SCAR PDF: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleExportCsv = () => {
    if (history.length === 0) return;
    const headers = [
      'Report_ID', 
      'Building_Name',
      'Building_Type',
      'Construction_Year',
      'Age_At_Inspection',
      'Age_Verification',
      'Distress_Type', 
      'Severity', 
      'Aperture_Width', 
      'Surface_Area', 
      'Confidence_Pct', 
      'Standard_Code',
      'Environmental_Exposure',
      'Timestamp'
    ];
    const rows = history.map((item) => {
      const bp = item.building_profile;
      return [
        item.analysis_id,
        `"${bp?.building_name || ''}"`,
        `"${bp?.building_type || 'unspecified'}"`,
        bp?.construction_year ?? '',
        bp?.building_age_years ?? '',
        `"${bp?.age_verification || 'unknown'}"`,
        `"${item.crack_type}"`,
        item.severity,
        `"${item.estimated_width}"`,
        `"${item.affected_area}"`,
        item.confidence.toFixed(1),
        item.compliance_details?.standard_code || 'ACI',
        `"${bp?.environmental_exposure || 'indoor_dry'}"`,
        item.created_at,
      ];
    });
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `civil_survey_log_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      const matchesSeverity = filterSeverity === 'all' || item.severity === filterSeverity;
      const matchesSearch =
        searchQuery.trim() === '' ||
        item.crack_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.analysis_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSeverity && matchesSearch;
    });
  }, [history, filterSeverity, searchQuery]);

  return (
    <div className="cad-panel rounded-xl p-6 sm:p-8 border border-slate-300 bg-white shadow-md">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-slate-100 rounded text-slate-800 border border-slate-300">
            <ClipboardList className="h-5 w-5 text-safetyOrange" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900 font-sans uppercase tracking-tight">
                Field Asset Survey Logbook
              </h3>
              <span className={`inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                isDbConnected 
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-300' 
                  : 'bg-slate-100 text-slate-600 border border-slate-300'
              }`}>
                <Database className="h-3 w-3" />
                <span>{isDbConnected ? 'SQLite Live' : 'Local Terminal Cache'}</span>
              </span>
            </div>
            <p className="text-xs text-slate-600 font-mono">
              {history.length} documented structural condition inspection records
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Refresh / DB Sync Button */}
          <button
            onClick={loadHistory}
            disabled={isSyncing}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-mono font-bold rounded border border-slate-300 transition-colors cursor-pointer"
            title="Sync with SQLite backend database"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-safetyOrange ${isSyncing ? 'animate-spin' : ''}`} />
            <span>Sync DB</span>
          </button>

          {history.length > 0 && (
            <>
              <button
                onClick={handleExportCsv}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-mono font-bold rounded border border-slate-300 transition-colors cursor-pointer"
                title="Export inspection data to CSV"
              >
                <Download className="h-3.5 w-3.5 text-safetyOrange" />
                <span>Export CSV</span>
              </button>

              {showClearConfirm ? (
                <div className="flex items-center gap-1.5 bg-rose-50 border border-rose-300 px-2 py-1 rounded text-xs">
                  <span className="text-rose-700 text-[11px] font-mono">Purge log?</span>
                  <button
                    onClick={handleClear}
                    className="px-2 py-0.5 bg-rose-600 text-white rounded text-[10px] font-bold cursor-pointer"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => setShowClearConfirm(false)}
                    className="px-2 py-0.5 bg-slate-200 text-slate-800 rounded text-[10px] cursor-pointer"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowClearConfirm(true)}
                  className="px-2.5 py-1.5 text-slate-500 hover:text-rose-700 hover:bg-rose-50 rounded text-xs font-mono transition-colors cursor-pointer"
                  title="Purge local survey records"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {history.length > 0 && (
        /* Filters and Search Bar */
        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Survey ID or Defect Type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-md pl-9 pr-3 py-1.5 text-xs text-slate-900 font-mono focus:outline-none focus:border-safetyOrange"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-md border border-slate-300 font-mono text-xs">
            {(['all', 'high', 'medium', 'low'] as const).map((s) => (
              <button
                key={s}
                onClick={() => setFilterSeverity(s)}
                className={`px-3 py-1 rounded text-xs font-bold capitalize transition-all cursor-pointer ${
                  filterSeverity === s
                    ? 'bg-civilNavy text-white'
                    : 'text-slate-600 hover:bg-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Log Table / List */}
      <div className="mt-4">
        {history.length === 0 ? (
          <div className="text-center py-8 border border-dashed border-slate-300 rounded-lg bg-slate-50 text-slate-500 text-xs font-mono">
            No field condition records logged yet. Run a surface survey above to generate inspection data.
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-500 font-mono">
            No inspection records match the current filter query.
          </div>
        ) : (
          <div className="space-y-2.5">
            {filteredHistory.map((item) => (
              <div
                key={item.analysis_id}
                onClick={() => onHistoryItemClick(item)}
                className="flex items-center justify-between p-3 rounded-lg border border-slate-300 bg-slate-50/70 hover:bg-amber-50/40 hover:border-safetyOrange cursor-pointer transition-all shadow-2xs group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-12 h-12 rounded border border-slate-300 overflow-hidden bg-white shrink-0">
                    {item.thumbnail ? (
                      <img src={item.thumbnail} alt="Thumbnail" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-400 font-mono text-xs">
                        IMG
                      </div>
                    )}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-bold text-xs font-sans text-slate-900 group-hover:text-safetyOrange transition-colors truncate">
                        {item.crack_type}
                      </span>
                      <SeverityBadge severity={item.severity} />
                      {item.compliance_details?.standard_code && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                          {item.compliance_details.standard_code}
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[11px] font-mono text-slate-600">
                      <span>ID: <strong className="text-slate-800">{item.analysis_id}</strong></span>
                      {item.building_profile?.building_name && (
                        <span>Asset: <strong className="text-slate-900">{item.building_profile.building_name}</strong></span>
                      )}
                      {item.building_profile?.building_age_years !== undefined && item.building_profile?.building_age_years !== null && (
                        <span className="text-cyan-800 font-bold bg-cyan-50 px-1 rounded border border-cyan-200">
                          {item.building_profile.building_age_years} yrs old
                        </span>
                      )}
                      <span>Width: <strong className="text-slate-900">{item.estimated_width}</strong></span>
                      <span>Area: <strong className="text-slate-900">{item.affected_area}</strong></span>
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {/* Download Official SCAR PDF Button (REQ-4.3) */}
                  <button
                    onClick={(e) => handleDownloadPDF(item, e)}
                    disabled={downloadingId === item.analysis_id}
                    className="flex items-center gap-1 px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-800 rounded border border-slate-300 text-xs font-mono font-bold transition-colors cursor-pointer"
                    title="Download Official SCAR PDF Report"
                  >
                    <Download className="h-3.5 w-3.5 text-safetyOrange" />
                    <span>{downloadingId === item.analysis_id ? 'Compiling...' : 'PDF'}</span>
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(item.analysis_id);
                    }}
                    className="p-1 rounded text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                    title="Delete record"
                  >
                    <X className="h-4 w-4" />
                  </button>
                  <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-slate-900" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisHistory;
