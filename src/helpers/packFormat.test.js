import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync } from 'node:zlib';
import { buildSplitPacks } from '../../scripts/vite-sample-meta.js';
import {
  CHUNK_SIZE,
  MATERIAL_DIR,
  VENDOR_PACKS,
  packChunkPath,
  packIndexPath,
} from './packFormat';
import { materialEntryToJt, readJt, vendorEntryToJt } from './samples';

const publicDir = join(dirname(fileURLToPath(import.meta.url)), '../../public');
const split = buildSplitPacks(publicDir);

const readPack = (path) => {
  const bytes = readFileSync(join(publicDir, path));
  const isGzip = bytes[0] === 0x1f && bytes[1] === 0x8b;
  return JSON.parse((isGzip ? gunzipSync(bytes) : bytes).toString('utf8'));
};

/** Rebuild every entry of a split pack the way the page does. */
const fromSplit = (packId) => {
  const index = JSON.parse(split[packIndexPath(packId)]);
  expect(index.chunkSize).toBe(CHUNK_SIZE);
  const chunks = new Map();
  return index.items.map((item, i) => {
    const chunkIndex = Math.floor(i / CHUNK_SIZE);
    if (!chunks.has(chunkIndex)) {
      const gz = split[packChunkPath(packId, chunkIndex)];
      chunks.set(chunkIndex, JSON.parse(gunzipSync(gz).toString('utf8')));
    }
    const data = chunks.get(chunkIndex)[i % CHUNK_SIZE];
    const jt = materialEntryToJt({ ...item, data });
    // What the card showed before loading must match what it shows after.
    expect(readJt(jt).frameNum).toBe(Math.max(1, Math.round(item.bytes / 576)));
    return jt;
  });
};

// Compared as JSON: deep equality on ~2,000 pixel arrays is slow.
const same = (a, b) => expect(JSON.stringify(a)).toBe(JSON.stringify(b));

test.each(VENDOR_PACKS.map((pack) => [pack.id, pack.file]))(
  'the split %s pack gives back every vendor entry exactly',
  (packId, file) => {
    const original = readPack(`samples/${file}`).animationData;
    const rebuilt = fromSplit(packId);
    expect(rebuilt.length).toBe(original.length);
    rebuilt.forEach((jt, i) => same(jt, vendorEntryToJt(original[i].sendData)));
  },
);

test('every split material pack gives back every entry exactly', () => {
  const { packs } = readPack(`${MATERIAL_DIR}/index.json`);
  expect(packs.length).toBeGreaterThan(0);
  for (const pack of packs) {
    const original = readPack(`${MATERIAL_DIR}/${pack.file}`).items;
    const rebuilt = fromSplit(pack.id);
    expect(rebuilt.length).toBe(original.length);
    rebuilt.forEach((jt, i) => same(jt, materialEntryToJt(original[i])));
  }
}, 60_000);
