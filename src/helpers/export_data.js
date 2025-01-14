import { GRID_HEIGHT, GRID_WIDTH } from './constants';

export const downloadJtFile = (imageData) => {
  const pixelArray = imageData.pixelArray;
  const originalData = reconstructGraffitiDataFromPixelArray(
    imageData,
    pixelArray,
  );
  const url = buildFile(imageData, originalData);
  // get timestamp for filename
  const timestamp = Date.now();
  const filename = `CoolLEDX_16x96_1_${timestamp}.jt`;
  downloadFile(url, filename);
};

export const buildFile = (imageData, chunks) => {
  const fileTemplate = buildTemplate(imageData, chunks);
  const json = JSON.stringify(fileTemplate);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  return url;
};

const graffitiTemplate = [
  {
    data: {
      graffitiData: [],
      graffitiType: 1,
      mode: 247,
      pixelHeight: 16,
      pixelWidth: 96,
      speed: 1,
      stayTime: 2,
    },
    dataType: 1,
  },
];

const animationTemplate = [
  {
    dataType: 0,
    data: {
      aniType: 1,
      pixelHeight: 16,
      pixelWidth: 96,
      frameNum: 3,
      delays: 300,
      aniData: [],
    },
  },
];

export const buildTemplate = (imageData, originalData) => {
  const isAnimation = imageData.isAnimation;
  const dataKey = isAnimation ? 'aniData' : 'graffitiData';
  const template = isAnimation ? [...animationTemplate] : [...graffitiTemplate];

  template[0].data[dataKey] = originalData;

  if (isAnimation) {
    template[0].data.aniType = 1;
    template[0].data.frameNum = imageData.frameNum;
  }

  return template;
};

export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
};

const convertBinaryToNumber = (binaryString) => {
  return parseInt(binaryString, 2);
};

const buildChunksFromColumn = (columnArray) => {
  let redChunk = '';
  let greenChunk = '';
  let blueChunk = '';
  for (let j = 0; j < columnArray.length; j++) {
    const pixel = columnArray[j];
    const redBit = pixel.r ? '1' : '0';
    const greenBit = pixel.g ? '1' : '0';
    const blueBit = pixel.b ? '1' : '0';
    redChunk += redBit;
    greenChunk += greenBit;
    blueChunk += blueBit;
  }
  return { redChunk, greenChunk, blueChunk };
};

const reconstructFrameFromChunks = (frameChunks) => {
  const reconstructedBinaryString =
    frameChunks.redChunks.join('') +
    frameChunks.greenChunks.join('') +
    frameChunks.blueChunks.join('');

  let originalData = [];
  for (let i = 0; i < reconstructedBinaryString.length; i += 8) {
    const num = convertBinaryToNumber(
      reconstructedBinaryString.substring(i, i + 8),
    );
    originalData.push(num);
  }

  return originalData;
};

const reconstructColorChunks = (ledArray) => {
  const redChunks = [];
  const greenChunks = [];
  const blueChunks = [];

  for (let i = 0; i < GRID_WIDTH; i++) {
    // Column start and end index
    const startIndex = i * GRID_HEIGHT;
    const endIndex = (i + 1) * GRID_HEIGHT;
    const columnArray = ledArray.slice(startIndex, endIndex);

    const columnChunks = buildChunksFromColumn(columnArray);
    redChunks.push(...columnChunks.redChunk);
    greenChunks.push(...columnChunks.greenChunk);
    blueChunks.push(...columnChunks.blueChunk);
  }

  return { redChunks, greenChunks, blueChunks };
};

const reconstructGraffitiDataFromPixelArray = (imageData, pixelArray) => {
  const frames = imageData.frameNum;

  let originalData = [];
  for (let i = 0; i < frames; i++) {
    const arrayOffset = i * GRID_WIDTH * GRID_HEIGHT;
    const frameArray = pixelArray.slice(
      arrayOffset,
      arrayOffset + GRID_HEIGHT * GRID_WIDTH,
    );

    const frameChunks = reconstructColorChunks(frameArray);
    const frameData = reconstructFrameFromChunks(frameChunks);
    originalData = originalData.concat(frameData);
  }

  return originalData;
};
