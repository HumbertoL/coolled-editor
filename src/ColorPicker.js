import React, { useState } from 'react';
import styled from 'styled-components';

const ColorSquare = styled.div`
  width: 50px;
  height: 50px;
  margin: 5px;
  cursor: pointer;
  background-color: ${(props) => props.color};
  border: ${(props) => (props.selected ? '4px solid orange' : '2px solid transparent')};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${(props) => (props.selected ? 'black' : 'inherit')};
`;

const ColorPicker = ({ setSelectedColor, selectedColor }) => {

    const colors = [
        { name: 'Black', hex: '#000000' },
        { name: 'Red', hex: '#FF0000' },
        { name: 'Pink', hex: '#FF69B4' },
        { name: 'Yellow', hex: '#FFFF00' },
        { name: 'Green', hex: '#00FF00' },
        { name: 'Cyan', hex: '#00FFFF' },
        { name: 'Blue', hex: '#0000FF' },
        { name: 'White', hex: '#FFFFFF' },
    ];

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
                        selected={selectedColor === color.hex}
                        onClick={() => handleColorSelection(color.hex)}
                    >
                    </ColorSquare>
                ))}
            </div>
            <div>
                <p>Selected Color: {selectedColor || 'None'}</p>
            </div>
        </div>
    );
};

export default ColorPicker;
