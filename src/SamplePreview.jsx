import { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { GRID_HEIGHT, GRID_WIDTH } from './helpers/constants';
import { drawFrame, firstLitFrame } from './helpers/samples';
import { subscribe } from './helpers/previewTicker';
import useNearViewport from './helpers/useNearViewport';

const Canvas = styled.canvas`
  display: block;
  width: 100%;
  height: auto;
  background: #05050a;
  border-radius: 6px;
  /* One canvas pixel per LED, scaled up by CSS. */
  image-rendering: pixelated;
`;

// Start playing slightly before a card scrolls into view, so it is already
// moving by the time it is looked at.
const NEAR_VIEWPORT = '150px';

const REDUCED_MOTION = '(prefers-reduced-motion: reduce)';

const useReducedMotion = () => {
  const [reduced, setReduced] = useState(
    () =>
      typeof window !== 'undefined' &&
      window.matchMedia &&
      window.matchMedia(REDUCED_MOTION).matches,
  );

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) {
      return undefined;
    }
    const query = window.matchMedia(REDUCED_MOTION);
    const onChange = (event) => setReduced(event.matches);
    query.addEventListener('change', onChange);
    return () => query.removeEventListener('change', onChange);
  }, []);

  return reduced;
};

/**
 * A 96x16 preview of one sample.
 *
 * Multi-frame samples play on their own once scrolled into view. Hovering
 * still forces playback, which is what someone who has asked for reduced
 * motion gets instead of autoplay.
 *
 * Without `pixelBytes` (a sample whose data has not arrived yet) it is an
 * empty panel of the same size, so the card does not jump when it loads.
 *
 * Playback is limited to cards near the viewport: the samples page does not
 * paginate -- one material pack is over 500 cards -- and only a dozen or so
 * are ever actually on screen.
 */
const SamplePreview = ({ pixelBytes, frameNum, delays, isHovered }) => {
  const canvasRef = useRef(null);
  const near = useNearViewport(canvasRef, { margin: NEAR_VIEWPORT });
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !pixelBytes) {
      return undefined;
    }
    const ctx = canvas.getContext('2d');
    const poster = firstLitFrame(pixelBytes, frameNum);

    const shouldPlay = frameNum > 1 && (isHovered || (near && !reducedMotion));

    if (!shouldPlay) {
      drawFrame(ctx, pixelBytes, poster, frameNum);
      return undefined;
    }

    // The sign treats `delays` as milliseconds per frame. Clamp it: a sample
    // asking for 10ms would just burn frames nobody can follow.
    const period = Math.max(60, Number(delays) || 100);
    let frame = 0;
    let previous = performance.now();
    drawFrame(ctx, pixelBytes, frame, frameNum);

    // Shared loop rather than a timer per preview -- see previewTicker.
    const unsubscribe = subscribe((now) => {
      const elapsed = now - previous;
      if (elapsed < period) {
        return;
      }
      // Advance by however many periods actually passed, so a stalled frame
      // does not leave this preview permanently behind the others.
      const steps = Math.floor(elapsed / period);
      previous += steps * period;
      frame = (frame + steps) % frameNum;
      drawFrame(ctx, pixelBytes, frame, frameNum);
    });

    return () => {
      unsubscribe();
      drawFrame(ctx, pixelBytes, poster, frameNum);
    };
  }, [pixelBytes, frameNum, delays, isHovered, near, reducedMotion]);

  return <Canvas ref={canvasRef} width={GRID_WIDTH} height={GRID_HEIGHT} />;
};

export default SamplePreview;
