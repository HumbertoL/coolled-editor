import { GRID_HEIGHT, GRID_WIDTH } from './constants.js';

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
  // Returned so the UI can show the exact path in the deploy command.
  return filename;
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
    template[0].data.delays = imageData.delays;
  }

  return template;
};

export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
};

/**
 * Pack a pixel array into the byte layout a .jt file carries.
 *
 * Three colour planes span the whole animation rather than sitting inside
 * each frame: every frame's red bits, then green, then blue. Within a plane
 * the frames sit side by side, each walking down its columns. Same layout
 * parse_data.js and samples.js read back.
 */
export const packPixelArray = (pixelArray, frameNum) => {
  const pixelsPerFrame = GRID_WIDTH * GRID_HEIGHT;
  const planeBits = frameNum * pixelsPerFrame;
  const bytes = new Uint8Array((planeBits * 3) / 8);

  const setBit = (bitIndex) => {
    bytes[bitIndex >> 3] |= 0x80 >> (bitIndex & 7);
  };

  for (let frame = 0; frame < frameNum; frame++) {
    for (let column = 0; column < GRID_WIDTH; column++) {
      for (let row = 0; row < GRID_HEIGHT; row++) {
        const pixel =
          pixelArray[frame * pixelsPerFrame + column * GRID_HEIGHT + row];
        if (!pixel) continue;

        const bitIndex = (frame * GRID_WIDTH + column) * GRID_HEIGHT + row;
        if (pixel.r) setBit(bitIndex);
        if (pixel.g) setBit(planeBits + bitIndex);
        if (pixel.b) setBit(planeBits * 2 + bitIndex);
      }
    }
  }

  return bytes;
};

const reconstructGraffitiDataFromPixelArray = (imageData, pixelArray) =>
  Array.from(packPixelArray(pixelArray, imageData.frameNum ?? 1));
