export interface AnalysisResult {
  analysis_id: string;
  status: 'crack_detected' | 'no_significant_crack';
  confidence: number; // percentage 0-100
  crack_type: string;
  severity: 'low' | 'medium' | 'high';
  estimated_width: string; // e.g., "0.3 - 0.7 mm"
  affected_area: string; // e.g., "4.8%"
  recommendation: string;
  inspection_note: string;
  annotated_image_note: string;
  created_at: string; // ISO timestamp
}

export interface AnalysisHistoryItem extends AnalysisResult {
  thumbnail: string; // base64 or URL
}
