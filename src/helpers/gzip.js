/**
 * Inflate a gzipped asset fetched from public/.
 *
 * Several of the vendored assets are gzipped on disk -- packed pixel planes
 * and glyph tables are repetitive enough to shrink 10-20x -- so they are
 * stored compressed and inflated here. A host that decodes .gz transparently
 * is handled too, since then the bytes have already stopped looking like gzip.
 */
const isGzip = (bytes) => bytes[0] === 0x1f && bytes[1] === 0x8b;

export const inflateResponse = async (response) => {
  const bytes = new Uint8Array(await response.arrayBuffer());

  if (!isGzip(bytes)) {
    return bytes;
  }

  if (typeof DecompressionStream === 'undefined') {
    throw new Error('This browser cannot inflate gzipped assets');
  }

  const stream = new Blob([bytes])
    .stream()
    .pipeThrough(new DecompressionStream('gzip'));

  return new Uint8Array(await new Response(stream).arrayBuffer());
};

export const inflateJson = async (response) => {
  const bytes = await inflateResponse(response);
  return JSON.parse(new TextDecoder().decode(bytes));
};
