import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildSampleMeta } from '../../scripts/vite-sample-meta.js';
import { BYTES_PER_FRAME, readJtMeta } from './jtMeta';

const sampleDir = join(dirname(fileURLToPath(import.meta.url)), '../sample');
const sampleFiles = readdirSync(sampleDir).filter((file) =>
  /\.(jt|json)$/.test(file),
);

test('the build-time manifest describes every sample', () => {
  // A sample missing here would still load, but show "Loading…" until its
  // card is scrolled to: a sign the manifest and the glob have drifted.
  const meta = buildSampleMeta(sampleDir);
  expect(Object.keys(meta).sort()).toEqual([...sampleFiles].sort());
});

test('manifest frame counts come from the pixel data', () => {
  const meta = buildSampleMeta(sampleDir);
  for (const file of ['LFG.jt', 'turkey_strut.jt']) {
    const jt = JSON.parse(readFileSync(join(sampleDir, file), 'utf8'));
    const pixels = jt[0].data.aniData ?? jt[0].data.graffitiData;
    expect(meta[file]).toEqual(readJtMeta(jt));
    expect(meta[file].frameNum).toBe(pixels.length / BYTES_PER_FRAME);
  }
});
