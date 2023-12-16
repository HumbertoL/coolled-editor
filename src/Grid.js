import React from 'react';
import styled from 'styled-components';

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
const Grid = ({ pixelArray }) => {
    if (!pixelArray) return <div>Please upload a file</div>;

    return (
        <GridContainer>
            {pixelArray.map((pixel, index) => (
                <GridSquare key={index} style={{ backgroundColor: getColorFromChunk(pixel) }}>
                    {/* {index} */}
                </GridSquare>
            ))}
        </GridContainer>
    );
};


function getColorFromChunk(pixel) {
    const { r, g, b } = pixel;
    const redValue = r ? 'FF' : '00';
    const greenValue = g ? 'FF' : '00';
    const blueValue = b ? 'FF' : '00';

    return `#${redValue}${greenValue}${blueValue}`
}

export default Grid;
