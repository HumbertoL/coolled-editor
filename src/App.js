import logo from './logo.svg';
import './App.css';
import { parseData } from './helpers/parse_data';
import Grid from './Grid';
import { useState } from 'react';
import styled from 'styled-components';

import welcome from './sample/welcome_to_chaos_corner.json';


const FileUpload = styled.input`
  margin: 60px;

`;

function App() {
  const [parsedData, setParsedData] = useState(() => parseData(JSON.stringify(welcome)));

  // Function to read the contents of the file
  const readFile = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result; // Get the file content
      const binaryString = parseData(content); // Call your parseData function with the content
      setParsedData(binaryString); // Set the state with the binary string
    };
    reader.readAsText(file); // Read the file as text
  };

  // Function to handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0]; // Get the selected file
    if (file) {
      readFile(file); // Call function to read the file
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <FileUpload type="file" onChange={handleFileChange} />
        <Grid binaryString={parsedData} />
      </header>
    </div>
  );
}

export default App;
