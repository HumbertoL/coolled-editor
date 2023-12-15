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

    // Each column is represent by 16bits
const CHUNK_SIZE = 16;
const separateIntoColumns = (binaryString) => {
    const chunks = [];
    for (let i = 0; i < binaryString.length; i += CHUNK_SIZE) {
        chunks.push(binaryString.substring(i, i + CHUNK_SIZE));
    }
    return chunks;
}

// The first 3rd of the data represents whether Red is on or off
// The second 3rd of the data represents whether Green is on or off
// The last 3rd of the data represents whether Blue is on or off
const divideColumnsIntoRGBGroups = (chunks) => {
    const totalChunks = chunks.length;
    const oneThird = totalChunks / 3;

    const redChunks = chunks.slice(0, oneThird);
    const greenChunks = chunks.slice(oneThird, 2 * oneThird);
    const blueChunks = chunks.slice(2 * oneThird);

    return { redChunks, greenChunks, blueChunks };
}


const GRID_HEIGHT = 16
const GRID_WIDTH = 96

const buildLedArray = (colorChunks) => {
    // const totalChunks = colorChunks.redChunks.length;
    const ledArray = [];

    for (let i = 0; i < GRID_WIDTH; i++) {
        // TODO: move to a new function
        const columnRed = colorChunks.redChunks[i];
        const columnGreen = colorChunks.greenChunks[i];
        const columnBlue = colorChunks.blueChunks[i];
        for (let j = 0; j < GRID_HEIGHT; j++) {
            const isRedOn = columnRed[j] === '1';
            const isGreenOn = columnGreen[j] === '1';
            const isBlueOn = columnBlue[j] === '1';
            const pixel = { r: isRedOn, g: isGreenOn, b: isBlueOn };
            ledArray.push(pixel);
        }

    }

    return ledArray;
}


// Component for rendering the grid
const Grid = ({ binaryString }) => {
    const columns = separateIntoColumns(binaryString);
    const colorArrays = divideColumnsIntoRGBGroups(columns);
    const ledArray = buildLedArray(colorArrays)

    return (
        <GridContainer>
            {ledArray.map((pixel, index) => (
                <GridSquare key={index} style={{ backgroundColor: getColorFromChunk(pixel) }}>{index}</GridSquare>
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
