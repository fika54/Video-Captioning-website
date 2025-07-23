import React, { useState } from "react";
import axios from "axios";

function UploadForm({ setCaptions, setVideoURL }) {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("batch");
  const [outputBlob, setOutputBlob] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", mode);

    const res = await axios.post("http://localhost:8000/upload", formData, {
      responseType: "blob"
    });
    console.log("returned data: ", res) //debug

    const videoBlob = new Blob([res.data], { type: "video/mp4" });
    const videoURL = URL.createObjectURL(videoBlob);

    setOutputBlob(videoBlob); // Save blob for download
    setVideoURL(videoURL);    // Set URL to show in <video>

    //setCaptions(res.data.segments);
    //setVideoURL(URL.createObjectURL(file));


  };

  const handleDownload = () => {
    if (!outputBlob) return;

    const a = document.createElement("a");
    a.href = URL.createObjectURL(outputBlob);
    a.download = "captioned_video.mp4";
    a.click();
  };

  return (
    <div>
      <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} />
      <select value={mode} onChange={e => setMode(e.target.value)}>
        <option value="batch">Batch</option>
        <option value="word">Word-by-word</option>
      </select>
      <button onClick={handleUpload}>Upload & Transcribe</button>
      {outputBlob && (
        <div style={{ marginTop: "1rem" }}>
          <button onClick={handleDownload}>Download Burned-In Video</button>
        </div>
      )}
    </div>
  );
}

export default UploadForm;