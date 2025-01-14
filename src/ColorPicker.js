import React, { useState } from 'react';
import styled from 'styled-components';
import { colors } from './helpers/colors';

const ColorSquare = styled.div`
  width: 50px;
  height: 50px;
  margin: 5px;
  cursor: pointer;
  background-color: ${(props) => props.color};
  border: ${(props) =>
    props.selected ? '4px solid orange' : '2px solid transparent'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${(props) => (props.selected ? 'black' : 'inherit')};
`;

const ColorPicker = ({ setSelectedColor, selectedColor }) => {
  const handleColorSelection = (color) => {
    setSelectedColor(color === selectedColor ? null : color); // Toggle selection
  };

  return (
    <div>
      <h3>Select a Color:</h3>
      <div style={{ display: 'flex' }}>
        {colors.map((color, index) => (
          <ColorSquare
            key={index}
            color={color.hex}
            selected={selectedColor === color.name}
            onClick={() => handleColorSelection(color.name)}
          ></ColorSquare>
        ))}
      </div>
      <div>
        <p>Selected Color: {selectedColor}</p>
      </div>
    </div>
  );
};

export default ColorPicker;
