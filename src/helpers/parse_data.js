// import welcome from '../sample/welcome_to_chaos_corner.json';
// import greenTopRight from '../sample/green_top_right.json';

export const parseData = (content) => {
  const imageData = convertDataToBinary(content);

  const columns = separateIntoColumns(imageData.binaryString);
  const colorArrays = divideColumnsIntoRGBGroups(columns);
  const pixelArray = buildLedArray(colorArrays);

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
  const frameNum = parsedData.frameNum;
  const pixelWidth = parsedData.pixelWidth;
  const pixelHeight = parsedData.pixelHeight;

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

const GRID_HEIGHT = 16;
const GRID_WIDTH = 96;

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

const buildLedArray = (colorChunks) => {
  const ledArray = [];

  for (let i = 0; i < GRID_WIDTH; i++) {
    // Build up the rows
    const column = buildColumn(colorChunks, i);
    ledArray.push(...column);
  }

  return ledArray;
};

const templateData = [
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

const reconstructGraffitiDataFromPixelArray = (pixelArray) => {
  const colorChunks = reconstructColorChunks(pixelArray);

  const reconstructedBinaryString =
    colorChunks.redChunks.join('') +
    colorChunks.greenChunks.join('') +
    colorChunks.blueChunks.join('');

  let originalData = [];
  for (let i = 0; i < reconstructedBinaryString.length; i += 8) {
    const num = convertBinaryToNumber(
      reconstructedBinaryString.substring(i, i + 8),
    );
    originalData.push(num);
  }

  return originalData;
};

export const buildTemplate = (graffitiData) => {
  const template = [...templateData];
  template[0].data.graffitiData = graffitiData;
  return template;
};

export const buildFile = (chunks) => {
  const fileTemplate = buildTemplate(chunks);
  const json = JSON.stringify(fileTemplate);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  return url;
};

export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
};

export const downloadJtFile = (pixelArray) => {
  const originalData = reconstructGraffitiDataFromPixelArray(pixelArray);
  const url = buildFile(originalData);
  // get timestamp for filename
  const timestamp = Date.now();
  const filename = `CoolLEDX_16x96_1_${timestamp}.jt`;
  downloadFile(url, filename);
};
