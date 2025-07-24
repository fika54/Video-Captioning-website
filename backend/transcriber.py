import whisper
import os

"""
Multiple Pretrained models that tradeoff Accuracy for speed.

Model Name	Parameters	Relative Size	 Accuracy	 Speed
tiny	    ~39M	    🟢 Smallest	    🔴 Low	    🟢 Fastest
base	    ~74M	    🟢 Small	    🟠 Low-med	🟢 Fast
small	    ~244M	    🟡 Medium	    🟡 Decent	🟡 Medium
medium	    ~769M	    🟠 Large	    🟢 High	    🔴 Slower
large	    ~1550M	    🔴 Largest	    🟢 Best	    🔴 Slowest
large-v2	~1550M	    🔴 Largest	    🟢 Best	    🔴 Slowest
large-v3	~1550M	    🔵 Most recent	🟢 Best++	🔴 Slowest
"""
model = whisper.load_model("medium")

#transcribes the audio and segments it
def transcribe_audio(audio_path, mode="batch"):
    result = model.transcribe(audio_path, word_timestamps=(True)) #always transcribes word by word

    #splits the transcription into individual words and their time stamps
    words = []
    for seg in result.get("segments", []):
        words.extend(seg.get("words", []))

    #segments the words into chunks based either on pauses or the length of a given sentence
    segments = []
    istart = 0
    i = 1
    step = 0
    while i < len(words):
        diff = words[i]['start'] - words[i-1]['end']
        segdiff = i - istart

        if diff > 0.2 or segdiff > 5:
            chunk = words[istart:i]
            istart = i
            if not chunk:
                continue

            segment = {
                "start": chunk[0]["start"],
                "end": chunk[-1]["end"],
                "text": " ".join([w["word"] for w in chunk]),
                "words": chunk
            }
            segments.append(segment)

        i = i+1

    #checks the last segment in the transcript
    chunk = words[istart:i]
    istart = i

    if chunk:
        segment = {
            "start": chunk[0]["start"],
            "end": chunk[-1]["end"],
            "text": " ".join([w["word"] for w in chunk]),
            "words": chunk
        }
        segments.append(segment)

    os.remove(audio_path)

    return segments