import React from 'react';
import styled from 'styled-components';
import { getColorFromChunk } from './helpers/colors';

const squareSize = 12;

const GridSquare = styled.div`
  width: ${squareSize}px;
  height: ${squareSize}px;
  border-radius: 2px;
  font-size: 10px;
  display: grid;
  transition: box-shadow 0.05s ease;
`;

const GridContainer = styled.div`
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(96, ${squareSize}px);
  grid-template-rows: repeat(16, ${squareSize}px);
  grid-gap: 1px;
  grid-auto-flow: column;
  background: #0a0a0f;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 0 40px rgba(0, 0, 0, 0.5),
    inset 0 0 30px rgba(0, 0, 0, 0.3);
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

  const getSquareStyle = (pixel) => {
    const color = getColorFromChunk(pixel);
    const isLit = color !== '#000000';
    return {
      backgroundColor: color,
      boxShadow: isLit ? `0 0 4px ${color}80, 0 0 1px ${color}40` : 'none',
    };
  };

  return (
    <GridContainer onMouseEnter={handleEnterGrid}>
      {pixelArray.map((pixel, index) => (
        <GridSquare
          key={index}
          style={getSquareStyle(pixel)}
          onClick={() => handleClick(index)}
          onMouseDown={onMouseDown}
          onMouseUp={onMouseUp}
          onMouseEnter={() => onMouseEnter(index)}
        />
      ))}
    </GridContainer>
  );
};

export default Grid;
