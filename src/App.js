import "./App.css";
import { downloadJtFile, parseData } from "./helpers/parse_data";
import Grid from "./Grid";
import { useState } from "react";
import styled from "styled-components";

import welcome from "./sample/welcome_to_chaos_corner.json";
import ColorPicker from "./ColorPicker";
import { getColorObjectFromName } from "./helpers/colors";

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

const getInitialPixelArray = () => {
  const GRID_HEIGHT = 16;
  const GRID_WIDTH = 96;
  const totalPixels = GRID_HEIGHT * GRID_WIDTH;
  const initialValue = { r: false, g: false, b: false };
  const initialArray = Array(totalPixels).fill(initialValue);
  return initialArray;
}

function App() {
  // const [pixelArray, setPixelArray] = useState(() =>
  //   parseData(JSON.stringify(welcome))
  // );
  const [pixelArray, setPixelArray] = useState(() => getInitialPixelArray());
  const [selectedColor, setSelectedColor] = useState("White");

  const readFile = (file) => {
    const reader = new FileReader();

    reader.onload = (event) => {
      const content = event.target.result; // Get the file content
      const pixelArray = parseData(content);
      setPixelArray(pixelArray);
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
    console.log(index);
    const rgb = getColorObjectFromName(selectedColor);
    const newPixelArray = [...pixelArray];
    newPixelArray[index] = rgb;
    setPixelArray(newPixelArray);
  };

  const handleDownload = () => {
    downloadJtFile(pixelArray);
  };

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

        <Grid pixelArray={pixelArray} onClick={handleClick} />
        <ColorPicker
          setSelectedColor={setSelectedColor}
          selectedColor={selectedColor}
        />
      </header>
    </div>
  );
}

export default App;
