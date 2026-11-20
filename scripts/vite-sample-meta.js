/**
 * Vite plugin: `virtual:sample-meta`, a manifest of every sample in
 * src/sample, built from the files themselves.
 *
 * The Samples page used to fetch and parse all ~30MB of .jt files before it
 * could show a single card. With this it knows each sample's frame count,
 * delay and size up front, renders every card (and searches them) at once,
 * and fetches a sample's pixels only when its card nears the viewport.
 *
 * The manifest is keyed by filename, the same way src/helpers/samples.js
 * keys its import.meta.glob, so the two always describe the same files.
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { readJtMeta } from '../src/helpers/jtMeta.js';

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

export default function sampleMeta() {
  let dir;

  return {
    name: 'sample-meta',
    configResolved(config) {
      dir = resolve(config.root, 'src/sample');
    },
    resolveId(id) {
      return id === VIRTUAL_ID ? RESOLVED_ID : null;
    },
    load(id) {
      if (id !== RESOLVED_ID) {
        return null;
      }
      return `export default ${JSON.stringify(buildSampleMeta(dir))};`;
    },
    configureServer(server) {
      // A sample added, changed or removed in dev rebuilds the manifest.
      const refresh = (file) => {
        if (!file.startsWith(dir) || !SAMPLE_FILE.test(file)) {
          return;
        }
        const module = server.moduleGraph.getModuleById(RESOLVED_ID);
        if (module) {
          server.moduleGraph.invalidateModule(module);
          server.ws.send({ type: 'full-reload' });
        }
      };
      server.watcher.on('add', refresh);
      server.watcher.on('change', refresh);
      server.watcher.on('unlink', refresh);
    },
  };
}
