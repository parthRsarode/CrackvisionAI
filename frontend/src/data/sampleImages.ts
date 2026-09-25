// Utility to generate realistic sample infrastructure crack images as File objects

export interface SampleImage {
  id: string;
  title: string;
  surface: string;
  severity: 'low' | 'medium' | 'high';
  thumbnailUrl: string;
  createFile: () => Promise<File>;
}

// Helper to convert an SVG string to a JPEG File object
const svgToFile = async (svgString: string, filename: string): Promise<File> => {
  return new Promise((resolve) => {
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 600;
      canvas.height = 400;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      canvas.toBlob((b) => {
        if (b) {
          const file = new File([b], filename, { type: 'image/jpeg' });
          resolve(file);
        } else {
          // Fallback to svg file
          resolve(new File([blob], filename, { type: 'image/svg+xml' }));
        }
      }, 'image/jpeg', 0.9);
    };
    img.onerror = () => {
      // Fallback
      resolve(new File([blob], filename, { type: 'image/jpeg' }));
    };
    img.src = url;
  });
};

const concreteWallSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <radialGradient id="wallBg" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#94a3b8"/>
      <stop offset="70%" stop-color="#64748b"/>
      <stop offset="100%" stop-color="#475569"/>
    </radialGradient>
    <filter id="concreteNoise">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" result="noise"/>
      <feColorMatrix type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0.15 0" in="noise" result="coloredNoise"/>
      <feBlend mode="multiply" in="SourceGraphic" in2="coloredNoise"/>
    </filter>
  </defs>
  <rect width="600" height="400" fill="url(#wallBg)"/>
  <rect width="600" height="400" filter="url(#concreteNoise)" opacity="0.4"/>
  <!-- Diagonal Crack -->
  <g stroke="#1e293b" stroke-linecap="round" fill="none">
    <path d="M 120 40 L 160 90 L 180 130 L 220 180 L 230 240 L 280 300 L 320 370" stroke-width="4.5" opacity="0.9"/>
    <path d="M 180 130 L 230 145 L 260 170" stroke-width="2.5" opacity="0.8"/>
    <path d="M 230 240 L 210 280 L 195 320" stroke-width="2" opacity="0.75"/>
    <path d="M 280 300 L 340 330" stroke-width="1.8" opacity="0.7"/>
  </g>
  <text x="20" y="380" font-family="sans-serif" font-size="14" fill="#cbd5e1" font-weight="bold">SAMPLE #1: Concrete Wall (Diagonal Shear)</text>
</svg>
`;

const asphaltRoadSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <linearGradient id="asphaltBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="50%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#asphaltBg)"/>
  <!-- Road Yellow Line -->
  <rect x="290" y="0" width="20" height="400" fill="#eab308" opacity="0.4" stroke-dasharray="30 20"/>
  <!-- Road Crack Network -->
  <g stroke="#090d16" stroke-linecap="round" fill="none">
    <path d="M 60 220 L 140 210 L 210 240 L 280 230 L 370 250 L 460 220 L 540 260" stroke-width="5" opacity="0.95"/>
    <path d="M 210 240 L 220 310 L 260 360" stroke-width="3" opacity="0.85"/>
    <path d="M 370 250 L 390 170 L 430 110" stroke-width="3" opacity="0.85"/>
    <path d="M 140 210 L 160 140 L 190 90" stroke-width="2.5" opacity="0.8"/>
  </g>
  <text x="20" y="380" font-family="sans-serif" font-size="14" fill="#94a3b8" font-weight="bold">SAMPLE #2: Highway Asphalt (Transverse Settlement)</text>
</svg>
`;

const bridgeBeamSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <linearGradient id="beamBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#64748b"/>
      <stop offset="40%" stop-color="#475569"/>
      <stop offset="100%" stop-color="#334155"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#beamBg)"/>
  <!-- Beam Rivets -->
  <circle cx="50" cy="50" r="12" fill="#1e293b"/>
  <circle cx="550" cy="50" r="12" fill="#1e293b"/>
  <!-- Micro-cracking & Flexural Crack -->
  <g stroke="#0f172a" stroke-linecap="round" fill="none">
    <path d="M 300 380 L 305 310 L 295 240 L 310 180 L 300 120" stroke-width="4" opacity="0.9"/>
    <path d="M 295 240 L 340 220 L 370 200" stroke-width="2" opacity="0.8"/>
    <path d="M 305 310 L 260 290 L 230 280" stroke-width="2" opacity="0.8"/>
  </g>
  <text x="20" y="380" font-family="sans-serif" font-size="14" fill="#cbd5e1" font-weight="bold">SAMPLE #3: Concrete Bridge Girder (Flexural Crack)</text>
</svg>
`;

export const SAMPLE_IMAGES: SampleImage[] = [
  {
    id: 'concrete-wall',
    title: 'Concrete Wall',
    surface: 'Vertical Shear',
    severity: 'medium',
    thumbnailUrl: `data:image/svg+xml;utf8,${encodeURIComponent(concreteWallSvg)}`,
    createFile: () => svgToFile(concreteWallSvg, 'concrete_wall_diagonal.jpg'),
  },
  {
    id: 'asphalt-road',
    title: 'Highway Asphalt',
    surface: 'Pavement Fatigue',
    severity: 'high',
    thumbnailUrl: `data:image/svg+xml;utf8,${encodeURIComponent(asphaltRoadSvg)}`,
    createFile: () => svgToFile(asphaltRoadSvg, 'highway_asphalt_crack.jpg'),
  },
  {
    id: 'bridge-girder',
    title: 'Bridge Girder',
    surface: 'Flexural Concrete',
    severity: 'low',
    thumbnailUrl: `data:image/svg+xml;utf8,${encodeURIComponent(bridgeBeamSvg)}`,
    createFile: () => svgToFile(bridgeBeamSvg, 'bridge_girder_flexural.jpg'),
  },
];
