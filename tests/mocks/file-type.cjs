module.exports.fileTypeFromBuffer = async buffer => {
  // Very small heuristic mock: if buffer contains 'jpeg' or 'JFIF' return jpeg mime
  const s = buffer && buffer.toString ? buffer.toString('utf8') : '';
  if (/JFIF|jpeg|jpeg/i.test(s)) {
    return { ext: 'jpg', mime: 'image/jpeg' };
  }
  // Default: undefined to simulate unknown file types
  return undefined;
};
