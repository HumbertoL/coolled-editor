import { parseGIF, decompressFrames } from 'gifuct-js';
import { GRID_HEIGHT, GRID_WIDTH } from './constants.js';

/**
 * GIF -> panel pixels.
 *
 * Two things make this less trivial than it looks, and both bit the earlier
 * version of this file:
 *
 * 1. A GIF frame is a *patch*, not a picture. It can be smaller than the
 *    canvas, sit at an offset, and leave pixels transparent so whatever the
 *    previous frame drew shows through. Reading `frame.patch` as if it were
 *    the whole canvas shifts and smears anything that isn't a full-size
 *    frame -- and in the vendor material catalog roughly a third of all
 *    frames are partial.
 * 2. The panel has 3 bits per pixel (one on/off per channel), so every colour
 *    has to be reduced to one of eight. Doing that by exact-matching a
 *    handful of hardcoded RGB triples only ever works for the one GIF the
 *    list was tuned against.
 */

/** All-off pixel. Shared: nothing in the app mutates these objects. */
const BLACK = Object.freeze({ r: false, g: false, b: false });

/**
 * Items in the vendor material catalog are real GIFs whose first 32 bytes are
 * XOR'd with 0xDA. See DptModelLoader in the CoolLED1248 app, which does
 * exactly this before handing the stream to its image loader. Left alone for
 * bytes that already look like a GIF, so it is safe to call on any input.
 */
export const MATERIAL_GIF_XOR = 0xda;
export const MATERIAL_GIF_XOR_LENGTH = 32;

export const deobfuscateMaterialGif = (bytes) => {
  const out = Uint8Array.from(bytes);
  if (out[0] === 0x47 && out[1] === 0x49 && out[2] === 0x46) {
    return out;
  }
  for (let i = 0; i < Math.min(MATERIAL_GIF_XOR_LENGTH, out.length); i++) {
    out[i] ^= MATERIAL_GIF_XOR;
  }
  return out;
};

/**
 * Reduce a colour to the eight the panel can show, keeping its hue.
 *
 * A channel lights up if it carries at least half of the pixel's dominant
 * channel, which is what separates "dim red" from "dark grey": (120, 20, 20)
 * stays red, (120, 110, 100) goes white. Anything below the floor, or mostly
 * transparent, is off.
 */
const BRIGHTNESS_FLOOR = 24;
const CHANNEL_RATIO = 0.5;

export const quantizePixel = (r, g, b, a = 255) => {
  if (a < 128) {
    return BLACK;
  }

  const dominant = Math.max(r, g, b);
  if (dominant < BRIGHTNESS_FLOOR) {
    return BLACK;
  }

  const threshold = dominant * CHANNEL_RATIO;
  return {
    r: r >= threshold,
    g: g >= threshold,
    b: b >= threshold,
  };
};

/**
 * Flatten a GIF into one full-canvas RGBA buffer per frame.
 *
 * Both disposal methods the vendor GIFs use (0 "unspecified" and 1 "keep")
 * leave the previous frame in place, so frames accumulate. Disposal 2
 * ("restore to background") clears the patch area first, and 3 ("restore to
 * previous") rolls back to the frame before -- handled so this works on
 * arbitrary GIFs a user drops in, not just the catalog's.
 */
export const compositeGifFrames = (buffer) => {
  const gif = parseGIF(buffer);
  const frames = decompressFrames(gif, true);

  const { width, height } = gif.lsd;
  let canvas = new Uint8ClampedArray(width * height * 4);

  return frames.map((frame) => {
    const { dims, patch, disposalType, delay } = frame;
    const previous = disposalType === 3 ? canvas.slice() : null;

    for (let y = 0; y < dims.height; y++) {
      const canvasY = dims.top + y;
      if (canvasY < 0 || canvasY >= height) continue;

      for (let x = 0; x < dims.width; x++) {
        const canvasX = dims.left + x;
        if (canvasX < 0 || canvasX >= width) continue;

        const from = (y * dims.width + x) * 4;
        // Transparent patch pixels leave the frame underneath showing.
        if (patch[from + 3] === 0) continue;

        const to = (canvasY * width + canvasX) * 4;
        canvas[to] = patch[from];
        canvas[to + 1] = patch[from + 1];
        canvas[to + 2] = patch[from + 2];
        canvas[to + 3] = patch[from + 3];
      }
    }

    const rgba = canvas.slice();

    if (disposalType === 2) {
      for (let y = 0; y < dims.height; y++) {
        const canvasY = dims.top + y;
        if (canvasY < 0 || canvasY >= height) continue;
        const start = (canvasY * width + Math.max(0, dims.left)) * 4;
        const span = Math.min(dims.width, width - dims.left) * 4;
        if (span > 0) canvas.fill(0, start, start + span);
      }
    } else if (disposalType === 3 && previous) {
      canvas = previous;
    }

    return { rgba, width, height, delay };
  });
};

/**
 * Drop one composited frame onto the panel grid.
 *
 * A GIF the same size as the panel lands 1:1; anything else is centred, and
 * anything larger is cropped rather than scaled. The grid is stored column by
 * column, which is the order the .jt planes are packed in.
 */
const placeFrameOnGrid = (frame, target, base, gridWidth, gridHeight) => {
  const offsetX = Math.round((gridWidth - frame.width) / 2);
  const offsetY = Math.round((gridHeight - frame.height) / 2);

  for (let y = 0; y < frame.height; y++) {
    const row = y + offsetY;
    if (row < 0 || row >= gridHeight) continue;

    for (let x = 0; x < frame.width; x++) {
      const column = x + offsetX;
      if (column < 0 || column >= gridWidth) continue;

      const source = (y * frame.width + x) * 4;
      target[base + column * gridHeight + row] = quantizePixel(
        frame.rgba[source],
        frame.rgba[source + 1],
        frame.rgba[source + 2],
        frame.rgba[source + 3],
      );
    }
  }
};

/**
 * The .jt format carries a single frame delay for the whole animation, so pick
 * the one most frames use. GIF delays are in 10ms units internally; gifuct
 * has already converted them to milliseconds.
 */
const commonDelay = (frames, fallback = 300) => {
  const counts = new Map();
  frames.forEach(({ delay }) => {
    if (!delay) return;
    counts.set(delay, (counts.get(delay) ?? 0) + 1);
  });

  let best = fallback;
  let bestCount = 0;
  counts.forEach((count, delay) => {
    if (count > bestCount) {
      best = delay;
      bestCount = count;
    }
  });

  return best;
};

/**
 * Convert a GIF into the imageData shape the editor works with: one
 * {r, g, b} per LED, all frames end to end.
 */
export const gifToImageData = (
  buffer,
  { width = GRID_WIDTH, height = GRID_HEIGHT } = {},
) => {
  const frames = compositeGifFrames(buffer);
  if (frames.length === 0) {
    throw new Error('GIF has no frames');
  }

  const pixelsPerFrame = width * height;
  const pixelArray = new Array(pixelsPerFrame * frames.length).fill(BLACK);

  frames.forEach((frame, index) => {
    placeFrameOnGrid(
      frame,
      pixelArray,
      index * pixelsPerFrame,
      width,
      height,
    );
  });

  return {
    pixelArray,
    isAnimation: frames.length > 1,
    delays: commonDelay(frames),
    frameNum: frames.length,
    pixelWidth: width,
    pixelHeight: height,
  };
};

/** Read a File/Blob from the editor's file picker. */
export const processGif = async (file) => {
  try {
    const buffer = await file.arrayBuffer();
    const bytes = deobfuscateMaterialGif(new Uint8Array(buffer));
    return gifToImageData(
      bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    );
  } catch (error) {
    console.error('Could not process GIF', error);
    return undefined;
  }
};
