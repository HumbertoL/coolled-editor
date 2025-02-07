import { parseGIF, decompressFrames } from 'gifuct-js';
import { GRID_HEIGHT, GRID_WIDTH } from './constants';

const colorMap = [
  // black
  {
    source: { r: 0, g: 0, b: 0 },
    target: { r: false, g: false, b: false },
  },
  // undefined becomes black
  {
    source: { r: undefined, g: undefined, b: undefined },
    target: { r: true, g: true, b: false },
  },
  // white
  {
    source: { r: 255, g: 255, b: 255 },
    target: { r: false, g: false, b: false },
  },
  // magenta
  {
    source: { r: 255, g: 110, b: 124 },
    target: { r: false, g: true, b: false },
  },
  // cyan
  {
    source: { r: 187, g: 226, b: 213 },
    target: { r: false, g: true, b: true },
  },
  // // 255, 141, 139 to magenta
  {
    source: { r: 255, g: 141, b: 139 },
    target: { r: false, g: true, b: false },
  },
  // // 254, 214, 137 to yellow
  // {
  //   source: { r: 254, g: 214, b: 137 },
  //   target: { r: false, g: true, b: true },
  // },
];

const totalPixels = GRID_HEIGHT * GRID_WIDTH;
const initialValue = { r: false, g: false, b: false };
const centerOffset = 16 * 36;

export const getGifBitmaps = async (frames) => {
  const bitmaps = frames.map((frame, index) => {
    const { patch, dims } = frame;
    const { width, height } = dims;

    // Create bitmap array from patch data
    const bitmap = new Array(height);
    for (let y = 0; y < height; y++) {
      bitmap[y] = new Array(width);
      for (let x = 0; x < width; x++) {
        const i = (y * width + x) * 4;
        bitmap[y][x] = {
          r: patch[i],
          g: patch[i + 1],
          b: patch[i + 2],
          a: patch[i + 3],
        };
      }
    }

    return {
      frameIndex: index,
      bitmap,
      delay: frame.delay,
    };
  });

  return bitmaps;
};

const COLOR_MAP = [
  { name: 'Black', values: { r: false, g: false, b: false } }, // 000
  { name: 'Blue', values: { r: false, g: false, b: true } }, // 001
  { name: 'Green', values: { r: false, g: true, b: false } }, // 010
  { name: 'Cyan', values: { r: false, g: true, b: true } }, // 011
  { name: 'Red', values: { r: true, g: false, b: false } }, // 100
  { name: 'Magenta', values: { r: true, g: false, b: true } }, // 101
  { name: 'Yellow', values: { r: true, g: true, b: false } }, // 110
  { name: 'White', values: { r: true, g: true, b: true } }, // 111
];

const guessPixelValue = (r, g, b, a) => {
  // If alpha is too low (nearly transparent), return black
  if (a < 127) {
    return { r: false, g: false, b: false };
  }

  // Calculate distances to each possible color
  const distances = COLOR_MAP.map((color) => {
    const rDist = Math.abs(r - (color.values.r ? 255 : 0));
    const gDist = Math.abs(g - (color.values.g ? 255 : 0));
    const bDist = Math.abs(b - (color.values.b ? 255 : 0));

    return {
      color: color.values,
      distance: Math.sqrt(rDist * rDist + gDist * gDist + bDist * bDist),
    };
  });

  // Find the closest color
  const closestColor = distances.reduce((prev, curr) =>
    curr.distance < prev.distance ? curr : prev,
  );

  return closestColor.color;
};

const handlePixelNotFound = (pixel, notFoundPixels) => {
  const { r, g, b } = pixel;

  const pixelValue = `rgb(${r}, ${g}, ${b})`;

  const notFoundObject = {
    count: 1,
    value: pixelValue,
  };

  const existingPixelIndex = notFoundPixels.findIndex((pixel) => {
    return pixel.value === pixelValue;
  });

  if (existingPixelIndex !== -1) {
    notFoundPixels[existingPixelIndex].count++;
  } else {
    notFoundPixels.push(notFoundObject);
  }
};

const notFoundPixels = [];
export const getGridPixelsFromBitmap = (bitmap) => {
  const { bitmap: frame } = bitmap;

  const pixelArray = Array(totalPixels).fill(initialValue);

  // Iterate over columns first, then rows
  for (let columnIndex = 0; columnIndex < frame[0].length; columnIndex++) {
    for (let rowIndex = 0; rowIndex < frame.length; rowIndex++) {
      const pixel = frame[rowIndex][columnIndex];
      const { r, g, b, a } = pixel;

      const targetPixel = colorMap.find((color) => {
        return (
          color.source.r === r && color.source.g === g && color.source.b === b
        );
      });

      // Calculate index in the output array based on column-first ordering
      const pixelOffset = columnIndex * frame.length + rowIndex;
      const pixelIndex = pixelOffset + centerOffset;

      if (targetPixel) {
        pixelArray[pixelIndex] = targetPixel.target;
      } else {
        handlePixelNotFound(pixel, notFoundPixels);
        // notFoundPixels.push({pixel: { r, g, b }
        // count :1});
        pixelArray[pixelIndex] = guessPixelValue(r, g, b, a);
      }
    }
  }

  return pixelArray;
};

export const getGridPixelArray = (bitmaps) => {
  const pixelArray = [];
  bitmaps.forEach((bitmap) => {
    const frame = getGridPixelsFromBitmap(bitmap);
    pixelArray.push(...frame);
  });

  notFoundPixels.sort((a, b) => b.count - a.count);
  console.table(notFoundPixels);

  return pixelArray;
};

export const processGif = async (file) => {
  try {
    // Read the file as ArrayBuffer
    const buffer = await file.arrayBuffer();

    // Parse the GIF
    const gif = parseGIF(buffer);
    const frames = decompressFrames(gif, true);
    const bitmaps = await getGifBitmaps(frames);
    const pixelArray = getGridPixelArray(bitmaps);

    const delay = frames[0].delay;

    const imageObject = {
      pixelArray,
      isAnimation: true,
      delays: delay,
      frameNum: frames.length,
      pixelWidth: GRID_WIDTH,
      pixelHeight: GRID_HEIGHT,
    };

    return imageObject;

    // Process each frame into a bitmap

    //   setFrames(bitmaps);
    //   setError(null);
  } catch (err) {
    // setError('Error processing GIF: ' + err.message);
    console.error(err);
  }
};
