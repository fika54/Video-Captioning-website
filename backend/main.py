from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from transcriber import transcribe_audio
from utils import extract_audio
import uuid
from burnincaptions import generate_ass_file, burn_in_captions, get_video_dimensions


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

CAPTION_DIR = "captions"
os.makedirs(CAPTION_DIR, exist_ok=True)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(
    file: UploadFile,
    mode: str = Form(...),  # 'batch' or 'word'
):
    file_id = str(uuid.uuid4())
    temp_input = f"temp_{file_id}.mp4"
    temp_ass = f"temp_{file_id}.ass"
    temp_output = f"output_{file_id}.mp4"



    filepath = os.path.join(UPLOAD_DIR, temp_input)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    audio_path = extract_audio(filepath)
    segments = transcribe_audio(audio_path, mode=mode)

    assFilePath = os.path.join(CAPTION_DIR, temp_ass)

    vidwidth,vidheight = get_video_dimensions(filepath)

    generate_ass_file(segments, assFilePath, vidwidth, vidheight)


    outputFilePath = os.path.join(OUTPUT_DIR, temp_output)


    assFilePath = os.path.normpath(assFilePath).replace("\\", "/")
    filepath = os.path.normpath(filepath).replace("\\", "/")
    outputFilePath = os.path.normpath(outputFilePath).replace("\\", "/")

    burn_in_captions(filepath, assFilePath, outputFilePath)

    os.remove(filepath)
    os.remove(assFilePath)


#    return JSONResponse(content={"segments": segments})
    return FileResponse(outputFilePath, filename="captioned.mp4", media_type="video/mp4")


# @app.post("/upload/")
# async def upload_video(file: UploadFile = File(...)):
#     file_id = str(uuid.uuid4())
#     temp_input = f"temp_{file_id}.mp4"
#     temp_ass = f"temp_{file_id}.ass"
#     temp_output = f"output_{file_id}.mp4"

#     # Save uploaded file
#     with open(temp_input, "wb") as f:
#         f.write(await file.read())

#     # Process video
#     segments = transcribe_audio(temp_input)
#     generate_ass_file(segments, temp_ass)
#     burn_in_captions(temp_input, temp_ass, temp_output)

#     # Cleanup inputs
#     os.remove(temp_input)
#     os.remove(temp_ass)

#     return FileResponse(temp_output, filename="captioned.mp4", media_type="video/mp4")