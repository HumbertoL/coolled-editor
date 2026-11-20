import sampleMeta from 'virtual:sample-meta';
import { GRID_HEIGHT, GRID_WIDTH } from './constants.js';
import { inflateJson } from './gzip.js';
import { BYTES_PER_FRAME, jtPixelData, readJtMeta } from './jtMeta.js';
import {
  MATERIAL_DIR,
  VENDOR_PACKS,
  framesInBytes,
  packChunkPath,
  packIndexPath,
  vendorEntryParts,
} from './packFormat.js';
import { categoryOf, descriptionOf, keywordsOf } from './sampleCategories.js';

// Where the driver lives, for the send commands shown next to each sample.
export const DRIVER_PATH = '~/workspace/coolledx-driver';
export const EDITOR_PATH = '~/workspace/coolled-editor';
export const DOWNLOADS_PATH = '~/Downloads';

export { BYTES_PER_FRAME };

export { MATERIAL_DIR, VENDOR_PACKS };

/**
 * Read one bit out of the packed pixel data.
 */
const getBit = (bytes, bitIndex) => {
  const offset = bitIndex >> 3;
  if (offset >= bytes.length) {
    return 0;
  }
  return (bytes[offset] >> (7 - (bitIndex & 7))) & 1;
};

/**
 * Bit offset of a pixel within its color plane.
 *
 * The three color planes span the WHOLE animation rather than sitting inside
 * each frame: all frames' red bits, then all frames' green, then all blue.
 * Within a plane the frames sit side by side, each walking down its columns.
 * Same layout parse_data.js reads and export_data.js writes.
 */
const planeBitIndex = (frameIndex, column, row) =>
  (frameIndex * GRID_WIDTH + column) * GRID_HEIGHT + row;

/** Bits in one color plane, for an animation of `frameNum` frames. */
const planeBits = (frameNum) => frameNum * GRID_WIDTH * GRID_HEIGHT;

// Every preview is the same size and drawing is synchronous, so one buffer
// can be shared. Allocating a fresh ImageData per frame meant ~6KB of garbage
// per redraw, which adds up fast once previews play unattended.
let scratchImage = null;

const getScratchImage = (ctx) => {
  if (!scratchImage) {
    try {
      scratchImage = new ImageData(GRID_WIDTH, GRID_HEIGHT);
    } catch {
      // Older engines only expose the factory on a context.
      scratchImage = ctx.createImageData(GRID_WIDTH, GRID_HEIGHT);
    }
  }
  return scratchImage;
};

/**
 * Draw a single frame of packed pixel data onto a 96x16 canvas. Kept
 * deliberately cheap: the samples page renders a couple hundred of these, so
 * it decodes just the one frame it needs rather than the whole animation.
 *
 * Safe to share one buffer: every channel of every pixel is written below, so
 * nothing carries over from the previous call.
 */
export const drawFrame = (ctx, pixelBytes, frameIndex, frameNum) => {
  const plane = planeBits(frameNum);
  const image = getScratchImage(ctx);

  for (let column = 0; column < GRID_WIDTH; column++) {
    for (let row = 0; row < GRID_HEIGHT; row++) {
      const bitIndex = planeBitIndex(frameIndex, column, row);
      const r = getBit(pixelBytes, bitIndex);
      const g = getBit(pixelBytes, plane + bitIndex);
      const b = getBit(pixelBytes, plane * 2 + bitIndex);

      const target = (row * GRID_WIDTH + column) * 4;
      image.data[target] = r * 255;
      image.data[target + 1] = g * 255;
      image.data[target + 2] = b * 255;
      image.data[target + 3] = 255;
    }
  }

  ctx.putImageData(image, 0, 0);
};

/**
 * Index of the first frame with any lit pixel. A handful of the vendor
 * animations fade in from black, and a blank still preview reads as broken.
 */
export const firstLitFrame = (pixelBytes, frameNum) => {
  const planeByteLength = planeBits(frameNum) / 8;
  const frameByteLength = (GRID_WIDTH * GRID_HEIGHT) / 8;

  for (let frame = 0; frame < frameNum; frame++) {
    // A frame's bits live in three separate stretches, one per plane.
    for (let plane = 0; plane < 3; plane++) {
      const start = plane * planeByteLength + frame * frameByteLength;
      const end = Math.min(start + frameByteLength, pixelBytes.length);
      for (let i = start; i < end; i++) {
        if (pixelBytes[i] !== 0) {
          return frame;
        }
      }
    }
  }
  return 0;
};

/** Pull the pixel data and metadata out of a parsed .jt structure. */
export const readJt = (jt) => ({
  ...readJtMeta(jt),
  pixelBytes: Uint8Array.from(jtPixelData(jt).pixelData),
});

/**
 * Convert a vendor `sendData` payload into a .jt file. Verified against all
 * 209 entries in the two packs: rebuilding the payload from the .jt this
 * produces gives back the original bytes exactly.
 */
export const vendorEntryToJt = (sendData) => {
  const { frameNum, delays, pixels } = vendorEntryParts(sendData);
  return pixelsToJt(frameNum, delays, pixels);
};

/** A minimal one-animation .jt around already-packed pixel planes. */
const pixelsToJt = (frameNum, delays, pixels) => [
  {
    dataType: 0,
    data: {
      aniType: 1,
      pixelHeight: GRID_HEIGHT,
      pixelWidth: GRID_WIDTH,
      frameNum,
      delays,
      aniData: Array.from(pixels),
    },
  },
];

const base64ToBytes = (base64) => {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
};

/**
 * Build a .jt from a material pack entry. The pack already holds the packed
 * planes, converted from the vendor's GIF by scripts/fetch-material.mjs.
 */
export const materialEntryToJt = (entry) =>
  pixelsToJt(entry.frameNum, entry.delays, base64ToBytes(entry.data));

/** Which material packs have been vendored, and how big each one is. */
export const loadMaterialIndex = async () => {
  const url = `${import.meta.env.BASE_URL}${MATERIAL_DIR}/index.json`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      return [];
    }
    const body = await response.json();
    return body.packs ?? [];
  } catch (error) {
    // Nobody has run the fetch script yet; the catalog tabs just stay hidden.
    console.warn('No material catalog index', error);
    return [];
  }
};

// Chunks of a split pack, one request each for the life of the page.
const chunkRequests = new Map();

const fetchJson = async (url, what) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not load ${what} (${response.status})`);
  }
  // Chunks are gzipped on disk; inflateJson passes plain JSON straight through.
  return inflateJson(response);
};

/**
 * List one vendor or material pack from its split index (written by
 * scripts/vite-sample-meta.js): every entry's name, frame count and delay,
 * but no pixels. Those come a chunk at a time through loadSampleJt.
 */
export const loadPack = async (packId) => {
  const root = import.meta.env.BASE_URL;
  const index = await fetchJson(
    `${root}${packIndexPath(packId)}`,
    `the ${packId} pack`,
  );

  return index.items.map((item, i) => ({
    id: `${packId}:${i}`,
    name: item.name,
    source: packId,
    localPath: null,
    downloadName: safeFilename(item.name, `${packId}-${i + 1}`),
    meta: {
      isAnimation: true,
      frameNum: framesInBytes(item.bytes),
      delays: item.delays,
      pixelWidth: GRID_WIDTH,
      pixelHeight: GRID_HEIGHT,
    },
    chunk: {
      url: `${root}${packChunkPath(packId, Math.floor(i / index.chunkSize))}`,
      offset: i % index.chunkSize,
      frameNum: item.frameNum,
      delays: item.delays,
    },
    jt: null,
  }));
};

const loadChunkJt = async ({ url, offset, frameNum, delays }) => {
  if (!chunkRequests.has(url)) {
    chunkRequests.set(
      url,
      fetchJson(url, 'a sample chunk').catch((error) => {
        chunkRequests.delete(url);
        throw error;
      }),
    );
  }
  const chunk = await chunkRequests.get(url);
  return materialEntryToJt({ frameNum, delays, data: chunk[offset] });
};

/** A filename safe to hand to a shell without quoting. */
export const safeFilename = (name, fallback) => {
  const slug = name
    .normalize('NFKD')
    // Anything outside a conservative set becomes a dash.
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48);
  return `${slug || fallback}.jt`;
};

/**
 * The .jt and .json samples committed alongside the editor. The glob is
 * resolved at build time, so dropping a file into src/sample is enough --
 * but it must stay a literal, since Vite rewrites it statically. Every
 * match comes back as a URL, fetched only when it is needed.
 */
const BUNDLED_SAMPLE_URLS = import.meta.glob('../sample/*.{jt,json}', {
  query: '?url',
  import: 'default',
  eager: true,
});

// One fetch per sample for the life of the page, however many cards (or
// re-renders, or an Edit click racing the scroll) ask for it.
const jtRequests = new Map();

/**
 * The parsed .jt behind a sample, fetched on first use: a bundled sample's
 * own file, or the chunk of a split pack it sits in. A failed fetch is
 * forgotten, so asking again retries.
 */
export const loadSampleJt = (sample) => {
  if (sample.jt) {
    return Promise.resolve(sample.jt);
  }
  if (sample.chunk) {
    return loadChunkJt(sample.chunk);
  }
  if (!jtRequests.has(sample.url)) {
    const request = fetch(sample.url)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not load ${sample.name} (${response.status})`);
        }
        return response.text();
      })
      .then((text) => JSON.parse(text))
      .catch((error) => {
        jtRequests.delete(sample.url);
        throw error;
      });
    jtRequests.set(sample.url, request);
  }
  return jtRequests.get(sample.url);
};

/**
 * Every bundled sample, without its pixels. Names, categories, descriptions
 * and search all work from this; `meta` comes from the build-time manifest
 * (virtual:sample-meta), and the .jt itself waits for loadSampleJt.
 */
export const listBundledSamples = () =>
  Object.entries(BUNDLED_SAMPLE_URLS)
    .map(([key, url]) => {
      const name = key.replace(/^.*\//, '');
      const base = name.replace(/\.(jt|json)$/, '');
      return {
        id: `bundled:${name}`,
        name: base,
        category: categoryOf(base),
        description: descriptionOf(base),
        keywords: keywordsOf(base),
        source: 'bundled',
        // Already on disk, so the command can point straight at the repo.
        localPath: `${EDITOR_PATH}/src/sample/${name}`,
        downloadName: name.endsWith('.jt') ? name : `${name}.jt`,
        url,
        meta: sampleMeta[name] ?? null,
        jt: null,
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));

export const downloadJt = async (sample) => {
  const jt = await loadSampleJt(sample);
  const blob = new Blob([JSON.stringify(jt)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = sample.downloadName;
  link.click();

  // Give the click a tick to start before releasing the blob.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

export const sendCommandFor = (sample) => {
  const path = sample.localPath ?? `${DOWNLOADS_PATH}/${sample.downloadName}`;
  // --command-timeout raises the per-chunk ack wait from 1s; without it a
  // multi-frame animation can time out and transfer only part way.
  return `cd ${DRIVER_PATH} && PYTHONPATH=src .venv/bin/python utils/tweak_sign.py --command-timeout 8 -jt ${path}`;
};
