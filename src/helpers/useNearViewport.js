import { useEffect, useState } from 'react';

/**
 * Whether the element behind `ref` is within `margin` of the viewport.
 *
 * With `once`, it latches: true from the first time the element comes near,
 * and the observer is dropped. That suits loading data, which should happen
 * once; without it, it tracks the element in and out, which suits playback.
 *
 * Where IntersectionObserver is missing (jsdom, very old engines) it reports
 * true, so nothing is left permanently unloaded or unplayed.
 */
const useNearViewport = (ref, { margin = '0px', once = false } = {}) => {
  const [near, setNear] = useState(
    () => typeof IntersectionObserver === 'undefined',
  );

  useEffect(() => {
    const element = ref.current;
    if (!element || typeof IntersectionObserver === 'undefined') {
      return undefined;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        setNear(entry.isIntersecting);
        if (once && entry.isIntersecting) {
          observer.disconnect();
        }
      },
      { rootMargin: margin },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, margin, once]);

  return near;
};

export default useNearViewport;
