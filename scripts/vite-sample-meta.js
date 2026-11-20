/**
 * Vite plugin: everything the Samples page needs to list samples without
 * downloading them.
 *
 * 1. `virtual:sample-meta`, a manifest of every sample in src/sample: frame
 *    count, delay and size per file, read from the files themselves. Keyed by
 *    filename, as src/helpers/samples.js keys its import.meta.glob.
 *
 * 2. A split copy of every pack in public/samples -- the two vendor packs and
 *    each material pack -- under samples/split/<pack id>/: an index.json
 *    listing every entry's name, frame count and delay, and numbered chunks
 *    of pixels (see src/helpers/packFormat.js). Emitted into the build, and
 *    served from memory by the dev server. The packs themselves are left as
 *    they are.
 *
 * Together these let the page render every card, and search them, at once,
 * and fetch pixels only for cards that near the viewport. Before, it fetched
 * every sample (~30MB for the repo's own) before showing anything.
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { gunzipSync, gzipSync } from 'node:zlib';
import { readJtMeta } from '../src/helpers/jtMeta.js';
import {
  CHUNK_SIZE,
  MATERIAL_DIR,
  SPLIT_DIR,
  VENDOR_PACKS,
  cleanVendorName,
  packChunkPath,
  packIndexPath,
  vendorEntryParts,
} from '../src/helpers/packFormat.js';

const VIRTUAL_ID = 'virtual:sample-meta';
const RESOLVED_ID = `\0${VIRTUAL_ID}`;
const SAMPLE_FILE = /\.(jt|json)$/;

export const buildSampleMeta = (dir) => {
  const meta = {};
  for (const file of readdirSync(dir).filter((name) =>
    SAMPLE_FILE.test(name),
  )) {
    try {
      meta[file] = readJtMeta(
        JSON.parse(readFileSync(join(dir, file), 'utf8')),
      );
    } catch (error) {
      // Leave it out: the page then fetches the file and reports it as
      // undecodable on its card, as before, rather than failing the build.
      console.warn(`sample-meta: skipping ${file}: ${error.message}`);
    }
  }
  return meta;
};

const readJson = (path) => {
  const bytes = readFileSync(path);
  const isGzip = bytes[0] === 0x1f && bytes[1] === 0x8b;
  return JSON.parse((isGzip ? gunzipSync(bytes) : bytes).toString('utf8'));
};

/**
 * One pack's index and chunks, as { path: JSON text }. Each entry is
 * { name, frameNum, delays, bytes, data }, `data` the packed pixel planes in
 * base64 -- the material catalog's own encoding, now used for both.
 */
const splitPack = (id, label, entries) => {
  const files = {};
  files[packIndexPath(id)] = JSON.stringify({
    id,
    label,
    count: entries.length,
    chunkSize: CHUNK_SIZE,
    items: entries.map(({ name, frameNum, delays, bytes }) => ({
      name,
      frameNum,
      delays,
      bytes,
    })),
  });
  for (let start = 0; start < entries.length; start += CHUNK_SIZE) {
    const chunk = entries.slice(start, start + CHUNK_SIZE).map((e) => e.data);
    files[packChunkPath(id, start / CHUNK_SIZE)] = gzipSync(
      JSON.stringify(chunk),
    );
  }
  return files;
};

/** Split every pack under `publicDir`. Missing packs are skipped. */
export const buildSplitPacks = (publicDir) => {
  const files = {};

  for (const pack of VENDOR_PACKS) {
    const path = join(publicDir, 'samples', pack.file);
    if (!existsSync(path)) continue;
    const entries = (readJson(path).animationData ?? []).map((entry, i) => {
      const { frameNum, delays, pixels } = vendorEntryParts(entry.sendData);
      return {
        name: cleanVendorName(entry.describe, i),
        frameNum,
        delays,
        bytes: pixels.length,
        data: Buffer.from(pixels).toString('base64'),
      };
    });
    Object.assign(files, splitPack(pack.id, pack.label, entries));
  }

  // The material catalog is optional: it exists once fetch-material has run.
  const indexPath = join(publicDir, MATERIAL_DIR, 'index.json');
  if (existsSync(indexPath)) {
    for (const pack of readJson(indexPath).packs ?? []) {
      const path = join(publicDir, MATERIAL_DIR, pack.file);
      if (!existsSync(path)) continue;
      const body = readJson(path);
      const entries = (body.items ?? []).map((item) => ({
        name: `${body.label} ${item.name}`,
        frameNum: item.frameNum,
        delays: item.delays,
        bytes: Buffer.from(item.data, 'base64').length,
        data: item.data,
      }));
      Object.assign(files, splitPack(pack.id, body.label, entries));
    }
  }

  return files;
};

export default function sampleMeta() {
  let sampleDir;
  let publicDir;
  let base = '/';

  return {
    name: 'sample-meta',
    configResolved(config) {
      sampleDir = resolve(config.root, 'src/sample');
      publicDir = config.publicDir;
      base = config.base;
    },
    resolveId(id) {
      return id === VIRTUAL_ID ? RESOLVED_ID : null;
    },
    load(id) {
      if (id !== RESOLVED_ID) {
        return null;
      }
      return `export default ${JSON.stringify(buildSampleMeta(sampleDir))};`;
    },
    generateBundle() {
      for (const [fileName, source] of Object.entries(
        buildSplitPacks(publicDir),
      )) {
        this.emitFile({ type: 'asset', fileName, source });
      }
    },
    configureServer(server) {
      // Built on first request, and again after a pack changes.
      let split = null;

      server.middlewares.use((req, res, next) => {
        const path = (req.url ?? '').split('?')[0];
        if (!path.startsWith(`${base}${SPLIT_DIR}/`)) {
          return next();
        }
        split ??= buildSplitPacks(publicDir);
        const body = split[path.slice(base.length)];
        if (body === undefined) {
          return next();
        }
        res.setHeader(
          'Content-Type',
          path.endsWith('.gz') ? 'application/gzip' : 'application/json',
        );
        res.end(body);
        return undefined;
      });

      server.watcher.on('all', (_event, file) => {
        if (file.startsWith(join(publicDir, 'samples'))) {
          split = null;
        }
        // A sample added, changed or removed rebuilds the manifest.
        if (file.startsWith(sampleDir) && SAMPLE_FILE.test(file)) {
          const module = server.moduleGraph.getModuleById(RESOLVED_ID);
          if (module) {
            server.moduleGraph.invalidateModule(module);
            server.ws.send({ type: 'full-reload' });
          }
        }
      });
    },
  };
}
