from fastapi import FastAPI, UploadFile, File
import torch
from pyannote.audio import Pipeline
import soundfile as sf
from typing import List, Dict
from groq import Groq
import os
from pathlib import Path
import tempfile
from pydub import AudioSegment

app = FastAPI(title="Pyannote Diarization")

HUGGINGFACE_TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "HuggingFace_token.txt"
GROQ_TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "Groq_token.txt"

with open(HUGGINGFACE_TOKEN_PATH, "r") as f:
    huggingface_token = f.read().strip()

with open(GROQ_TOKEN_PATH, "r") as f:
    groq_token = f.read().strip()   

huggingface_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=huggingface_token)

groq_client = Groq(api_key=groq_token)



@app.get("/status")
async def status_check():
    return {"status": "ok", "message": "FastAPI Endpoint Reached"}

@app.post("/diarize")
async def diarize(audio: UploadFile = File(...)):
    try:
        #Writing N8N File To Temp File
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = Path(tmp.name)

        #Splitting Audio
        data, sample_rate = sf.read(tmp_path, dtype='float32')
        if data.ndim == 1:
            waveform = torch.tensor(data).unsqueeze(0)
        else:
            waveform = torch.tensor(data).T

        #Diarizing Audio 
        diarization = huggingface_pipeline({"waveform": waveform, "sample_rate": sample_rate})

        #Breaking Into Diarized Portions
        ret = []
        for turn, speaker in diarization.speaker_diarization:
            ret.append({
                "speaker": speaker,
                "start": round(turn.start, 2),
                "end": round(turn.end, 2)
            })

        #WHISPER STUFF, WILL MOVE INTO SEPERATE FUNCTION LATER, BUT FOR NOW TESTING ITS TOGETHER
        #--------------------------------------------------------------------------------------------
        audio_file = AudioSegment.from_file(tmp_path)

        for segment in ret:

            clip = audio_file[segment["start"]*1000:segment["end"]*1000]

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name 
                clip.export(temp_file_path, format="wav")

            with open(temp_file_path, "rb") as f:   # open the file as binary
                segment_ret = groq_client.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json"
                )

            segment["text"] = segment_ret.text

            os.unlink(temp_file_path)


        os.unlink(tmp_path) 


        return ret

    except Exception as e:
        return {"status": "error", "error": str(e)}
    

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), segments: List[Dict] = None):
    try:
        #Writing N8N File To Temp File
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = Path(tmp.name)

        




    except Exception as e:
        return {"status": "error", "error": str(e)}

    

