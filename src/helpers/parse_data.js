// import welcome from '../sample/welcome_to_chaos_corner.json';
// import greenTopRight from '../sample/green_top_right.json';

import { GRID_HEIGHT, GRID_WIDTH } from './constants';

export const parseData = (content) => {
  const imageData = convertDataToBinary(content);

  const columns = separateIntoColumns(imageData.binaryString);
  const colorArrays = divideColumnsIntoRGBGroups(columns);
  const pixelArray = buildLedArray(imageData, colorArrays);

  delete imageData.binaryString;

  const imageObject = {
    ...imageData,
    pixelArray,
  };

  return imageObject;
};

function convertToBinary(num) {
  if (num < 0 || num > 255 || isNaN(num) || !Number.isInteger(num)) {
    return 'Invalid input: Please provide a number between 0 and 255.';
  }

  return ('00000000' + num.toString(2)).slice(-8);
}

export const convertDataToBinary = (content) => {
  const parsedJson = JSON.parse(content);
  const parsedData = parsedJson[0].data;
  const graffitiData = parsedData.graffitiData;
  const animationData = parsedData.aniData;
  const isAnimation = Boolean(parsedData.aniType);
  const frameNum = parsedData.frameNum ?? 1;
  const pixelWidth = parsedData.pixelWidth;
  const pixelHeight = parsedData.pixelHeight;
  const delays = parsedData.delays;

  // If no graffiti data, fall back to animation data
  const imageData = isAnimation ? animationData : graffitiData;

  // combine into one string
  const binaryString = imageData.reduce(function (result, currentNum) {
    return result + convertToBinary(currentNum);
  }, '');

  const imageObject = {
    binaryString,
    isAnimation,
    frameNum,
    pixelWidth,
    pixelHeight,
    delays,
  };

  return imageObject;
};

// Each column is represent by 16bits
const CHUNK_SIZE = 16;
const separateIntoColumns = (binaryString) => {
  const chunks = [];
  for (let i = 0; i < binaryString.length; i += CHUNK_SIZE) {
    chunks.push(binaryString.substring(i, i + CHUNK_SIZE));
  }
  return chunks;
};

// The first 3rd of the data represents whether Red is on or off
// The second 3rd of the data represents whether Green is on or off
// The last 3rd of the data represents whether Blue is on or off
const divideColumnsIntoRGBGroups = (chunks) => {
  const totalChunks = chunks.length;
  const oneThird = totalChunks / 3;

  const redChunks = chunks.slice(0, oneThird);
  const greenChunks = chunks.slice(oneThird, 2 * oneThird);
  const blueChunks = chunks.slice(2 * oneThird);

  return { redChunks, greenChunks, blueChunks };
};

// Each column is represented by 16 bits.
// The first bit is in the top left corner of the grid.
// The next bit is in the row below that, and so on.
// e.x. 1000000000000001 represents the top left and bottom left pixels being on.
// However, there's 3 groups of data in the array.
// The groups are for Red, Green, and Blue.
const buildColumn = (colorChunks, index) => {
  const columnRed = colorChunks.redChunks[index];
  const columnGreen = colorChunks.greenChunks[index];
  const columnBlue = colorChunks.blueChunks[index];

  const columnArray = [];
  for (let j = 0; j < GRID_HEIGHT; j++) {
    const isRedOn = columnRed[j] === '1';
    const isGreenOn = columnGreen[j] === '1';
    const isBlueOn = columnBlue[j] === '1';
    const pixel = { r: isRedOn, g: isGreenOn, b: isBlueOn };
    columnArray.push(pixel);
  }

  return columnArray;
};

const buildLedFrame = (colorChunks) => {
  const ledArray = [];

  for (let i = 0; i < GRID_WIDTH; i++) {
    // Build up the rows
    const column = buildColumn(colorChunks, i);
    ledArray.push(...column);
  }

  return ledArray;
};

const getFrameChunks = (chunkSize, frameIndex, colorChunks) => {
  const chunkOffset = frameIndex * chunkSize;
  const frameChunks = colorChunks.slice(chunkOffset, chunkOffset + chunkSize);

  return frameChunks;
};

const buildLedArray = (imageObject, colorChunks) => {
  const frameArray = [];
  const numFrames = imageObject.frameNum;

  const chunkSize = imageObject.pixelWidth;

  for (let i = 0; i < numFrames; i++) {
    // const chunkOffset = i * chunkSize;

    const redChunks = getFrameChunks(chunkSize, i, colorChunks.redChunks);
    const greenChunks = getFrameChunks(chunkSize, i, colorChunks.greenChunks);
    const blueChunks = getFrameChunks(chunkSize, i, colorChunks.blueChunks);

    const frameChunks = {
      redChunks,
      greenChunks,
      blueChunks,
    };

    // TODO
    const chunkArray = buildLedFrame(frameChunks);
    frameArray.push(...chunkArray);
  }

  return frameArray;
};
