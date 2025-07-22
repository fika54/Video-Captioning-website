// 1. Find the current caption text based on video playback time
export function getCurrentCaption(captions, currentTime) {
  // captions = array of { start, end, text }
  return captions.find(
    (caption) => currentTime >= caption.start && currentTime <= caption.end
  )?.text || '';
}

// 2. Return a style object based on user options for captions
export function getCaptionStyle(options) {
  // options = { fontSize, color, backgroundColor, fontWeight }
  return {
    fontSize: options.fontSize || '16px',
    color: options.color || '#FFF',
    backgroundColor: options.backgroundColor || 'rgba(0,0,0,0.5)',
    fontWeight: options.fontWeight || 'normal',
    padding: '4px 8px',
    borderRadius: '4px',
  };
}

// 3. Parse simple subtitle text into caption objects
export function parseCaptions(rawText) {
  // Very basic parser for captions in format: "start --> end\ntext\n\n"
  // Example:
  // 0:00:00.000 --> 0:00:05.000
  // Hello world
  const captionBlocks = rawText.split('\n\n');
  return captionBlocks.map((block) => {
    const [timeLine, ...textLines] = block.split('\n');
    const [startStr, endStr] = timeLine.split(' --> ');
    return {
      start: toSeconds(startStr.trim()),
      end: toSeconds(endStr.trim()),
      text: textLines.join('\n'),
    };
  });
}

function toSeconds(timeStr) {
  // Converts "HH:MM:SS.mmm" to seconds
  const [hms, ms] = timeStr.split('.');
  const [h, m, s] = hms.split(':').map(Number);
  return h * 3600 + m * 60 + s + (ms ? parseInt(ms) / 1000 : 0);
}
