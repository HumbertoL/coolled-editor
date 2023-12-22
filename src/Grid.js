import React from 'react';
import styled from 'styled-components';
import { getColorFromChunk } from './helpers/colors';

// Styled component for the individual grid square
const GridSquare = styled.div`
  width: 20px;
  height: 20px;
  border: 1px solid #ccc;
  font-size: 10px;
  display: grid;

`;

const GridContainer = styled.div`
    display: grid;
    grid-template-columns: repeat(96, 20px); /* 96 columns, each with a width of 20px */
    grid-template-rows: repeat(16, 20px); /* 16 rows, each with a height of 20px */
    grid-gap: 1px; /* Gap between each grid square */
    grid-auto-flow: column; /* Automatically flow the grid items into columns */
    `


// Component for rendering the grid
const Grid = ({ pixelArray, onClick }) => {
    if (!pixelArray) {
        return <div>Please upload a file</div>;
    }

    const handleClick = (index) => {
        onClick(index);

    }

    return (
        <GridContainer>
            {pixelArray.map((pixel, index) => (
                <GridSquare key={index} style={{ backgroundColor: getColorFromChunk(pixel) }} onClick={() => handleClick(index)}>
                    {/* {index} */}
                </GridSquare>
            ))}
        </GridContainer>
    );
};



export default Grid;
