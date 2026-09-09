import { useEffect, useMemo, useRef, useState } from 'react';
import styled from 'styled-components';
import { GRID_HEIGHT, GRID_WIDTH } from './helpers/constants';
import {
  DEFAULT_TRACKING,
  alignX,
  drawColumns,
  ensureGlyphs,
  layoutText,
} from './helpers/font';
import { getColorObjectFromName } from './helpers/colors';

const Panel = styled.div`
  width: 100%;
  max-width: 720px;
  margin: 0 auto 16px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  text-align: left;
`;

const Row = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;

  & + & {
    margin-top: 12px;
  }
`;

const TextInput = styled.input`
  flex: 1;
  min-width: 220px;
  padding: 9px 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: #e0e0ea;
  font-size: 14px;

  &::placeholder {
    color: #6a6a80;
  }

  &:focus {
    outline: none;
    border-color: rgba(122, 92, 255, 0.6);
  }
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #7a7a90;
`;

const Pill = styled.button`
  padding: 5px 11px;
  background: ${({ $active }) =>
    $active ? 'rgba(122, 92, 255, 0.28)' : 'rgba(255, 255, 255, 0.05)'};
  color: ${({ $active }) => ($active ? '#d8d0ff' : '#8a8aa0')};
  border: 1px solid
    ${({ $active }) =>
      $active ? 'rgba(122,92,255,0.5)' : 'rgba(255,255,255,0.1)'};
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;

  &:hover {
    color: #fff;
  }
`;

const Number = styled.input`
  width: 54px;
  padding: 5px 8px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: #e0e0ea;
  font-size: 12px;
  text-align: center;
`;

const Preview = styled.canvas`
  display: block;
  width: 100%;
  height: auto;
  margin: 12px 0 0;
  background: #05050a;
  border-radius: 6px;
  image-rendering: pixelated;
`;

const Note = styled.p`
  margin: 10px 0 0;
  font-size: 11.5px;
  line-height: 1.6;
  color: ${({ $warn }) => ($warn ? '#ffb4a2' : '#7a7a90')};
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 14px;
`;

const Button = styled.button`
  padding: 8px 14px;
  background: ${({ $primary }) =>
    $primary
      ? 'linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%)'
      : 'rgba(255,255,255,0.08)'};
  color: ${({ $primary }) => ($primary ? '#fff' : '#c0c0d0')};
  border: ${({ $primary }) =>
    $primary ? 'none' : '1px solid rgba(255,255,255,0.12)'};
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;

  &:disabled {
    opacity: 0.45;
    cursor: default;
  }

  &:hover:not(:disabled) {
    color: #fff;
  }
`;

const ALIGNMENTS = ['left', 'center', 'right'];

/**
 * Set text with the vendor's bitmap font and stamp it into the current frame.
 *
 * Stamping rather than keeping a text layer is deliberate: once the pixels are
 * down they're editable like any others, which is what you want on a panel
 * this small, where a glyph usually needs a nudge somewhere.
 */
const TextTool = ({
  imageData,
  setImageData,
  frame,
  selectedColor,
  onClose,
}) => {
  const [text, setText] = useState('');
  const [align, setAlign] = useState('center');
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);
  const [tracking, setTracking] = useState(DEFAULT_TRACKING);
  const [monospace, setMonospace] = useState(false);
  const [clearFirst, setClearFirst] = useState(true);
  const [manifest, setManifest] = useState(null);
  // Bumped whenever glyph pages land. The manifest is a cached singleton, so
  // its identity never changes and can't be what tells the layout below that
  // more glyphs are available now than on the last render.
  const [glyphsLoaded, setGlyphsLoaded] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef(null);

  // Fetch only the font pages this string needs, then re-lay it out. Every
  // keystroke can trigger this; pages are cached, so it settles immediately
  // for text in a script already loaded.
  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    ensureGlyphs(text)
      .then((loaded) => {
        if (cancelled) return;
        setManifest(loaded);
        setGlyphsLoaded((count) => count + 1);
        setError(null);
      })
      .catch((loadError) => {
        if (cancelled) return;
        setError(loadError.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [text]);

  const layout = useMemo(() => {
    if (!manifest || !text) {
      return null;
    }
    return layoutText(manifest, text, { tracking, monospace });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manifest, glyphsLoaded, text, tracking, monospace]);

  const startX = layout ? alignX(layout, align) + offsetX : 0;
  const overflow = layout ? layout.width + Math.abs(offsetX) - GRID_WIDTH : 0;

  // Preview is the real thing: the same layout run through the same painter,
  // over a copy of the frame it would land on.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const image = ctx.createImageData(GRID_WIDTH, GRID_HEIGHT);
    const pixelsPerFrame = GRID_WIDTH * GRID_HEIGHT;
    const frameOffset = (frame - 1) * pixelsPerFrame;

    const black = { r: false, g: false, b: false };
    const pixels = clearFirst
      ? new Array(pixelsPerFrame).fill(black)
      : imageData.pixelArray.slice(frameOffset, frameOffset + pixelsPerFrame);

    if (layout) {
      drawColumns(pixels, layout, {
        color: getColorObjectFromName(selectedColor),
        x: startX,
        y: offsetY,
      });
    }

    for (let column = 0; column < GRID_WIDTH; column++) {
      for (let row = 0; row < GRID_HEIGHT; row++) {
        const pixel = pixels[column * GRID_HEIGHT + row] ?? black;
        const target = (row * GRID_WIDTH + column) * 4;
        image.data[target] = pixel.r ? 255 : 0;
        image.data[target + 1] = pixel.g ? 255 : 0;
        image.data[target + 2] = pixel.b ? 255 : 0;
        image.data[target + 3] = 255;
      }
    }

    ctx.putImageData(image, 0, 0);
  }, [layout, startX, offsetY, clearFirst, imageData, frame, selectedColor]);

  const handleInsert = () => {
    if (!layout) return;

    const pixelsPerFrame = GRID_WIDTH * GRID_HEIGHT;
    const frameOffset = (frame - 1) * pixelsPerFrame;
    const pixelArray = imageData.pixelArray.slice();

    if (clearFirst) {
      pixelArray.fill(
        { r: false, g: false, b: false },
        frameOffset,
        frameOffset + pixelsPerFrame,
      );
    }

    drawColumns(pixelArray, layout, {
      color: getColorObjectFromName(selectedColor),
      x: startX,
      y: offsetY,
      frameOffset,
    });

    setImageData({ ...imageData, pixelArray });
  };

  const missing = layout?.missing ?? [];

  return (
    <Panel>
      <Row>
        <TextInput
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Type text to set in the panel font…"
          autoFocus
        />
      </Row>

      <Row>
        <Label>Align</Label>
        {ALIGNMENTS.map((option) => (
          <Pill
            key={option}
            $active={align === option}
            onClick={() => setAlign(option)}
          >
            {option}
          </Pill>
        ))}
        <Label>
          Nudge x
          <Number
            type="number"
            value={offsetX}
            onChange={(event) => setOffsetX(Number(event.target.value) || 0)}
          />
        </Label>
        <Label>
          y
          <Number
            type="number"
            value={offsetY}
            onChange={(event) => setOffsetY(Number(event.target.value) || 0)}
          />
        </Label>
      </Row>

      <Row>
        <Label>
          Tracking
          <Number
            type="number"
            min="0"
            max="8"
            value={tracking}
            onChange={(event) =>
              setTracking(Math.max(0, Number(event.target.value) || 0))
            }
          />
        </Label>
        <Pill $active={monospace} onClick={() => setMonospace((on) => !on)}>
          {monospace ? 'Monospace' : 'Proportional'}
        </Pill>
        <Pill $active={clearFirst} onClick={() => setClearFirst((on) => !on)}>
          {clearFirst ? 'Replace frame' : 'Draw over frame'}
        </Pill>
      </Row>

      <Preview ref={canvasRef} width={GRID_WIDTH} height={GRID_HEIGHT} />

      {error && <Note $warn>{error}</Note>}

      {!error && layout && (
        <Note $warn={overflow > 0}>
          {layout.width} of {GRID_WIDTH} columns
          {overflow > 0 && ` · ${overflow} clipped off the panel`}
          {missing.length > 0 &&
            ` · no glyph for ${missing.slice(0, 6).join(' ')}`}
        </Note>
      )}

      {!error && !layout && !loading && (
        <Note>
          Text is drawn with the CoolLED1248 app&apos;s own 16px bitmap font, so
          accented Latin, Greek, Cyrillic, Kana and CJK all work. Pixels are
          stamped into the current frame and stay editable.
        </Note>
      )}

      <Actions>
        <Button $primary onClick={handleInsert} disabled={!layout}>
          Insert into frame {frame}
        </Button>
        <Button onClick={onClose}>Done</Button>
      </Actions>
    </Panel>
  );
};

export default TextTool;
