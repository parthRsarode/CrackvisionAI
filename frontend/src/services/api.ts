import { AnalysisResult, BatchAnalysisResponse } from '../types/analysis';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface AnalysisMetadata {
  memberType?: string;
  elementCriticality?: string;
  proximityToSupports?: string;
  visibleSpalling?: boolean;
  visibleCorrosion?: boolean;
  previousWidthMm?: number | null;
  crackDepthStatus?: string;
  environment?: string;
  standardCode?: string;
}

export const analyzeImage = async (file: File, metadata?: AnalysisMetadata): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  if (metadata) {
    if (metadata.memberType) formData.append('member_type', metadata.memberType);
    if (metadata.elementCriticality) formData.append('element_criticality', metadata.elementCriticality);
    if (metadata.proximityToSupports) formData.append('proximity_to_supports', metadata.proximityToSupports);
    if (metadata.visibleSpalling !== undefined) formData.append('visible_spalling', String(metadata.visibleSpalling));
    if (metadata.visibleCorrosion !== undefined) formData.append('visible_corrosion', String(metadata.visibleCorrosion));
    if (metadata.previousWidthMm !== undefined && metadata.previousWidthMm !== null) {
      formData.append('previous_width_mm', String(metadata.previousWidthMm));
    }
    if (metadata.crackDepthStatus) formData.append('crack_depth_status', metadata.crackDepthStatus);
    if (metadata.environment) formData.append('environment', metadata.environment);
    if (metadata.standardCode) formData.append('standard_code', metadata.standardCode);
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

export const analyzeBatchImages = async (
  files: File[],
  metadata?: AnalysisMetadata
): Promise<BatchAnalysisResponse> => {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));

  if (metadata) {
    if (metadata.memberType) formData.append('member_type', metadata.memberType);
    if (metadata.elementCriticality) formData.append('element_criticality', metadata.elementCriticality);
    if (metadata.proximityToSupports) formData.append('proximity_to_supports', metadata.proximityToSupports);
    if (metadata.visibleSpalling !== undefined) formData.append('visible_spalling', String(metadata.visibleSpalling));
    if (metadata.visibleCorrosion !== undefined) formData.append('visible_corrosion', String(metadata.visibleCorrosion));
    if (metadata.standardCode) formData.append('standard_code', metadata.standardCode);
  }

  const response = await fetch(`${API_BASE_URL}/analyze/batch`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Batch inspection failed: ${response.statusText}`);
  }

  return response.json();
};

export const fetchSurveys = async (severity?: string, standardCode?: string): Promise<AnalysisResult[]> => {
  const params = new URLSearchParams();
  if (severity && severity !== 'all') params.append('severity', severity);
  if (standardCode && standardCode !== 'all') params.append('standard_code', standardCode);

  const response = await fetch(`${API_BASE_URL}/api/surveys?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch surveys: ${response.statusText}`);
  }
  return response.json();
};

export const fetchSurveyById = async (surveyId: string): Promise<AnalysisResult> => {
  const response = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}`);
  if (!response.ok) {
    throw new Error(`Failed to load survey: ${response.statusText}`);
  }
  return response.json();
};

export const saveSurveyRecord = async (surveyData: any): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/surveys`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(surveyData),
  });
  if (!response.ok) {
    throw new Error(`Failed to save survey: ${response.statusText}`);
  }
  return response.json();
};

export const deleteSurveyRecord = async (surveyId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete survey: ${response.statusText}`);
  }
};

export const downloadSurveyPDF = async (surveyId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}/pdf`);
  if (!response.ok) {
    throw new Error(`Failed to generate SCAR PDF: ${response.statusText}`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `SCAR_Report_${surveyId}.pdf`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const exportDirectPDF = async (surveyData: any): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/surveys/export-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(surveyData),
  });
  if (!response.ok) {
    throw new Error(`Failed to generate SCAR PDF: ${response.statusText}`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  const surveyId = surveyData.survey_id || surveyData.analysis_id || 'INSPECTION';
  link.setAttribute('download', `SCAR_Report_${surveyId}.pdf`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
};

