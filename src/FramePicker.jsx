import React from 'react';
import styled from 'styled-components';

const StyledRoot = styled.div`
  display: flex;
  margin-top: 8px;
  margin-bottom: 4px;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
`;

const FrameButton = styled.button`
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${(props) =>
    props.selected
      ? 'linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%)'
      : 'rgba(255, 255, 255, 0.06)'};
  color: ${(props) => (props.selected ? '#fff' : 'rgba(255, 255, 255, 0.6)')};
  border: 1px solid ${(props) =>
    props.selected ? 'rgba(122, 92, 255, 0.5)' : 'rgba(255, 255, 255, 0.08)'};
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    background: ${(props) =>
      props.selected
        ? 'linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%)'
        : 'rgba(255, 255, 255, 0.1)'};
    color: #fff;
  }
`;

const Label = styled.span`
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  margin-right: 8px;
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
      <Label>Frames</Label>
      {frameButtons}
    </StyledRoot>
  );
};

export default FramePicker;
