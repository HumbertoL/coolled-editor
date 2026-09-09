import { GRID_HEIGHT, GRID_WIDTH } from './constants.js';
import { inflateResponse } from './gzip.js';

/**
 * The vendor's bitmap font, as a source of text for the panel.
 *
 * Extracted from the CoolLED1248 APK by scripts/extract-font.mjs. The tables
 * are flat and header-less, indexed straight by code point, and packed the
 * same way the panel packs pixels: column-major, most significant bit at the
 * top of the column. So a glyph is 16 columns of two bytes -- first byte rows
 * 0-7, second rows 8-15 -- which is why nothing here has to transform
 * anything, only place it.
 *
 * Glyphs are stored in a fixed cell, left-aligned inside it, with the unused
 * columns blank. Setting text at the cell width looks gappy, so by default
 * blank columns are trimmed off each glyph and a fixed tracking is inserted
 * between them, which is what the app itself does.
 */

const FONT_NAME = 'unicode16';
const FONT_DIR = 'fonts';

export const DEFAULT_TRACKING = 1;

// A blank glyph has no columns to trim, so a space needs an advance of its
// own. Three columns plus tracking sits about right against 7-column Latin.
export const DEFAULT_SPACE_WIDTH = 3;

let manifestPromise = null;
const pages = new Map();
const pagePromises = new Map();

const fontUrl = (file) =>
  `${process.env.PUBLIC_URL}/${FONT_DIR}/${FONT_NAME}/${file}`;

export const loadManifest = () => {
  if (!manifestPromise) {
    manifestPromise = fetch(fontUrl('index.json'))
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            'No font data. Run `node scripts/extract-font.mjs` to extract it.',
          );
        }
        return response.json();
      })
      .catch((error) => {
        // Don't cache the failure; a retry after running the script should work.
        manifestPromise = null;
        throw error;
      });
  }
  return manifestPromise;
};

const loadPage = (manifest, start) => {
  if (pages.has(start)) {
    return Promise.resolve(pages.get(start));
  }
  if (pagePromises.has(start)) {
    return pagePromises.get(start);
  }

  const entry = manifest.pages.find((page) => page.start === start);
  if (!entry) {
    // A page with no ink at all was never written out. Cache the absence so
    // text full of unassigned code points doesn't refetch on every keystroke.
    pages.set(start, null);
    return Promise.resolve(null);
  }

  const promise = fetch(fontUrl(entry.file))
    .then(inflateResponse)
    .then((bytes) => {
      pages.set(start, bytes);
      pagePromises.delete(start);
      return bytes;
    })
    .catch((error) => {
      pagePromises.delete(start);
      throw error;
    });

  pagePromises.set(start, promise);
  return promise;
};

/** Code points in a string, so astral characters count as one. */
const codePoints = (text) => Array.from(text).map((ch) => ch.codePointAt(0));

/**
 * Fetch whatever pages `text` needs. Call before laying it out; everything
 * below is synchronous so it can run inside a render.
 */
export const ensureGlyphs = async (text) => {
  const manifest = await loadManifest();
  const needed = new Set(
    codePoints(text)
      .filter((cp) => cp < manifest.pageSize * 64)
      .map((cp) => Math.floor(cp / manifest.pageSize) * manifest.pageSize),
  );

  await Promise.all([...needed].map((start) => loadPage(manifest, start)));
  return manifest;
};

/**
 * One glyph as an array of 16-bit column masks, bit 15 being the top row.
 * Returns null for a code point the font has no ink for.
 */
export const glyphColumns = (manifest, codePoint) => {
  const start = Math.floor(codePoint / manifest.pageSize) * manifest.pageSize;
  const page = pages.get(start);
  if (!page) {
    return null;
  }

  const offset = (codePoint - start) * manifest.bytesPerGlyph;
  const bytesPerColumn = manifest.bytesPerGlyph / manifest.glyphWidth;

  const columns = [];
  let lit = false;
  for (let column = 0; column < manifest.glyphWidth; column++) {
    let mask = 0;
    for (let byte = 0; byte < bytesPerColumn; byte++) {
      mask = (mask << 8) | page[offset + column * bytesPerColumn + byte];
    }
    // Masks are stored top-aligned in a 16-bit word regardless of glyph
    // height, so a 8-row font still has its top row at bit 15.
    columns.push(mask << (16 - bytesPerColumn * 8));
    if (mask) lit = true;
  }

  return lit ? columns : null;
};

const trim = (columns) => {
  let first = 0;
  let last = columns.length - 1;
  while (first <= last && !columns[first]) first++;
  while (last >= first && !columns[last]) last--;
  return columns.slice(first, last + 1);
};

/**
 * Lay text out into a single list of column masks.
 *
 * `monospace` keeps the font's own cell width, which lines characters up in a
 * grid; the default trims each glyph and inserts `tracking` between them,
 * which fits noticeably more on 96 columns.
 */
export const layoutText = (
  manifest,
  text,
  {
    tracking = DEFAULT_TRACKING,
    spaceWidth = DEFAULT_SPACE_WIDTH,
    monospace = false,
  } = {},
) => {
  const columns = [];
  const missing = [];

  codePoints(text).forEach((codePoint, index) => {
    if (index > 0) {
      for (let i = 0; i < tracking; i++) columns.push(0);
    }

    const glyph = glyphColumns(manifest, codePoint);

    if (!glyph) {
      // Blank in the font: a space if that's what was typed, otherwise a
      // character this font can't draw. Both advance; only one is a problem.
      if (codePoint !== 0x20) {
        missing.push(String.fromCodePoint(codePoint));
      }
      for (let i = 0; i < spaceWidth; i++) columns.push(0);
      return;
    }

    const cell = monospace ? glyph : trim(glyph);
    cell.forEach((mask) => columns.push(mask));
  });

  return { columns, width: columns.length, missing };
};

/**
 * Paint laid-out columns into a pixel array, in place.
 *
 * `pixelArray` is the editor's own representation -- one {r, g, b} per LED,
 * frames end to end -- so this writes into the frame at `frameOffset` and
 * leaves everything else alone. Columns outside the panel are clipped.
 */
export const drawColumns = (
  pixelArray,
  layout,
  {
    color,
    x = 0,
    y = 0,
    frameOffset = 0,
    width = GRID_WIDTH,
    height = GRID_HEIGHT,
  },
) => {
  layout.columns.forEach((mask, index) => {
    const column = x + index;
    if (mask === 0 || column < 0 || column >= width) {
      return;
    }

    for (let row = 0; row < height; row++) {
      const source = row - y;
      if (source < 0 || source > 15) continue;
      if (!(mask & (0x8000 >> source))) continue;

      pixelArray[frameOffset + column * height + row] = color;
    }
  });

  return pixelArray;
};

/** Where to start drawing so `layout` sits centred, or flush right. */
export const alignX = (layout, align, width = GRID_WIDTH) => {
  if (align === 'center') {
    return Math.round((width - layout.width) / 2);
  }
  if (align === 'right') {
    return width - layout.width;
  }
  return 0;
};

/** Convenience for callers that just want a rendered string. */
export const renderText = async (text, options = {}) => {
  const manifest = await ensureGlyphs(text);
  return layoutText(manifest, text, options);
};
