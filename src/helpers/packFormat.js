/**
 * How the vendor packs and the material catalog are split for the Samples
 * page, shared by the browser (samples.js) and the build (vite-sample-meta.js).
 *
 * The packs in public/samples stay exactly as fetched -- the vendor's
 * data1696_*.json are kept byte-identical to the CDN's -- and the build
 * writes a split copy beside them: per pack, an index.json naming every
 * entry with its frame count and delay, plus numbered chunks of CHUNK_SIZE
 * entries' pixels. The page lists a pack from its index, and fetches a chunk
 * only when one of its cards nears the viewport.
 *
 * Kept free of browser and Vite APIs: Node imports it at build time.
 */
import { BYTES_PER_FRAME } from './jtMeta.js';

// Where the vendored catalog lives, relative to public/.
export const MATERIAL_DIR = 'samples/material';

// Where the split copies are served, relative to the site root.
export const SPLIT_DIR = 'samples/split';

// Entries per chunk. A row of cards is three wide; 24 is a few screens.
export const CHUNK_SIZE = 24;

/**
 * Where a split pack's files live, relative to the site root. Chunks are
 * gzipped on disk, like the material packs they come from: packed pixel
 * planes shrink 10-20x, and the build stays small whatever the host does.
 */
export const packIndexPath = (packId) => `${SPLIT_DIR}/${packId}/index.json`;
export const packChunkPath = (packId, chunk) =>
  `${SPLIT_DIR}/${packId}/${chunk}.json.gz`;

export const VENDOR_PACKS = [
  {
    id: 'static',
    label: 'Vendor static',
    file: 'data1696_static.json',
    blurb: 'Single-frame graffiti from the CoolLED1248 app.',
  },
  {
    id: 'dynamic',
    label: 'Vendor animations',
    file: 'data1696_dynamic.json',
    blurb: 'Multi-frame animations, loaded as you scroll.',
  },
];

// A vendor payload is 24 zero bytes, a frame count, then a 16-bit speed,
// before the pixel planes start. Same layout the driver builds.
const VENDOR_HEADER_BYTES = 27;
const VENDOR_FRAME_OFFSET = 24;
const VENDOR_SPEED_OFFSET = 25;

/** Split a vendor `sendData` payload into its header fields and pixels. */
export const vendorEntryParts = (sendData) => ({
  frameNum: sendData[VENDOR_FRAME_OFFSET],
  delays:
    sendData[VENDOR_SPEED_OFFSET] * 256 + sendData[VENDOR_SPEED_OFFSET + 1],
  pixels: sendData.slice(VENDOR_HEADER_BYTES),
});

/** Strip the numbering the vendor prefixes to each name ("152.圣诞礼物袜"). */
export const cleanVendorName = (describe, index) => {
  const trimmed = (describe ?? '').replace(/^\d+\./, '').trim();
  return trimmed || `Sample ${index + 1}`;
};

/**
 * Frame count as the page reports it: from the byte count, which some vendor
 * files disagree with their own frameNum about. Matches readJtMeta.
 */
export const framesInBytes = (byteLength) =>
  Math.max(1, Math.round(byteLength / BYTES_PER_FRAME));
