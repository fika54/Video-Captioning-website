import React, { useState } from "react";
import axios from "axios";

function UploadForm({ setCaptions, setVideoURL }) {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("batch");

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", mode);

    const res = await axios.post("http://localhost:8000/upload", formData);
    console.log("returned data: ", res) //debug
    setCaptions(res.data.segments);
    setVideoURL(URL.createObjectURL(file));
  };

  return (
    <div>
      <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} />
      <select value={mode} onChange={e => setMode(e.target.value)}>
        <option value="batch">Batch</option>
        <option value="word">Word-by-word</option>
      </select>
      <button onClick={handleUpload}>Upload & Transcribe</button>
    </div>
  );
}

export default UploadForm;