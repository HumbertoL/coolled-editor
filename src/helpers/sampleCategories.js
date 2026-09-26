/**
 * How the samples in src/sample are grouped on the Samples page, and the
 * descriptions its search reads.
 *
 * Categories are listed by hand: a new sample dropped into src/sample still
 * shows up without touching this file, just under "Other" until it is added
 * to a list here. Descriptions come from the tables in docs/AI_ANIMATIONS.md,
 * so a row added there is searchable with no extra step; the few samples
 * without a row (hand-drawn or editor exports) get one in EXTRA_DESCRIPTIONS.
 */
import animationsDoc from '../../docs/AI_ANIMATIONS.md?raw';

export const OTHER_CATEGORY = 'other';

export const CATEGORIES = [
  {
    id: 'tea',
    label: 'Text-Em-All',
    names: [
      'TEA_purpose',
      'campaign_sent',
      'sms_bubbles',
      'tea_broadcast',
      'tea_delivered',
      'tea_heartbeat',
      'tea_network',
      'tea_optin',
      'tea_poll',
      'tea_uptime',
      'tea_voice',
      'tea_wordmark',
    ],
  },
  {
    id: 'office',
    label: 'Office & desk',
    names: [
      '0DayVelociratpr',
      '3DayVelociraptr',
      '4DayVelociraptor',
      '5DayVelociraptor',
      'LFG',
      'PancakesVWaffles',
      'breathing',
      'chaos_corner',
      'coffee',
      'humberto',
      'hype_meter',
      'letters_dance',
      'riddle',
      'status_brb',
      'status_focus',
      'status_on_a_call',
      'team_name',
      'welcome_to_chaos_corner',
    ],
  },
  {
    id: 'code',
    label: 'Code & nerd humour',
    names: [
      'attention',
      'bios',
      'bug_hunt',
      'captcha',
      'deploy',
      'eta',
      'git_log',
      'gradient_descent',
      'hello_world',
      'neural_net',
      'spicy_autocomplete',
      'temperature',
      'tests_passing',
      'turing_machine',
    ],
  },
  {
    id: 'memes',
    label: 'Memes',
    names: [
      'PartyParrot',
      'all_your_base',
      'among_us',
      'bongo_cat',
      'crab_rave',
      'deal_with_it',
      'distracted_boyfriend',
      'doge',
      'drake',
      'galaxy_brain',
      'grumpy_cat',
      'hellmo_ring',
      'high_five',
      'leeroy_jenkins',
      'loss',
      'moo_deng',
      'nyan_cat',
      'oh_yeah',
      'over_9000',
      'road_work_ahead',
      'stonks',
      'thanos_snap',
      'the_dress',
      'this_is_fine',
      'this_is_sparta',
      'wednesday_frog',
      'zoomies',
    ],
  },
  {
    id: 'screen',
    label: 'Films, TV & books',
    names: [
      'Believe',
      'amaze',
      'chosen_one',
      'dftba',
      'eye_of_sauron',
      'fun_begins',
      'hamilton_duel',
      'hamilton_shot',
      'hello_there',
      'high_ground',
      'i_am_the_senate',
      'i_dont_like_sand',
      'marauders_map',
      'order_66',
      'the_door',
      'unlimited_power',
    ],
  },
  {
    id: 'dcc',
    label: 'Dungeon Crawler Carl',
    names: [
      'dcc_boss_battle',
      'dcc_collapse',
      'dcc_followers',
      'dcc_goddammit_donut',
      'dcc_level_up',
      'dcc_loot_box',
      'dcc_new_achievement',
    ],
  },
  {
    id: 'games',
    label: 'Games',
    names: [
      'AnimalWellBlink',
      'asteroids',
      'breakout',
      'chess_mate',
      'd20_nat1',
      'd20_nat20',
      'dnd_dragon',
      'dnd_fireball',
      'dnd_hp',
      'flappy',
      'frogger',
      'invaders',
      'key_quest',
      'konami',
      'lightcycles',
      'lunar_lander',
      'pacman',
      'pinball',
      'pong',
      'portal',
      'slot_machine',
      'snake',
      'tamagotchi',
      'tetris',
      'triforce',
      'waldo',
      'wordle',
    ],
  },
  {
    id: 'science',
    label: 'Science & maths',
    names: [
      'bifurcation',
      'collatz',
      'coral',
      'double_pendulum',
      'double_slit',
      'eclipse',
      'galaxy',
      'glider_gun',
      'julia',
      'langtons_ant',
      'life',
      'lissajous',
      'lorenz',
      'maze',
      'mitosis',
      'murmuration',
      'orbit',
      'rule30',
      'seismograph',
      'sierpinski',
      'signal',
      'slime_mold',
      'sorting',
      'spirograph',
      'traffic_wave',
      'turing_patterns',
      'waggle_dance',
    ],
  },
  {
    id: 'satisfying',
    label: 'Satisfying',
    names: [
      'ball_sort',
      'bounce',
      'bubble_wrap',
      'dominoes',
      'flip_disc',
      'gears',
      'hourglass',
      'loom',
      'newtons_cradle',
      'pendulum_wave',
      'sand_art',
      'stack_tower',
      'tusi_couple',
      'zipper',
    ],
  },
  {
    id: 'effects',
    label: 'Effects & demoscene',
    names: [
      'copper_bars',
      'cubes',
      'donut_dvd',
      'equalizer',
      'fire',
      'globe',
      'hazard',
      'heartbeat',
      'helix',
      'hyperspace',
      'kaleidoscope',
      'matrix',
      'metaballs',
      'pipes',
      'plasma',
      'raycaster',
      'ripples',
      'sonar',
      'stained_glass',
      'starfield',
      'torus',
      'tunnel',
      'wave',
      'waveform',
    ],
  },
  {
    id: 'scenes',
    label: 'Scenes & nature',
    names: [
      'RooftopTerrace2',
      'aquarium',
      'aurora',
      'cassette',
      'constellation',
      'eyes',
      'fireflies',
      'fireworks',
      'flag',
      'lighthouse',
      'lightning',
      'night_drive',
      'pigeon',
      'popcorn',
      'rain',
      'rocket',
      'rooftop',
      'snow',
      'sunrise',
      'timelapse_garden',
      'tiny_village',
      'train',
      'washing_machine',
    ],
  },
  {
    id: 'puzzles',
    label: 'Puzzles',
    names: ['spot_the_difference', 'word_ladder'],
  },
  {
    id: 'antics',
    label: 'Sign antics',
    names: ['ghost_in_the_machine', 'peek', 'staring_contest', 'stick_fight'],
  },
  {
    id: 'tests',
    label: 'Sign tests',
    names: [
      'bit_order',
      'column_markers',
      'frame_ladder_test_113',
      'frame_ladder_test_53',
      'warning',
    ],
  },
];

const CATEGORY_OF = new Map(
  CATEGORIES.flatMap((category) =>
    category.names.map((name) => [name, category.id]),
  ),
);

export const categoryOf = (name) => CATEGORY_OF.get(name) ?? OTHER_CATEGORY;

export const categoryLabel = (id) =>
  CATEGORIES.find((category) => category.id === id)?.label ?? 'Other';

// Samples with no row in docs/AI_ANIMATIONS.md: drawn in the editor or
// written as hardware probes rather than generated.
const EXTRA_DESCRIPTIONS = {
  '0DayVelociratpr': 'Days since the last velociraptor attack: 0.',
  '3DayVelociraptr': 'Days since the last velociraptor attack: 3.',
  '4DayVelociraptor': 'Days since the last velociraptor attack: 4.',
  '5DayVelociraptor': 'Days since the last velociraptor attack: 5.',
  AnimalWellBlink: 'A blink, from the game Animal Well.',
  Believe: 'The BELIEVE sign from Ted Lasso.',
  LFG: "LFG -- let's go.",
  PancakesVWaffles: 'Pancakes versus waffles.',
  PartyParrot: 'The party parrot.',
  RooftopTerrace2: 'A rooftop terrace scene.',
  TEA_purpose: 'The Text-Em-All purpose statement.',
  column_markers: 'Coloured columns at both edges, for checking orientation.',
  frame_ladder_test_113:
    'Frame counter test: 113 frames, the protocol ceiling.',
  frame_ladder_test_53: 'Frame counter test: 53 frames, the device maximum.',
  pacman: 'Pac-Man chased by four ghosts along a row of dots.',
  warning: 'Hand-drawn WARNING in red, used to probe the wire format.',
  welcome_to_chaos_corner: 'WELCOME TO CHAOS CORNER.',
};

const ROW = /^\| `(\w+)` \| .*? \| (.*) \|$/;

/**
 * Name -> { description, keywords } from the doc's tables. First row wins.
 * Keywords are the headings the row sits under -- the model that made it
 * and the brief ("Round two: the Star Wars prequels") -- which often say
 * what the description takes for granted.
 */
export const parseDocRows = (markdown) => {
  const rows = {};
  let model = '';
  let section = '';
  for (const line of markdown.split('\n')) {
    if (line.startsWith('## ')) {
      model = line.slice(3);
      section = '';
    } else if (line.startsWith('### ')) {
      section = line.slice(4);
    }
    const match = ROW.exec(line);
    if (match && !(match[1] in rows)) {
      rows[match[1]] = {
        // Strip markdown the card would show literally.
        description: match[2].replace(/`/g, '').replace(/\*\*/g, ''),
        keywords: [model, section].filter(Boolean).join(' '),
      };
    }
  }
  return rows;
};

const DOC_ROWS = parseDocRows(animationsDoc);

export const descriptionOf = (name) =>
  EXTRA_DESCRIPTIONS[name] ?? DOC_ROWS[name]?.description ?? '';

export const keywordsOf = (name) => DOC_ROWS[name]?.keywords ?? '';

/**
 * Does a sample match a search? Every word must appear somewhere in its
 * name, description, keywords or category, so "star wars" or "pendulum chaos" narrow
 * rather than widen. Underscores in names count as spaces.
 */
export const matchesQuery = (sample, query) => {
  const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  if (words.length === 0) return true;
  const haystack = [
    sample.name,
    sample.name.replace(/_/g, ' '),
    sample.description ?? '',
    sample.keywords ?? '',
    sample.category ? categoryLabel(sample.category) : '',
  ]
    .join(' ')
    .toLowerCase();
  return words.every((word) => haystack.includes(word));
};
