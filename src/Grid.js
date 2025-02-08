import React from 'react';
import styled from 'styled-components';
import { getColorFromChunk } from './helpers/colors';

const squareSize = 12;

// Styled component for the individual grid square
const GridSquare = styled.div`
  width: ${squareSize}px;
  height: ${squareSize}px;
  border: 1px solid #ccc;
  font-size: 10px;
  display: grid;
`;

const GridContainer = styled.div`
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(
    96,
    ${squareSize}px
  ); /* 96 columns, each with a width of 20px */
  grid-template-rows: repeat(
    16,
    ${squareSize}px
  ); /* 16 rows, each with a height of 20px */
  grid-gap: 1px; /* Gap between each grid square */
  grid-auto-flow: column; /* Automatically flow the grid items into columns */
`;

// Component for rendering the grid
const Grid = ({
  pixelArray,
  onClick,
  onMouseDown,
  onMouseUp,
  onMouseEnter,
}) => {
  if (!pixelArray) {
    return <div>Please upload a file</div>;
  }

  const handleClick = (index) => {
    onClick(index);
  };

  const handleEnterGrid = (e) => {
    // Stop dragging when leaving and re-entering the grid
    e.stopPropagation();
    e.preventDefault();
    onMouseUp();
  };

  return (
    <GridContainer onMouseEnter={handleEnterGrid}>
      {pixelArray.map((pixel, index) => (
        <GridSquare
          key={index}
          style={{ backgroundColor: getColorFromChunk(pixel) }}
          onClick={() => handleClick(index)}
          onMouseDown={onMouseDown}
          onMouseUp={onMouseUp}
          onMouseEnter={() => onMouseEnter(index)}
        >
          {/* {index} */}
        </GridSquare>
      ))}
    </GridContainer>
  );
};

export default Grid;
