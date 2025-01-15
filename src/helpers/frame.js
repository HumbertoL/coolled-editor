import { GRID_HEIGHT, GRID_WIDTH } from './constants';

const FRAME_OFFSET = GRID_HEIGHT * GRID_WIDTH;

export const getStartingPixel = (frame) => {
  return frame === 1 ? 0 : FRAME_OFFSET * (frame - 1);
};

export const getFrameData = (pixelArray, frame) => {
  const startingPixel = getStartingPixel(frame);
  const frameData = pixelArray.slice(
    startingPixel,
    startingPixel + FRAME_OFFSET,
  );
  return frameData;
};

export const insertFrame = (pixelArray, selectedFrame, frameData) => {
  const newFrameData = [...pixelArray];
  const frameIndex = selectedFrame - 1;
  newFrameData.splice(frameIndex * FRAME_OFFSET, 0, ...frameData);
  return newFrameData;
};
