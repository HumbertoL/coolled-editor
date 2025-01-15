import React from 'react';
import styled from 'styled-components';
const StyledRoot = styled.div`
  display: flex;
  margin-top: 10px;
  align-items: center;
`;

const FrameButton = styled.button`
  margin-left: 14px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${(props) => (props.selected ? 'grey' : 'inherit')};
  color: #fff;
`;

const FramePicker = ({ setFrame, selectedFrame, frameNum }) => {
  if (!frameNum || frameNum <= 1) {
    return null;
  }

  const frameButtons = [];

  for (let i = 1; i <= frameNum; i++) {
    const frameButton = (
      <FrameButton
        key={`frame-${i}`}
        onClick={() => setFrame(i)}
        selected={selectedFrame === i}
      >
        {i}
      </FrameButton>
    );
    frameButtons.push(frameButton);
  }

  return (
    <StyledRoot>
      <div>Frame</div>
      {frameButtons}
    </StyledRoot>
  );
};

export default FramePicker;
