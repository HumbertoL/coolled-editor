import './App.css';
import { parseData } from './helpers/parse_data';
import Grid from './Grid';
import { useState } from 'react';
import styled from 'styled-components';

import welcome from './sample/welcome_to_chaos_corner.json';
import ColorPicker from './ColorPicker';


const FileUpload = styled.input`
  margin: 60px;
`;

function App() {
  const [pixelArray, setPixelArray] = useState(() => parseData(JSON.stringify(welcome)));
  const [selectedColor, setSelectedColor] = useState( "#FFFFFF");

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

  return (
    <div className="App">
      <header className="App-header">
        <FileUpload type="file" onChange={handleFileChange} />
        <Grid pixelArray={pixelArray} />
        <ColorPicker setSelectedColor={setSelectedColor} selectedColor={selectedColor} />
      </header>
    </div>
  );
}

export default App;
