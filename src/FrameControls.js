import React, { useEffect } from 'react';
import styled from 'styled-components';
import {
  getFrameData,
  insertFrame,
  removeFrame,
} from './helpers/frame';

const StyledRoot = styled.div`
  display: flex;
  margin-top: 12px;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  font-size: 13px;
`;

const ControlButton = styled.button`
  padding: 6px 14px;
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${(props) =>
    props.active
      ? 'linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%)'
      : 'rgba(255, 255, 255, 0.08)'};
  color: #fff;
  border: 1px solid ${(props) =>
    props.active ? 'rgba(255, 107, 107, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    background: ${(props) =>
      props.active
        ? 'linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%)'
        : 'rgba(255, 255, 255, 0.14)'};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const StyledLabel = styled.span`
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  margin: 0 4px;
`;

const DelayInput = styled.input`
  width: 70px;
  height: 32px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
  outline: none;
  transition: border-color 0.15s ease;

  &:focus {
    border-color: rgba(122, 92, 255, 0.5);
  }

  /* Hide number spinners */
  -moz-appearance: textfield;
  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
`;

const Divider = styled.div`
  width: 1px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 4px;
`;

const FrameControls = ({
  setFrame,
  selectedFrame,
  frameNum,
  delays,
  setImageData,
  pixelArray,
}) => {
  const [isPreviewing, setIsPreviewing] = React.useState(false);

  useEffect(() => {
    if (isPreviewing) {
      let currentFrame = selectedFrame;
      const interval = setInterval(() => {
        // currentFrame index starts from 1
        // wrap around to frame 1 when reaching frameNum length
        const nextFrame = currentFrame === frameNum ? 1 : currentFrame + 1;
        setFrame(nextFrame);
        currentFrame = nextFrame;
      }, delays);

      return () => {
        clearInterval(interval);
      };
    }
  }, [isPreviewing, delays, frameNum]);

  const handleClick = () => {
    setIsPreviewing(!isPreviewing);
  };

  const handleChangeDelay = (e) => {
    const value = e.target.value;
    setImageData((prev) => ({
      ...prev,
      delays: value,
    }));
  };

  const handleAddFrame = () => {
    // copy current frame and insert new frame after it
    const tempNewFrame = getFrameData(pixelArray, selectedFrame);
    const newFrameData = insertFrame(pixelArray, selectedFrame, tempNewFrame);

    setImageData((prev) => ({
      ...prev,
      frameNum: frameNum + 1,
      pixelArray: newFrameData,
    }));
  };

  const handleRemoveFrame = () => {
    // remove current frame
    const newFrameData = removeFrame(pixelArray, selectedFrame);
    const newFrameCount = frameNum - 1;

    setImageData((prev) => ({
      ...prev,
      frameNum: newFrameCount,
      pixelArray: newFrameData,
    }));

    if (selectedFrame > newFrameCount) {
      setFrame(newFrameCount);
    }
  };

  return (
    <StyledRoot>
      <ControlButton onClick={handleClick} active={isPreviewing}>
        {isPreviewing ? 'Stop' : 'Preview'}
      </ControlButton>

      <Divider />

      <StyledLabel>Delay (ms)</StyledLabel>
      <DelayInput value={delays} onChange={handleChangeDelay} type="number" />

      <Divider />

      <StyledLabel>Frames</StyledLabel>
      <ControlButton onClick={handleRemoveFrame}>−</ControlButton>
      <ControlButton onClick={handleAddFrame}>+</ControlButton>
    </StyledRoot>
  );
};

export default FrameControls;
