import { GRID_HEIGHT, GRID_WIDTH } from './constants';

// Where the driver lives, for the send commands shown next to each sample.
export const DRIVER_PATH = '~/workspace/coolledx-driver';
export const EDITOR_PATH = '~/workspace/coolled-editor';
export const DOWNLOADS_PATH = '~/Downloads';

// Bytes of pixel data for one frame: 3 bits per pixel, packed into 3 planes.
export const BYTES_PER_FRAME = (GRID_WIDTH * GRID_HEIGHT * 3) / 8;
const PLANE_BYTES = BYTES_PER_FRAME / 3;

// A vendor payload is 24 zero bytes, a frame count, then a 16-bit speed,
// before the pixel planes start. Same layout the driver builds.
const VENDOR_HEADER_BYTES = 27;
const VENDOR_FRAME_OFFSET = 24;
const VENDOR_SPEED_OFFSET = 25;

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
    blurb: 'Multi-frame animations. Larger download, loads on demand.',
  },
];

/**
 * Read one pixel out of packed frame data. Each frame holds three planes
 * (red, green, blue) of one bit per pixel, walking down each column in turn.
 */
const getBit = (bytes, base, planeOffset, bitIndex) => {
  const offset = base + planeOffset + (bitIndex >> 3);
  if (offset >= bytes.length) {
    return 0;
  }
  return (bytes[offset] >> (7 - (bitIndex & 7))) & 1;
};

/**
 * Draw a single frame of packed pixel data onto a 96x16 canvas. Kept
 * deliberately cheap: the samples page renders a couple hundred of these, so
 * it decodes just the one frame it needs rather than the whole animation.
 */
export const drawFrame = (ctx, pixelBytes, frameIndex) => {
  const base = frameIndex * BYTES_PER_FRAME;
  const image = ctx.createImageData(GRID_WIDTH, GRID_HEIGHT);

  for (let column = 0; column < GRID_WIDTH; column++) {
    for (let row = 0; row < GRID_HEIGHT; row++) {
      const bitIndex = column * GRID_HEIGHT + row;
      const r = getBit(pixelBytes, base, 0, bitIndex);
      const g = getBit(pixelBytes, base, PLANE_BYTES, bitIndex);
      const b = getBit(pixelBytes, base, PLANE_BYTES * 2, bitIndex);

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
  for (let frame = 0; frame < frameNum; frame++) {
    const start = frame * BYTES_PER_FRAME;
    const end = Math.min(start + BYTES_PER_FRAME, pixelBytes.length);
    for (let i = start; i < end; i++) {
      if (pixelBytes[i] !== 0) {
        return frame;
      }
    }
  }
  return 0;
};

/** Pull the pixel data and metadata out of a parsed .jt structure. */
export const readJt = (jt) => {
  const data = Array.isArray(jt) ? jt[0]?.data : jt?.data;
  if (!data) {
    throw new Error('Not a .jt structure');
  }

  const pixelData = data.aniData ?? data.graffitiData;
  if (!pixelData) {
    throw new Error('No aniData or graffitiData');
  }

  const pixelBytes = Uint8Array.from(pixelData);
  const isAnimation = Boolean(data.aniType);

  return {
    pixelBytes,
    isAnimation,
    // Trust the byte count over frameNum; some vendor files disagree.
    frameNum: Math.max(1, Math.round(pixelBytes.length / BYTES_PER_FRAME)),
    delays: data.delays ?? 300,
    pixelWidth: data.pixelWidth ?? GRID_WIDTH,
    pixelHeight: data.pixelHeight ?? GRID_HEIGHT,
  };
};

/**
 * Convert a vendor `sendData` payload into a .jt file. Verified against all
 * 209 entries in the two packs: rebuilding the payload from the .jt this
 * produces gives back the original bytes exactly.
 */
export const vendorEntryToJt = (sendData) => {
  const frameNum = sendData[VENDOR_FRAME_OFFSET];
  const delays =
    sendData[VENDOR_SPEED_OFFSET] * 256 + sendData[VENDOR_SPEED_OFFSET + 1];

  return [
    {
      dataType: 0,
      data: {
        aniType: 1,
        pixelHeight: GRID_HEIGHT,
        pixelWidth: GRID_WIDTH,
        frameNum,
        delays,
        aniData: sendData.slice(VENDOR_HEADER_BYTES),
      },
    },
  ];
};

/** Strip the numbering the vendor prefixes to each name ("152.圣诞礼物袜"). */
const cleanVendorName = (describe, index) => {
  const trimmed = (describe ?? '').replace(/^\d+\./, '').trim();
  return trimmed || `Sample ${index + 1}`;
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
 * The .jt and .json samples committed alongside the editor. Unknown
 * extensions come back from webpack as a URL, .json as a parsed object.
 */
export const loadBundledSamples = async () => {
  const context = require.context('../sample', false, /\.(jt|json)$/);

  const samples = await Promise.all(
    context.keys().map(async (key) => {
      const name = key.replace(/^\.\//, '');
      const asset = context(key);

      let jt;
      if (typeof asset === 'string') {
        const response = await fetch(asset);
        jt = JSON.parse(await response.text());
      } else {
        jt = asset;
      }

      return {
        id: `bundled:${name}`,
        name: name.replace(/\.(jt|json)$/, ''),
        source: 'bundled',
        // Already on disk, so the command can point straight at the repo.
        localPath: `${EDITOR_PATH}/src/sample/${name}`,
        downloadName: name.endsWith('.jt') ? name : `${name}.jt`,
        jt,
      };
    }),
  );

  return samples.filter(Boolean).sort((a, b) => a.name.localeCompare(b.name));
};

/** Fetch and unpack one of the vendor packs from the README. */
export const loadVendorPack = async (pack) => {
  const url = `${process.env.PUBLIC_URL}/samples/${pack.file}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not load ${pack.file} (${response.status})`);
  }

  const body = await response.json();
  const entries = body.animationData ?? [];

  return entries.map((entry, index) => {
    const name = cleanVendorName(entry.describe, index);
    return {
      id: `${pack.id}:${index}`,
      name,
      source: pack.id,
      localPath: null,
      downloadName: safeFilename(name, `${pack.id}-${index + 1}`),
      jt: vendorEntryToJt(entry.sendData),
    };
  });
};

export const downloadJt = (sample) => {
  const blob = new Blob([JSON.stringify(sample.jt)], {
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
  return `cd ${DRIVER_PATH} && PYTHONPATH=src .venv/bin/python utils/tweak_sign.py -jt ${path}`;
};
