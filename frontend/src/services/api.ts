import { AnalysisResult } from '../types/analysis';

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

export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
};
