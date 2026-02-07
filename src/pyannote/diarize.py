from fastapi import FastAPI, UploadFile, File
from pyannote.audio import Pipeline
import shutil
from fastapi.responses import JSONResponse
import traceback
import os

app = FastAPI(title="Pyannote Diarization")

#pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")


@app.get("/status")
async def status_check():
    return {"status": "ok", "message": "FastAPI Endpoint Reached"}
