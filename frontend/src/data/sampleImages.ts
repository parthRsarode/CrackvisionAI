// Pre-calibrated infrastructure benchmark samples for CrackVision AI optical verification

export interface SampleImage {
  id: string;
  title: string;
  surface: string;
  severity: 'low' | 'medium' | 'high';
  thumbnailUrl: string;
  createFile: () => Promise<File>;
}

// Fetch real pre-calibrated JPEG sample assets directly
const fetchSampleFile = async (url: string, filename: string): Promise<File> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load benchmark sample: ${response.statusText}`);
  }
  const blob = await response.blob();
  return new File([blob], filename, { type: 'image/jpeg' });
};

export const SAMPLE_IMAGES: SampleImage[] = [
  {
    id: 'clean-concrete',
    title: 'Intact Concrete',
    surface: 'Clean Control (Negative)',
    severity: 'low',
    thumbnailUrl: '/samples/clean_concrete.jpg',
    createFile: () => fetchSampleFile('/samples/clean_concrete.jpg', 'clean_concrete_slab.jpg'),
  },
  {
    id: 'concrete-wall',
    title: 'Concrete Wall',
    surface: 'Shear Fissure (Positive)',
    severity: 'high',
    thumbnailUrl: '/samples/concrete_wall_crack.jpg',
    createFile: () => fetchSampleFile('/samples/concrete_wall_crack.jpg', 'concrete_wall_crack.jpg'),
  },
  {
    id: 'asphalt-road',
    title: 'Highway Asphalt',
    surface: 'Transverse Crack (Positive)',
    severity: 'high',
    thumbnailUrl: '/samples/highway_asphalt_crack.jpg',
    createFile: () => fetchSampleFile('/samples/highway_asphalt_crack.jpg', 'highway_asphalt_crack.jpg'),
  },
  {
    id: 'bridge-girder',
    title: 'Bridge Girder',
    surface: 'Flexural Distress (Positive)',
    severity: 'high',
    thumbnailUrl: '/samples/bridge_girder_crack.jpg',
    createFile: () => fetchSampleFile('/samples/bridge_girder_crack.jpg', 'bridge_girder_crack.jpg'),
  },
  {
    id: 'calibrated-aruco',
    title: 'ArUco Calibrated Pier',
    surface: 'Fiducial 50mm Datum (Positive)',
    severity: 'high',
    thumbnailUrl: '/samples/calibrated_aruco_crack.jpg',
    createFile: () => fetchSampleFile('/samples/calibrated_aruco_crack.jpg', 'calibrated_aruco_crack.jpg'),
  },
];
