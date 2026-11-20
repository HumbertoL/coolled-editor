import { GRID_HEIGHT, GRID_WIDTH } from './constants.js';

/**
 * The parts of a .jt that describe it without its pixels: shared by the
 * Samples page and the build-time manifest in vite-sample-meta.js, so the two
 * cannot disagree about a sample's frame count.
 *
 * Kept free of browser and Vite APIs: vite.config.js imports it under Node.
 */

// Bytes of pixel data for one frame: 3 bits per pixel, packed into 3 planes.
export const BYTES_PER_FRAME = (GRID_WIDTH * GRID_HEIGHT * 3) / 8;

/** The `data` object of a parsed .jt, plus its packed pixel array. */
export const jtPixelData = (jt) => {
  const data = Array.isArray(jt) ? jt[0]?.data : jt?.data;
  if (!data) {
    throw new Error('Not a .jt structure');
  }

  const pixelData = data.aniData ?? data.graffitiData;
  if (!pixelData) {
    throw new Error('No aniData or graffitiData');
  }

  return { data, pixelData };
};

/** Everything the Samples page shows about a .jt, except its pixels. */
export const readJtMeta = (jt) => {
  const { data, pixelData } = jtPixelData(jt);
  return {
    isAnimation: Boolean(data.aniType),
    // Trust the byte count over frameNum; some vendor files disagree.
    frameNum: Math.max(1, Math.round(pixelData.length / BYTES_PER_FRAME)),
    delays: data.delays ?? 300,
    pixelWidth: data.pixelWidth ?? GRID_WIDTH,
    pixelHeight: data.pixelHeight ?? GRID_HEIGHT,
  };
};
