import React, { useEffect } from 'react';
import styled from 'styled-components';

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

const FrameControls = ({ setFrame, selectedFrame, frameNum, delays }) => {
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

  if (!frameNum || frameNum <= 1) {
    return null;
  }

  const handleClick = () => {
    setIsPreviewing(!isPreviewing);
  };

  return (
    <StyledRoot>
      <FrameButton onClick={handleClick}>
        {isPreviewing ? 'Stop' : 'Preview'}
      </FrameButton>

      <StyledLabel>Frame Delay</StyledLabel>
      <input type="text" value={delays} />

      <StyledLabel>Add/Remove Frame</StyledLabel>
      <FrameButton>-</FrameButton>
      <FrameButton>+</FrameButton>
    </StyledRoot>
  );
};

export default FrameControls;
