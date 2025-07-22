import ffmpeg
import os

def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k')
        .overwrite_output()
        .run()
    )
    return audio_path