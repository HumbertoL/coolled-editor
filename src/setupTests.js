import '@testing-library/jest-dom';

// jsdom has no 2D canvas: getContext returns null, which crashes the
// components that draw the panel. A no-op context is enough for render
// smoke tests -- anything asserting on pixels needs a real canvas.
const stubContext = () => ({
  arcTo: () => {},
  beginPath: () => {},
  closePath: () => {},
  createImageData: (width, height) => ({
    data: new Uint8ClampedArray(width * height * 4),
    width,
    height,
  }),
  drawImage: () => {},
  fill: () => {},
  fillRect: () => {},
  moveTo: () => {},
  putImageData: () => {},
  scale: () => {},
  setTransform: () => {},
  fillStyle: '',
  shadowBlur: 0,
  shadowColor: '',
});

HTMLCanvasElement.prototype.getContext = stubContext;
