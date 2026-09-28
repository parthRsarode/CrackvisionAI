export interface EvidenceSufficiency {
  status: 'sufficient_for_surface_assessment' | 'insufficient_for_engineering_assessment';
  missing_factors: string[];
  summary: string;
}

export interface AssessmentBreakdown {
  observation: string;
  context: string;
  deterioration: string;
  assessment: string;
}

export interface ComplianceDetails {
  status: 'verified' | 'provisionally_consistent' | 'requires_review' | 'potential_non_conformance' | 'not_applicable' | 'unable_to_determine';
  standard_name: string;
  standard_category: 'current_standard' | 'reference_guidance' | 'historical_guidance' | 'superseded_guidance';
  relevant_criterion: string;
  observed_value: string;
  reference_value: string;
  explanation: string;
  missing_information: string;
}

export interface MultiFactorMetrics {
  crack_width_mm: number;
  crack_length_mm: number;
  crack_area_mm2: number;
  crack_density_pct: number;
  crack_count: number;
  crack_pattern: string;
  member_type: string;
  element_criticality: string;
  proximity_to_supports: string;
  visible_spalling: boolean;
  visible_corrosion: boolean;
  historical_progression: string;
}

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

  // Computer Vision Segmentation fields
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

  // Section 1-8 Refined Engineering & Assessment Fields
  crack_depth_status?: string;
  crack_depth_explanation?: string;
  evidence_sufficiency?: EvidenceSufficiency;
  assessment_breakdown?: AssessmentBreakdown;
  compliance_details?: ComplianceDetails;
  plain_language_explanation?: string;
  multi_factor_metrics?: MultiFactorMetrics;
  unsupported_claims_disclaimer?: string;
}

export interface AnalysisHistoryItem extends AnalysisResult {
  thumbnail: string; // base64 or URL
}
