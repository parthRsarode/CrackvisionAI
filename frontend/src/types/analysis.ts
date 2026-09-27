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

  // Phase 03 Computer Vision Segmentation fields
  has_segmentation?: boolean;
  polygons?: number[][][]; // [ [ [x, y], ... ] ]
  normalized_polygons?: number[][][]; // [ [ [x_norm, y_norm], ... ] ]
  bounding_boxes?: number[][]; // [ [x1, y1, x2, y2], ... ]
  defect_count?: number;
  inference_time_ms?: number;
  aci_compliance?: {
    water_retaining: boolean;
    deicing_marine: boolean;
    humidity_soil: boolean;
    dry_air_protected: boolean;
  };
}

export interface AnalysisHistoryItem extends AnalysisResult {
  thumbnail: string; // base64 or URL
}
