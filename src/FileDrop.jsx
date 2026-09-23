import { useCallback, useEffect, useRef, useState } from 'react';
import styled from 'styled-components';

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(10, 10, 18, 0.82);
  backdrop-filter: blur(6px);
  pointer-events: none;
`;

const Target = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 40px 56px;
  border: 2px dashed
    ${({ $rejecting }) =>
      $rejecting ? 'rgba(255, 110, 110, 0.7)' : 'rgba(122, 92, 255, 0.7)'};
  border-radius: 20px;
  background: rgba(122, 92, 255, 0.06);
`;

const Headline = styled.div`
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: ${({ $rejecting }) => ($rejecting ? '#ff9c9c' : '#fff')};
`;

const Hint = styled.div`
  font-size: 13px;
  color: #9a9ab0;
`;

const ACCEPTED = ['.jt', '.json', '.gif'];

const isAccepted = (name) =>
  ACCEPTED.some((extension) => name.toLowerCase().endsWith(extension));

/**
 * Whole-window drop target for sample files.
 *
 * Listens on window rather than a single element so a file can be dropped
 * anywhere, including over the grid or the samples list.
 */
const FileDrop = ({ onFile }) => {
  const [isOver, setIsOver] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  // dragenter/dragleave fire for every element the cursor crosses, so count
  // depth instead of treating the first dragleave as "the drag ended".
  const depth = useRef(0);

  const reset = useCallback(() => {
    depth.current = 0;
    setIsOver(false);
    setRejecting(false);
  }, []);

  useEffect(() => {
    const carriesFiles = (event) =>
      Array.from(event.dataTransfer?.types ?? []).includes('Files');

    const onDragEnter = (event) => {
      if (!carriesFiles(event)) return;
      event.preventDefault();
      depth.current += 1;
      setIsOver(true);

      // dataTransfer.items exposes types (but not names) during the drag, so
      // an obviously wrong file can be flagged before it is dropped.
      const items = Array.from(event.dataTransfer.items ?? []);
      const known = items.filter((item) => item.kind === 'file');
      setRejecting(
        known.length > 0 &&
          known.every(
            (item) =>
              item.type !== '' &&
              item.type !== 'application/json' &&
              item.type !== 'image/gif',
          ),
      );
    };

    const onDragOver = (event) => {
      if (!carriesFiles(event)) return;
      // Without this the browser navigates to the file instead of dropping.
      event.preventDefault();
    };

    const onDragLeave = (event) => {
      if (!carriesFiles(event)) return;
      event.preventDefault();
      depth.current -= 1;
      if (depth.current <= 0) {
        reset();
      }
    };

    const onDrop = (event) => {
      if (!carriesFiles(event)) return;
      event.preventDefault();
      reset();

      const [file] = Array.from(event.dataTransfer.files ?? []);
      if (!file) return;
      onFile(file, { accepted: isAccepted(file.name) });
    };

    window.addEventListener('dragenter', onDragEnter);
    window.addEventListener('dragover', onDragOver);
    window.addEventListener('dragleave', onDragLeave);
    window.addEventListener('drop', onDrop);
    // A drag that leaves the window entirely never fires dragleave on it.
    window.addEventListener('blur', reset);

    return () => {
      window.removeEventListener('dragenter', onDragEnter);
      window.removeEventListener('dragover', onDragOver);
      window.removeEventListener('dragleave', onDragLeave);
      window.removeEventListener('drop', onDrop);
      window.removeEventListener('blur', reset);
    };
  }, [onFile, reset]);

  if (!isOver) {
    return null;
  }

  return (
    <Overlay>
      <Target $rejecting={rejecting}>
        <Headline $rejecting={rejecting}>
          {rejecting ? 'Not a supported file' : 'Drop to open'}
        </Headline>
        <Hint>
          {rejecting
            ? 'Needs a .jt, .json or .gif'
            : '.jt and .json load as frames, .gif is converted'}
        </Hint>
      </Target>
    </Overlay>
  );
};

export default FileDrop;
