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

  // Building & Asset Profile and Age-Aware Context
  building_profile?: BuildingProfile;
  age_deterioration_context?: AgeDeteriorationContext;
  remediation_specification?: RemediationSpecification;

  // Phase 04 Spatial Calibration & Caliper Fields
  calibration?: CalibrationInfo;
  caliper_samples?: CaliperSample[];
}

export interface RemediationSpecification {
  protocol_title: string;
  governing_standard: string;
  structural_material: string;
  material_specification: string;
  prescribed_actions: string[];
  equipment_required: string[];
  safety_protocol?: string;
  preventive_maintenance?: string;
  summary_recommendation?: string;
}

export interface BuildingProfile {
  building_name?: string | null;
  building_type?: string;
  construction_year?: number | null;
  building_age_years?: number | null;
  age_verification?: 'documented' | 'owner_reported' | 'estimated' | 'unknown' | string;
  inspection_date?: string | null;
  structural_system?: string | null;
  structural_material?: string;
  structural_member?: string | null;
  member_importance?: string;
  maintenance_condition?: string;
  environmental_exposure?: string;
  previous_repairs?: string;
  water_leakage?: boolean;
  known_reinforcement_corrosion?: boolean;
  known_spalling?: boolean;
  known_settlement?: boolean;
  damaging_event?: boolean;
  damaging_event_details?: string | null;
  repair_history_notes?: string | null;
}

export interface AgeDeteriorationContext {
  status: 'context_documented' | 'potential_age_related_distress' | 'further_deterioration_assessment_recommended' | 'early_age_construction_defect_suspected' | 'insufficient_historical_information' | 'no_age_specific_conclusion_supported' | string;
  construction_year?: number | null;
  age_at_inspection?: number | null;
  age_verification: string;
  inspection_date?: string | null;
  environmental_exposure: string;
  maintenance_condition: string;
  observed_deterioration_indicators: string[];
  historical_progression: string;
  missing_information: string[];
  engineering_reasoning: string;
  context_disclaimer: string;
}

export interface CalibrationInfo {
  calibration_status: 'fiducial_calibrated' | 'user_two_point_calibrated' | 'uncalibrated_macro';
  method: 'aruco_fiducial' | 'manual_two_point' | 'default_macro';
  marker_id?: number | null;
  marker_size_mm?: number | null;
  mean_side_px?: number;
  marker_corners?: number[][];
  normalized_corners?: number[][];
  mm_per_pixel: number;
  assumed_field_width_m: number;
  confidence: number;
}

export interface CaliperSample {
  id: string; // e.g. "CAL-01"
  x: number;
  y: number;
  width_px: number;
  width_mm: number;
  points: [number, number][]; // span endpoints [[x1, y1], [x2, y2]]
  normalized_points: [number, number][];
  timestamp: string;
  note?: string;
  compliance_status?: 'within_limit' | 'exceeds_limit';
}

export interface AnalysisHistoryItem extends AnalysisResult {
  thumbnail: string; // base64 or URL
}

export interface BatchAnalysisSummary {
  total_images: number;
  defects_detected_count: number;
  critical_count: number;
  moderate_count: number;
  minor_count: number;
  max_width_mm: number;
  total_crack_length_mm: number;
  critical_elements_flagged: string[];
}

export interface BatchAnalysisResponse {
  summary: BatchAnalysisSummary;
  results: AnalysisResult[];
}
