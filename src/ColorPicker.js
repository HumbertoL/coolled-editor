import React from 'react';
import styled from 'styled-components';
import { colors } from './helpers/colors';

const ColorPickerWrapper = styled.div`
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
`;

const Label = styled.span`
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1.5px;
`;

const SwatchRow = styled.div`
  display: flex;
  gap: 8px;
`;

const ColorSquare = styled.div`
  width: 40px;
  height: 40px;
  cursor: pointer;
  background-color: ${(props) => props.color};
  border-radius: 10px;
  border: 2px solid ${(props) =>
    props.selected ? '#fff' : 'rgba(255, 255, 255, 0.1)'};
  box-shadow: ${(props) =>
    props.selected
      ? `0 0 12px ${props.color}80, 0 0 4px ${props.color}40`
      : 'none'};
  transition: all 0.15s ease;
  transform: ${(props) => (props.selected ? 'scale(1.15)' : 'scale(1)')};

  &:hover {
    transform: scale(1.1);
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

const SelectedName = styled.span`
  font-size: 14px;
  font-weight: 600;
  color: #fff;
`;

const ColorPicker = ({ setSelectedColor, selectedColor }) => {
  const handleColorSelection = (color) => {
    setSelectedColor(color === selectedColor ? null : color); // Toggle selection
  };

  return (
    <ColorPickerWrapper>
      <Label>Color Palette</Label>
      <SwatchRow>
        {colors.map((color, index) => (
          <ColorSquare
            key={index}
            color={color.hex}
            selected={selectedColor === color.name}
            onClick={() => handleColorSelection(color.name)}
          />
        ))}
      </SwatchRow>
      {selectedColor && <SelectedName>{selectedColor}</SelectedName>}
    </ColorPickerWrapper>
  );
};

export default ColorPicker;
