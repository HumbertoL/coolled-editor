import './App.css';
import { parseData } from './helpers/parse_data';
import Grid from './Grid';
import { useState } from 'react';
import styled from 'styled-components';

import ColorPicker from './ColorPicker';
import { getColorObjectFromName } from './helpers/colors';
import FramePicker from './FramePicker';
import { downloadJtFile } from './helpers/export_data';
import FrameControls from './FrameControls';

const FileUpload = styled.input`
  margin-left: 50px;
`;

const FileUploadWrapper = styled.div`
  display: flex;
  align-items: center;
  font-size: 20px;
  width: 500px;

  & > button {
    margin-left: 28px;
  }
`;

const GRID_HEIGHT = 16;
const GRID_WIDTH = 96;

const FRAME_OFFSET = GRID_HEIGHT * GRID_WIDTH;

const getInitialPixelArray = () => {
  const totalPixels = GRID_HEIGHT * GRID_WIDTH;
  const initialValue = { r: false, g: false, b: false };
  const initialArray = Array(totalPixels).fill(initialValue);
  return initialArray;
};

const getInitialData = () => {
  const imageObject = {
    pixelArray: getInitialPixelArray(),
    isAnimation: false,
    frameNum: 1,
    pixelWidth: GRID_WIDTH,
    pixelHeight: GRID_HEIGHT,
  };

  return imageObject;
};

const getStartingPixel = (frame) => {
  return frame === 1 ? 0 : FRAME_OFFSET * (frame - 1);
};

function App() {
  // const [pixelArray, setPixelArray] = useState(() =>
  //   parseData(JSON.stringify(welcome))
  // );
  const [imageData, setImageData] = useState(() => getInitialData());
  const [selectedColor, setSelectedColor] = useState('White');
  const [isDragging, setIsDragging] = useState(false);
  const [frame, setFrame] = useState(1);

  const startingPixel = getStartingPixel(frame);

  const readFile = (file) => {
    const reader = new FileReader();

    reader.onload = (event) => {
      const content = event.target.result;
      const imageData = parseData(content);
      setImageData(imageData);
    };

    reader.readAsText(file);
  };

  // Function to handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      readFile(file);
    }
  };

  const handleClick = (index) => {
    // console.log(index);
    const rgb = getColorObjectFromName(selectedColor);

    // performance hack, we're mutating the state directly here.
    // We shouldn't be doing this, but it's fine for this project.
    // We create a new imageData object, which should update the state correctly.
    const pixelArray = imageData.pixelArray;

    const startingPixel = getStartingPixel(frame);
    const offsetPixel = startingPixel + index;
    pixelArray[offsetPixel] = rgb;

    setImageData({
      ...imageData,
      pixelArray: pixelArray,
    });
  };

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseEnter = (id) => {
    if (isDragging) {
      // console.log(`Entered div with id: ${id} while dragging`);
      handleClick(id);
    }
  };

  const handleDownload = () => {
    downloadJtFile(imageData);
  };

  const displayPixelArray = imageData.pixelArray.slice(
    startingPixel,
    startingPixel + GRID_HEIGHT * GRID_WIDTH,
  );

  return (
    <div className="App">
      <header className="App-header">
        <FileUploadWrapper>
          Upload File:
          <FileUpload type="file" onChange={handleFileChange} />
        </FileUploadWrapper>
        <FileUploadWrapper>
          Export Design:
          <button onClick={handleDownload}>Download</button>
        </FileUploadWrapper>

        <FramePicker
          selectedFrame={frame}
          frameNum={imageData.frameNum}
          setFrame={setFrame}
        />
        <FrameControls
          setFrame={setFrame}
          selectedFrame={frame}
          frameNum={imageData.frameNum}
          delays={imageData.delays}
        />
        <Grid
          pixelArray={displayPixelArray}
          onClick={handleClick}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseEnter={handleMouseEnter}
        />
        <ColorPicker
          setSelectedColor={setSelectedColor}
          selectedColor={selectedColor}
        />
      </header>
    </div>
  );
}

export default App;
