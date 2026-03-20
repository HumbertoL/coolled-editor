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
import { GRID_HEIGHT, GRID_WIDTH } from './helpers/constants';
import { getStartingPixel } from './helpers/frame';
import { processGif } from './helpers/gif_utils';

const AppTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 32px;
  background: linear-gradient(135deg, #00d2ff, #7a5cff, #ff6bca);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: uppercase;
`;

const Toolbar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
`;

const StyledButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.5px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(122, 92, 255, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`;

const FileInput = styled.input`
  display: none;
`;

const FileLabel = styled.label`
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.08);
  color: #c0c0d0;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(122, 92, 255, 0.5);
    color: #fff;
  }
`;

const Divider = styled.div`
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 4px;
`;

const getInitialPixelArray = () => {
  const totalPixels = GRID_HEIGHT * GRID_WIDTH;
  const initialValue = { r: false, g: false, b: false };
  const initialArray = Array(totalPixels).fill(initialValue);
  return initialArray;
};

const getInitialData = () => {
  const imageObject = {
    pixelArray: getInitialPixelArray(),
    isAnimation: true,
    delays: 300,
    frameNum: 1,
    pixelWidth: GRID_WIDTH,
    pixelHeight: GRID_HEIGHT,
  };

  return imageObject;
};

function App() {
  const [imageData, setImageData] = useState(() => getInitialData());
  const [selectedColor, setSelectedColor] = useState('White');
  const [isDragging, setIsDragging] = useState(false);
  const [frame, setFrame] = useState(1);

  const startingPixel = getStartingPixel(frame);

  const readFile = async (file) => {
    const fileName = file.name;
    if (fileName.endsWith('.jt')) {
      const reader = new FileReader();

      reader.onload = (event) => {
        const content = event.target.result;

        const imageData = parseData(content);
        setImageData(imageData);
      };

      reader.readAsText(file);
    } else if (fileName.endsWith('.gif')) {
      const imageData = await processGif(file);
      setImageData(imageData);
    }
  };

  // Function to handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      readFile(file);
    }
  };

  const handleClick = (index) => {
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
        <AppTitle>CoolLED Editor</AppTitle>

        <Toolbar>
          <FileLabel>
            Upload .jt / .gif
            <FileInput type="file" onChange={handleFileChange} />
          </FileLabel>
          <Divider />
          <StyledButton onClick={handleDownload}>Export .jt</StyledButton>
        </Toolbar>

        {imageData.isAnimation && (
          <>
            <FrameControls
              setFrame={setFrame}
              selectedFrame={frame}
              frameNum={imageData.frameNum}
              delays={imageData.delays}
              setImageData={setImageData}
              pixelArray={imageData.pixelArray}
            />
            <FramePicker
              selectedFrame={frame}
              frameNum={imageData.frameNum}
              setFrame={setFrame}
            />
          </>
        )}

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
