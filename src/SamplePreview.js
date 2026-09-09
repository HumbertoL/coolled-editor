import { useEffect, useRef } from 'react';
import styled from 'styled-components';
import { GRID_HEIGHT, GRID_WIDTH } from './helpers/constants';
import { drawFrame, firstLitFrame } from './helpers/samples';

const Canvas = styled.canvas`
  display: block;
  width: 100%;
  height: auto;
  background: #05050a;
  border-radius: 6px;
  /* One canvas pixel per LED, scaled up by CSS. */
  image-rendering: pixelated;
`;

/**
 * A 96x16 preview of one sample. Renders the first frame, and cycles through
 * the rest while hovered so animations can be told apart without opening them.
 */
const SamplePreview = ({ pixelBytes, frameNum, delays, isHovered }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return undefined;
    }
    const ctx = canvas.getContext('2d');

    const poster = firstLitFrame(pixelBytes, frameNum);

    if (!isHovered || frameNum <= 1) {
      drawFrame(ctx, pixelBytes, poster);
      return undefined;
    }

    let frame = 0;
    // The sign treats `delays` as milliseconds per frame.
    const interval = setInterval(
      () => {
        frame = (frame + 1) % frameNum;
        drawFrame(ctx, pixelBytes, frame);
      },
      Math.max(60, delays),
    );

    return () => {
      clearInterval(interval);
      drawFrame(ctx, pixelBytes, poster);
    };
  }, [pixelBytes, frameNum, delays, isHovered]);

  return <Canvas ref={canvasRef} width={GRID_WIDTH} height={GRID_HEIGHT} />;
};

export default SamplePreview;
