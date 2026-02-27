from python_venv import _embedding, _diarization, _transcription
from fastapi import FastAPI, UploadFile, File, Form, Body
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import json

#FastAPI App Initialization
app = FastAPI(title="Pyannote Diarization")

@app.get("/status")
async def status() -> Dict[str, str]:
    return {"status": "ok", "message": "FastAPI Endpoint Reached"} 

@app.post("/transcribe-original-audio")
def transcribe_original_audio(audio_file: UploadFile = File(...)) -> List[Dict[str, Any]]:
    try:    
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.file.read())
            audio_path = str(Path(tmp.name))

        #NOTE: By Placing Diarize Here, I Avoid Passing And Saving The Audio File Through 2 Endpoints
        diarization = _diarization.get_diarization(audio_path=audio_path).speaker_diarization

        ret = _transcription.transcribe_original_audio(audio_path=audio_path, diarization=diarization)

        #TODO: Delete Temp?

        return [{"transcription": ret}]
        
    except Exception as e:
        return [{"status": "error", "text": f"Error In Transcribe Original Audio: {str(e)}"}]

@app.post("/index-text")
def index_text(metadata: str) -> List[Dict[str, Any]]:
    try: 
        audio_transcriptions = json.loads(metadata)["transcription"]
        texts = [segment["text"] for segment in audio_transcriptions]
        embeddings = _embedding.get_embeddings(texts)

        for embedding, transcription in zip(embeddings, audio_transcriptions):
            transcription["embedding"] = embedding

        return audio_transcriptions    
    except Exception as e:
        return [{"status": "error", "text": f"Error In Index Audio: {str(e)}"}]


@app.get("/retrieve-conversation") 
def retrieve_conversation() -> List[Dict[str, Any]]:
    try:
        return [{"response": _transcription.get_retrieval(query="Hi Hows Your Day Going", system_prompt="Please Respond To The User Kindly")}]
    except Exception as e:
        return [{"status": "error", "text": f"Error In Retrieval: {str(e)}"}]












#NOTE: Not Tested, As LiveKit Not Setup And This Is Based On Expected LiveKit Outputs, Subject To Change
#@app.post("/transcribe-seperated-audio")
def transcribe_separated_audio(audio_files: List[UploadFile] = File(...), metadata: str = Form(...)) -> dict:
    try:
        audio_paths = []
        metadata = json.loads(metadata)

        for audio_file in audio_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.file.read())
                audio_paths.append(str(Path(tmp.name)))

        ret = _transcription.transcribe_seperated_audio(audio_paths=audio_paths, metadata=metadata)

        #TODO: Clear Temp Files
        
        return [{"transciption:": ret}]
    
    except Exception as e:
        raise RuntimeError(f"Error In Transcribe Separated Audio: {str(e)}")
    
#NOTE: Not In Use, For Efficiency Reasons Moved Into Transcribe
#@app.post("/diarize-original-audio")
async def diarize_original_audio(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio.read())
            audio_path = str(Path(tmp.name))
        return [{"diarization": _diarization.get_diarization(audio_path=audio_path)}]
    except Exception as e:
        raise RuntimeError(f"Error In Diarized Original Audio: {str(e)}")