import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  CATEGORIES,
  OTHER_CATEGORY,
  categoryOf,
  descriptionOf,
  matchesQuery,
  keywordsOf,
  parseDocRows,
} from './sampleCategories';

const sampleNames = readdirSync(
  join(dirname(fileURLToPath(import.meta.url)), '../sample'),
)
  .filter((file) => /\.(jt|json)$/.test(file))
  .map((file) => file.replace(/\.(jt|json)$/, ''));

test('every categorised name is a real sample', () => {
  // Catches typos and samples that were renamed or removed.
  const listed = CATEGORIES.flatMap((category) => category.names);
  const missing = listed.filter((name) => !sampleNames.includes(name));
  expect(missing).toEqual([]);
});

test('no sample sits in two categories', () => {
  const listed = CATEGORIES.flatMap((category) => category.names);
  expect(listed.length).toBe(new Set(listed).size);
});

test('uncategorised samples fall back to Other', () => {
  expect(categoryOf('chess_mate')).toBe('games');
  expect(categoryOf('not_a_sample')).toBe(OTHER_CATEGORY);
});

test('descriptions come from the animations doc', () => {
  expect(descriptionOf('raycaster')).toMatch(/Wolfenstein/);
  expect(keywordsOf('order_66')).toMatch(/Star Wars/);
  expect(
    parseDocRows(
      [
        '## Claude Test',
        '### Round one',
        '| `demo` | ![demo](gifs/demo.gif) | Uses `code` and **bold**. |',
      ].join('\n'),
    ),
  ).toEqual({
    demo: {
      description: 'Uses code and bold.',
      keywords: 'Claude Test Round one',
    },
  });
});

test('search matches every word across name, description and category', () => {
  const sample = {
    name: 'double_pendulum',
    category: 'science',
    description: 'Three double pendulums released 0.001 rad apart.',
    keywords: 'Claude Opus 5.5 Simulations and demos',
  };
  expect(matchesQuery(sample, '')).toBe(true);
  expect(matchesQuery(sample, 'double pendulum')).toBe(true);
  expect(matchesQuery(sample, 'RAD apart')).toBe(true);
  expect(matchesQuery(sample, 'maths')).toBe(true);
  expect(matchesQuery(sample, 'opus simulations')).toBe(true);
  expect(matchesQuery(sample, 'pendulum tetris')).toBe(false);
});
