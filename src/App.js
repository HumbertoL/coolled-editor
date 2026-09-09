import './App.css';
import { parseData } from './helpers/parse_data';
import Grid from './Grid';
import { useCallback, useEffect, useState } from 'react';
import styled from 'styled-components';

import ColorPicker from './ColorPicker';
import { getColorObjectFromName } from './helpers/colors';
import FramePicker from './FramePicker';
import { downloadJtFile } from './helpers/export_data';
import FrameControls from './FrameControls';
import DeployInstructions from './DeployInstructions';
import SamplesPage from './SamplesPage';
import FileDrop from './FileDrop';
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

const SecondaryButton = styled.button`
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.08);
  color: #c0c0d0;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.5px;

  &:hover {
    background: rgba(255, 255, 255, 0.14);
    color: #fff;
  }
`;

const Nav = styled.nav`
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
`;

const NavLink = styled.a`
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-decoration: none;
  color: ${({ $active }) => ($active ? '#fff' : '#8a8aa0')};
  background: ${({ $active }) =>
    $active ? 'rgba(122, 92, 255, 0.18)' : 'transparent'};
  border: 1px solid
    ${({ $active }) => ($active ? 'rgba(122,92,255,0.5)' : 'transparent')};
  transition: all 0.15s ease;

  &:hover {
    color: #fff;
  }
`;

// Hash routing keeps each view bookmarkable without pulling in a router or
// needing rewrite rules on static hosting.
const useHashRoute = () => {
  const [route, setRoute] = useState(() => window.location.hash);

  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash);
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  return route.replace(/^#\/?/, '');
};

const ErrorBanner = styled.div`
  max-width: 640px;
  margin: 0 auto 20px;
  padding: 10px 16px;
  background: rgba(255, 90, 90, 0.1);
  border: 1px solid rgba(255, 90, 90, 0.35);
  border-radius: 10px;
  font-size: 13px;
  color: #ff9c9c;
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
  const [showDeploy, setShowDeploy] = useState(false);
  const [lastExportedFile, setLastExportedFile] = useState(null);
  const [fileError, setFileError] = useState(null);

  const route = useHashRoute();

  const startingPixel = getStartingPixel(frame);

  // parseData assumes a .jt shape; check it first so an unrelated JSON file
  // reports what is actually wrong rather than a property access failure.
  const loadJtText = (text) => {
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (error) {
      throw new Error(`not valid JSON (${error.message})`);
    }

    const data = Array.isArray(parsed) ? parsed[0]?.data : parsed?.data;
    if (!data || !(data.aniData || data.graffitiData)) {
      throw new Error('no aniData or graffitiData - is this a .jt file?');
    }

    return parseData(text);
  };

  const readFile = async (file) => {
    const fileName = file.name.toLowerCase();
    setFileError(null);

    try {
      if (fileName.endsWith('.jt') || fileName.endsWith('.json')) {
        // .json samples carry the same structure as .jt.
        setImageData(loadJtText(await file.text()));
      } else if (fileName.endsWith('.gif')) {
        setImageData(await processGif(file));
      } else {
        setFileError(`${file.name} is not a .jt, .json or .gif file.`);
        return;
      }
      // A shorter file than the one before would leave us on a frame that
      // no longer exists.
      setFrame(1);
    } catch (error) {
      setFileError(`Could not read ${file.name} - ${error.message}`);
    }
  };

  // Function to handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      readFile(file);
    }
  };

  const handleDroppedFile = useCallback((file) => {
    readFile(file);
    // A file dropped while browsing samples belongs in the editor.
    if (window.location.hash.replace(/^#\/?/, '') !== '') {
      window.location.hash = '#/';
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  // Load a sample from the Samples page straight into the editor.
  const handleEditSample = (sample) => {
    setImageData(parseData(JSON.stringify(sample.jt)));
    setFrame(1);
    setLastExportedFile(null);
    setShowDeploy(false);
    window.location.hash = '#/';
  };

  const handleDownload = () => {
    const filename = downloadJtFile(imageData);
    setLastExportedFile(filename);
    // Surface the send command as soon as there is a file to send.
    setShowDeploy(true);
  };

  const displayPixelArray = imageData.pixelArray.slice(
    startingPixel,
    startingPixel + GRID_HEIGHT * GRID_WIDTH,
  );

  const isSamples = route === 'samples';

  return (
    <div className="App">
      <header className="App-header">
        <FileDrop onFile={handleDroppedFile} />
        <AppTitle>CoolLED Editor</AppTitle>

        <Nav>
          <NavLink href="#/" $active={!isSamples}>
            Editor
          </NavLink>
          <NavLink href="#/samples" $active={isSamples}>
            Samples
          </NavLink>
        </Nav>

        {isSamples && <SamplesPage onEdit={handleEditSample} />}

        {!isSamples && (
          <>
            <Toolbar>
              <FileLabel>
                Upload or drop .jt / .gif
                <FileInput
                  type="file"
                  accept=".jt,.json,.gif"
                  onChange={handleFileChange}
                />
              </FileLabel>
              <Divider />
              <StyledButton onClick={handleDownload}>Export .jt</StyledButton>
              <Divider />
              <SecondaryButton onClick={() => setShowDeploy((shown) => !shown)}>
                {showDeploy ? 'Hide' : 'Send to sign'}
              </SecondaryButton>
            </Toolbar>

            {fileError && <ErrorBanner>{fileError}</ErrorBanner>}

            {showDeploy && (
              <DeployInstructions lastExportedFile={lastExportedFile} />
            )}

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
          </>
        )}
      </header>
    </div>
  );
}

export default App;
