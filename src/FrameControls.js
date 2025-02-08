import React, { useEffect } from 'react';
import styled from 'styled-components';
import {
  getFrameData,
  insertFrame,
  removeFrame,
} from './helpers/frame';

const StyledRoot = styled.div`
  display: flex;
  margin-top: 10px;
  align-items: center;
  font-size: 14px;
`;

const FrameButton = styled.button`
  margin-left: 14px;
  min-width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${(props) => (props.selected ? 'grey' : 'inherit')};
  color: #fff;
`;

const StyledLabel = styled.div`
  margin-right: 4px;
  margin-left: 20px;
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
      <FrameButton onClick={handleClick}>
        {isPreviewing ? 'Stop' : 'Preview'}
      </FrameButton>

      <StyledLabel>Frame Delay</StyledLabel>
      <input value={delays} onChange={handleChangeDelay} type="number" />

      <StyledLabel>Add/Remove Frame</StyledLabel>
      <FrameButton onClick={handleRemoveFrame}>-</FrameButton>
      <FrameButton onClick={handleAddFrame}>+</FrameButton>
    </StyledRoot>
  );
};

export default FrameControls;
