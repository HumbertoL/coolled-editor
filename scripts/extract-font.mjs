#!/usr/bin/env node
/**
 * Extract the CoolLED1248 app's bitmap font into public/fonts/.
 *
 * The app ships flat, header-less glyph tables in its APK assets, indexed
 * directly by Unicode code point, packed exactly the way the panel packs
 * pixels: column-major, most significant bit at the top. See
 * docs/VENDOR_DATA.md.
 *
 *   node scripts/extract-font.mjs                        # default APK path
 *   node scripts/extract-font.mjs --apk ~/Downloads/x.apk
 *   node scripts/extract-font.mjs --asset /tmp/UNICODE16 --name unicode16
 *
 * Output is split into pages of 1024 code points, and blank pages are
 * dropped, so the editor fetches ~7KB to set Latin text instead of the whole
 * 2MB table. Regenerating is cheap; the pages are committed so the editor
 * works without an APK to hand.
 */
import fs from 'fs/promises';
import path from 'path';
import { execFileSync } from 'child_process';
import { gzipSync } from 'zlib';

const DEFAULT_APK = `${process.env.HOME}/Downloads/CoolLED1248com.jtkj.led1248v2.7.7.apk`;
const DEFAULT_OUT = 'public/fonts';

// The asset name, and the glyph geometry that goes with it. Bytes per glyph
// is what the app skips per code point: `open.skip(c * 32)` for UNICODE16.
const FONTS = {
  unicode16: { asset: 'UNICODE16', width: 16, height: 16, bytesPerGlyph: 32 },
  unicode16bold: {
    asset: 'UNICODE16_bold',
    width: 16,
    height: 16,
    bytesPerGlyph: 32,
  },
  unicode12: { asset: 'UNICODE12', width: 12, height: 16, bytesPerGlyph: 24 },
  font8: { asset: '8_small', width: 8, height: 8, bytesPerGlyph: 8 },
};

const CODE_POINTS = 0x10000;
const PAGE_SIZE = 1024;

const parseArgs = (argv) => {
  const args = {
    apk: DEFAULT_APK,
    asset: null,
    name: 'unicode16',
    out: DEFAULT_OUT,
  };
  for (let i = 0; i < argv.length; i += 2) {
    const value = argv[i + 1];
    switch (argv[i]) {
      case '--apk':
        args.apk = value;
        break;
      case '--asset':
        args.asset = value;
        break;
      case '--name':
        args.name = value;
        break;
      case '--out':
        args.out = value;
        break;
      default:
        throw new Error(`Unknown option ${argv[i]}`);
    }
  }
  if (!FONTS[args.name]) {
    throw new Error(
      `Unknown font ${args.name}. One of: ${Object.keys(FONTS).join(', ')}`,
    );
  }
  return args;
};

/** Read one asset out of the APK. It's a zip, so unzip can stream it out. */
const readFromApk = (apkPath, assetName) => {
  try {
    return execFileSync('unzip', ['-p', apkPath, `assets/${assetName}`], {
      maxBuffer: 64 * 1024 * 1024,
      encoding: 'buffer',
    });
  } catch (error) {
    throw new Error(
      `Could not read assets/${assetName} from ${apkPath}. ` +
        `Pass --apk <path>, or --asset <extracted file>. (${error.message})`,
    );
  }
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const font = FONTS[args.name];

  const table = args.asset
    ? await fs.readFile(args.asset)
    : readFromApk(args.apk, font.asset);

  const expected = CODE_POINTS * font.bytesPerGlyph;
  if (table.length !== expected) {
    // A short table is not fatal -- it just means fewer code points -- but a
    // size that isn't a multiple of the glyph stride means the wrong asset.
    if (table.length % font.bytesPerGlyph !== 0) {
      throw new Error(
        `${font.asset} is ${table.length} bytes, not a multiple of ` +
          `${font.bytesPerGlyph}; is that the right asset?`,
      );
    }
    console.warn(
      `Note: ${font.asset} is ${table.length} bytes, expected ${expected}.`,
    );
  }

  const outDir = path.join(args.out, args.name);
  await fs.rm(outDir, { recursive: true, force: true });
  await fs.mkdir(outDir, { recursive: true });

  const available = Math.floor(table.length / font.bytesPerGlyph);
  const pages = [];
  let glyphs = 0;

  for (let start = 0; start < available; start += PAGE_SIZE) {
    const from = start * font.bytesPerGlyph;
    const to = Math.min(start + PAGE_SIZE, available) * font.bytesPerGlyph;
    const block = table.subarray(from, to);

    // Most of the BMP is unassigned; skip pages with no ink at all.
    if (!block.some((byte) => byte !== 0)) {
      continue;
    }

    for (let i = 0; i < block.length; i += font.bytesPerGlyph) {
      if (block.subarray(i, i + font.bytesPerGlyph).some((b) => b !== 0)) {
        glyphs++;
      }
    }

    const file = `u${start.toString(16).padStart(4, '0')}.bin.gz`;
    const body = gzipSync(block, { level: 9 });
    await fs.writeFile(path.join(outDir, file), body);
    pages.push({ start, file, bytes: body.length });
  }

  const manifest = {
    name: args.name,
    asset: font.asset,
    glyphWidth: font.width,
    glyphHeight: font.height,
    bytesPerGlyph: font.bytesPerGlyph,
    pageSize: PAGE_SIZE,
    glyphs,
    source: args.asset ?? `${path.basename(args.apk)}!assets/${font.asset}`,
    generated: new Date().toISOString(),
    pages,
  };

  await fs.writeFile(
    path.join(outDir, 'index.json'),
    JSON.stringify(manifest, null, 2),
  );

  const total = pages.reduce((sum, page) => sum + page.bytes, 0);
  const latin = pages.find((page) => page.start === 0);
  console.log(
    `${args.name}: ${glyphs} glyphs, ${pages.length} pages, ` +
      `${(total / 1024).toFixed(0)}KB total, ` +
      `${((latin?.bytes ?? 0) / 1024).toFixed(1)}KB for U+0000-03FF`,
  );
};

run().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
