import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import VideoPlayer from "./components/VideoPlayer";

function App() {
  const [captions, setCaptions] = useState([]);
  const [videoURL, setVideoURL] = useState(null);

  return (
    <div className="App">
      <UploadForm setCaptions={setCaptions} setVideoURL={setVideoURL} />
      {videoURL && <VideoPlayer videoURL={videoURL} captions={captions} />}
    </div>
  );
}

export default App;