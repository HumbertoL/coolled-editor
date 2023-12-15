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

// Each column is represented by 16 bits.
// The first bit is in the top left corner of the grid.
// The next bit is in the row below that, and so on.
// e.x. 1000000000000001 represents the top left and bottom left pixels being on.
// However, there's 3 groups of data in the array. 
// The groups are for Red, Green, and Blue.
const buildColumn = (colorChunks, index) => {
    const columnRed = colorChunks.redChunks[index];
    const columnGreen = colorChunks.greenChunks[index];
    const columnBlue = colorChunks.blueChunks[index];

    const columnArray = [];
    for (let j = 0; j < GRID_HEIGHT; j++) {
        const isRedOn = columnRed[j] === '1';
        const isGreenOn = columnGreen[j] === '1';
        const isBlueOn = columnBlue[j] === '1';
        const pixel = { r: isRedOn, g: isGreenOn, b: isBlueOn };
        columnArray.push(pixel);
    }

    return columnArray;

}

const buildLedArray = (colorChunks) => {
    const ledArray = [];

    for (let i = 0; i < GRID_WIDTH; i++) {
        // Build up the rows
        const column = buildColumn(colorChunks, i);
        ledArray.push(...column);
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
