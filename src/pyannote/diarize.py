from fastapi import FastAPI, UploadFile, File

import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

import os
from pathlib import Path
import tempfile

app = FastAPI(title="Pyannote Diarization")

TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "HuggingFace_token.txt"

with open(TOKEN_PATH, "r") as f:
    token = f.read().strip()


pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=token)



@app.get("/status")
async def status_check():
    return {"status": "ok", "message": "FastAPI Endpoint Reached"}


@app.post("/diarize")
async def diarize(audio: UploadFile = File(...)):

    try:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = Path(tmp.name)


        #diarized = pipeline(tmp_path)

        return {"status": "ok", "message": "Diarization Endpoint Reached After Temp"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    # try:
    #     return {"status": "ok", "message": "Diarization Endpoint Reached After Temp"}
    #     diarization = pipeline(tmp_path)

    #     return {"status": "ok", "message": "Diarization Endpoint Reached"}
    # except Exception as e:
    #     return {"status": "error", "message": str(e)}