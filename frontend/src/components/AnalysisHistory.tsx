import { useState, useEffect, useCallback, useMemo } from 'react';
import { AnalysisHistoryItem } from '../types/analysis';
import { 
  FileSpreadsheet, 
  Trash2, 
  X, 
  Download, 
  Search, 
  ChevronRight,
  ClipboardList
} from 'lucide-react';
import SeverityBadge from './SeverityBadge';

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

  const loadHistory = useCallback(() => {
    try {
      const saved = localStorage.getItem('crackvision-history');
      if (saved) {
        const parsed = JSON.parse(saved);
        const valid = parsed.filter(
          (item: any) => item.analysis_id && item.status && typeof item.confidence === 'number'
        );
        setHistory(valid);
      } else {
        setHistory([]);
      }
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = (id: string) => {
    const updated = history.filter((item) => item.analysis_id !== id);
    setHistory(updated);
    localStorage.setItem('crackvision-history', JSON.stringify(updated));
  };

  const handleClear = () => {
    setHistory([]);
    localStorage.removeItem('crackvision-history');
    setShowClearConfirm(false);
  };

  const handleExportCsv = () => {
    if (history.length === 0) return;
    const headers = ['Report_ID', 'Distress_Type', 'Severity', 'Aperture_Width', 'Surface_Area', 'Confidence_Pct', 'Timestamp'];
    const rows = history.map((item) => [
      item.analysis_id,
      `"${item.crack_type}"`,
      item.severity,
      `"${item.estimated_width}"`,
      `"${item.affected_area}"`,
      item.confidence.toFixed(1),
      item.created_at,
    ]);
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
            <h3 className="text-base font-bold text-slate-900 font-sans uppercase tracking-tight">
              Field Asset Survey Logbook
            </h3>
            <p className="text-xs text-slate-600 font-mono">
              {history.length} documented inspection records in local terminal storage
            </p>
          </div>
        </div>

        {history.length > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCsv}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-mono font-bold rounded border border-slate-300 transition-colors"
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
                  className="px-2 py-0.5 bg-rose-600 text-white rounded text-[10px] font-bold"
                >
                  Confirm
                </button>
                <button
                  onClick={() => setShowClearConfirm(false)}
                  className="px-2 py-0.5 bg-slate-200 text-slate-800 rounded text-[10px]"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowClearConfirm(true)}
                className="px-2.5 py-1.5 text-slate-500 hover:text-rose-700 hover:bg-rose-50 rounded text-xs font-mono transition-colors"
                title="Purge survey records"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {history.length > 0 && (
        /* Filters and Search Bar */
        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Report ID or Defect Type..."
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
                className={`px-3 py-1 rounded text-xs font-bold capitalize transition-all ${
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
          <div className="text-center py-8 border border-dashed border-slate-300 rounded-lg bg-slate-50 text-slate-500 text-xs">
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
                    </div>

                    <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[11px] font-mono text-slate-600">
                      <span>ID: <strong className="text-slate-800">{item.analysis_id}</strong></span>
                      <span>Width: <strong className="text-slate-900">{item.estimated_width}</strong></span>
                      <span>Area: <strong className="text-slate-900">{item.affected_area}</strong></span>
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(item.analysis_id);
                    }}
                    className="p-1 rounded text-slate-400 hover:text-rose-600 transition-colors"
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
