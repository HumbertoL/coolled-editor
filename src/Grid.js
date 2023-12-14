import React from 'react';
import styled from 'styled-components';

// Styled component for the individual grid square
const GridSquare = styled.div`
  width: 20px;
  height: 20px;
  border: 1px solid #ccc;
`;

// Function to split the binary string into 3-character chunks
function chunkBinaryString(binaryString) {
  const chunks = [];
  for (let i = 0; i < binaryString.length; i += 3) {
    chunks.push(binaryString.slice(i, i + 3));
  }
  return chunks;
}

// Component for rendering the grid
const Grid = ({ binaryString }) => {
  // Split the binary string into 3-character chunks
  const chunks = chunkBinaryString(binaryString);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(96, 20px)`, gridGap: '1px' }}>
      {chunks.map((chunk, index) => (
        <GridSquare key={index} style={{ backgroundColor: getColorFromChunk(chunk) }} />
      ))}
    </div>
  );
};

// Function to map each 3-character chunk to a color
function getColorFromChunk(chunk) {
  const colors = [
    '#000000', // Black
    '#00FF00', // Green
    '#FF0000', // Red   
    '#0000FF', // Color 4
    '#FFFF00', // Color 5
    '#FF00FF', // Color 6
    '#00FFFF', // Color 7
    '#FFFFFF', // Color 8
  ];

  // Convert the chunk to a decimal number (base 2) to get the index for the color
  const colorIndex = parseInt(chunk, 2);

  // Return the color based on the index
  return colors[colorIndex % colors.length];
}

export default Grid;
