/**
 * One animation loop shared by every playing preview.
 *
 * The samples page mounts a card per sample and does not paginate -- the
 * largest material pack is over 500 -- so giving each preview its own
 * setInterval would mean hundreds of independent timers, each waking the main
 * thread on its own schedule. Instead every preview registers a callback here
 * and one requestAnimationFrame loop drives them all, so the work for a given
 * moment lands in a single frame.
 *
 * requestAnimationFrame also stops on its own while the tab is hidden, which
 * setInterval does not: timers would keep firing and queue up redraws nobody
 * can see.
 *
 * The loop only runs while something is subscribed, so an idle page costs
 * nothing.
 */

const subscribers = new Set();
let running = false;

const loop = (now) => {
  // Iterate a copy: a callback may unsubscribe itself, and mutating the set
  // mid-iteration would skip a neighbour.
  for (const advance of Array.from(subscribers)) {
    advance(now);
  }

  if (subscribers.size > 0) {
    requestAnimationFrame(loop);
  } else {
    running = false;
  }
};

/**
 * Register a callback to be invoked with a timestamp on every frame.
 * Returns an unsubscribe function.
 */
export const subscribe = (advance) => {
  subscribers.add(advance);
  if (!running) {
    running = true;
    requestAnimationFrame(loop);
  }
  return () => {
    subscribers.delete(advance);
  };
};

/** How many previews are currently playing. Exposed for debugging. */
export const playingCount = () => subscribers.size;
