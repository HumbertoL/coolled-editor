#!/usr/bin/env node
/**
 * Pull the CoolLED1248 material catalog into public/samples/material/.
 *
 * The catalog lives on the vendor's CDN, which serves plain HTTP with no CORS
 * headers, so the browser cannot read it directly -- same reason the two
 * animation packs in public/samples/ are vendored. This script does the
 * fetching, un-obfuscates the GIFs, converts each one to the panel's packed
 * pixel format with the same code the editor's GIF import uses, and writes one
 * pack per category (gzipped JSON) plus an index.
 *
 *   node scripts/fetch-material.mjs                  # sc + fc at 16x96
 *   node scripts/fetch-material.mjs --dir fc --only emoji,festival
 *   node scripts/fetch-material.mjs --size 16x64 --out public/samples/material
 *
 * See docs/VENDOR_DATA.md for how the endpoints fit together.
 */
import fs from 'fs/promises';
import path from 'path';
import { gzipSync } from 'zlib';
import { GRID_HEIGHT, GRID_WIDTH } from '../src/helpers/constants.js';
import {
  deobfuscateMaterialGif,
  gifToImageData,
} from '../src/helpers/gif_utils.js';
import { packPixelArray } from '../src/helpers/export_data.js';

const DEVICE_CONFIG_URL = 'http://www.coolledx.com/CoolLEDX/CoolLEDX/config.json';
const DEFAULT_OUT = 'public/samples/material';
const DEFAULT_DIRS = ['sc', 'fc'];
const CONCURRENCY = 8;
const RETRIES = 3;

const parseArgs = (argv) => {
  const args = { dirs: DEFAULT_DIRS, size: `${GRID_HEIGHT}x${GRID_WIDTH}`, out: DEFAULT_OUT, only: null };
  for (let i = 0; i < argv.length; i += 2) {
    const value = argv[i + 1];
    switch (argv[i]) {
      case '--dir':
        args.dirs = value.split(',');
        break;
      case '--size':
        args.size = value;
        break;
      case '--out':
        args.out = value;
        break;
      case '--only':
        args.only = value.split(',');
        break;
      default:
        throw new Error(`Unknown option ${argv[i]}`);
    }
  }
  return args;
};

const fetchWithRetry = async (url, as) => {
  let lastError;
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      return as === 'json' ? response.json() : new Uint8Array(await response.arrayBuffer());
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
    }
  }
  throw new Error(`${url}: ${lastError.message}`);
};

/** Run tasks with a fixed number in flight, keeping input order. */
const mapLimit = async (items, limit, worker) => {
  const results = new Array(items.length);
  let next = 0;

  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const index = next++;
      results[index] = await worker(items[index], index);
    }
  });

  await Promise.all(runners);
  return results;
};

/** Strip the vendor's naming ("sc_16x96_2_51.gif") down to something readable. */
const itemName = (file, index) => {
  const stem = file.replace(/\.gif$/i, '');
  const trailing = stem.match(/(\d+(?:_\d+)?)$/);
  return trailing ? `#${trailing[1].replace('_', '.')}` : `#${index + 1}`;
};

const convertItem = async (baseUrl, file, index) => {
  const raw = await fetchWithRetry(`${baseUrl}/${file}`);
  const bytes = deobfuscateMaterialGif(raw);
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);

  const image = gifToImageData(buffer);
  const packed = packPixelArray(image.pixelArray, image.frameNum);

  return {
    name: itemName(file, index),
    file,
    frameNum: image.frameNum,
    delays: image.delays,
    data: Buffer.from(packed).toString('base64'),
  };
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));

  if (args.size !== `${GRID_HEIGHT}x${GRID_WIDTH}`) {
    console.warn(
      `Note: the editor is built for ${GRID_HEIGHT}x${GRID_WIDTH}; ` +
        `${args.size} items will be centred and cropped to fit.`,
    );
  }

  const config = await fetchWithRetry(DEVICE_CONFIG_URL, 'json');
  console.log(`material_url: ${config.material_url}`);

  await fs.mkdir(args.out, { recursive: true });
  const packs = [];

  for (const dir of args.dirs) {
    const categoryUrl = `${config.material_url}/${dir}/${args.size}/category.json`;

    let categories;
    try {
      ({ category: categories } = await fetchWithRetry(categoryUrl, 'json'));
    } catch (error) {
      console.warn(`skipping ${dir}/${args.size}: ${error.message}`);
      continue;
    }

    for (const category of categories) {
      const slug = category.url.replace(/\/+$/, '').split('/').pop();
      if (args.only && !args.only.includes(slug)) {
        continue;
      }

      const listing = await fetchWithRetry(`${category.url}/list_en.json`, 'json');
      const files = listing.list ?? [];

      const items = await mapLimit(files, CONCURRENCY, async (file, index) => {
        try {
          return await convertItem(listing.baseUrl, file, index);
        } catch (error) {
          console.warn(`  ${file}: ${error.message}`);
          return null;
        }
      });

      const converted = items.filter(Boolean);
      const id = `material-${dir}-${slug}`;
      // Gzipped on disk: the packed planes are extremely repetitive, so this
      // is ~20x smaller in the repo and over the wire. The samples page
      // inflates it with DecompressionStream.
      const file = `${id}.json.gz`;

      const body = gzipSync(
        Buffer.from(
          JSON.stringify({
            id,
            label: category.name?.en ?? slug,
            names: category.name ?? {},
            colorDir: dir,
            size: args.size,
            slug,
            source: category.url,
            generated: new Date().toISOString(),
            items: converted,
          }),
        ),
        { level: 9 },
      );
      await fs.writeFile(path.join(args.out, file), body);

      const size = body.length;
      packs.push({
        id,
        file,
        label: category.name?.en ?? slug,
        colorDir: dir,
        size: args.size,
        slug,
        count: converted.length,
        bytes: size,
      });

      console.log(
        `${dir}/${slug}: ${converted.length}/${files.length} items, ` +
          `${(size / 1024).toFixed(0)}KB`,
      );
    }
  }

  await fs.writeFile(
    path.join(args.out, 'index.json'),
    JSON.stringify({ generated: new Date().toISOString(), packs }, null, 2),
  );

  const total = packs.reduce((sum, pack) => sum + pack.count, 0);
  console.log(`\n${packs.length} packs, ${total} items`);
};

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
