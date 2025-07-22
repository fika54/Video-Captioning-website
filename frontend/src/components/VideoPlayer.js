import React, {useState, useRef, useEffect} from "react";
import "./VideoPlayer.css";

function VideoPlayer({ videoURL, captions }) {
  const [currentTime, setCurrentTime] = useState(0);
  const [currentCaption, setCurrentCaption] = useState('')
  //const [wordID, setWordID] = useState(-1)
  const videoRef = useRef(null);

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
      //console.log("Current time:", videoRef.current.currentTime);
    }
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    //console.log(captions[0]['words'][0])

    const interval = setInterval(() => {

      const vidTime = video.currentTime;
      const segmentID = captions.find(
        (cap) => vidTime >= cap.start && vidTime <= cap.end
      );

      
      if (segmentID) {
        const activeCaption = segmentID.words.find(
        (cap) => vidTime >= cap.start && vidTime <= cap.end
        );
        setCurrentCaption(activeCaption ? activeCaption.word : "");
      } else {
        setCurrentCaption("");
      }
    }, 50)     

    return () => clearInterval(interval);
    


    
  }, [captions]);

  return (
    <div className="video-container">
      <video ref = {videoRef} src={videoURL} onTimeUpdate={handleTimeUpdate} controls />
      <div className="captions">
          <div className="caption" style={{ top: "80%" }}>
            {currentCaption}
          </div>
      </div>
      <div className="debug-time">Current time: {currentTime.toFixed(2)}s</div>
    </div>
  );
}

export default VideoPlayer;