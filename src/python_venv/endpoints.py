from python_venv import _diarize, _embed, _generate, _retrieve, _transcribe
from fastapi import FastAPI, UploadFile, File, Form, Body
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import json

#FastAPI App Initialization
app = FastAPI(title="Pyannote Diarization")

#NOTES:
#- Files Named "_{name}" As Considered Internal, As Such Error Handling Needs To Be Done In This Outer Layer




#TEST ENDPOINTS: (NOT USED IN PIPELINE)

@app.get("/test-generation") 
def test_generation() -> List[Dict[str, Any]]:
    try:
        return [{"response": _generate.get_generation(query="Hi Hows Your Day Going", system_prompt="Please Respond To The User Kindly")}]
    except Exception as e:
        return [{"status": "error", "text": f"Error In Generation Retrieval: {str(e)}"}]

@app.get("/test-retrieval")
def test_retrieval() -> List[Dict[str, Any]]:
    try:
        query_vector = _embed.get_embeddings(["Russian, Demography"])[0]
        return [{"response": _retrieve.get_retrieval(query_vector=query_vector)}]
    except Exception as e:
        return [{"status": "error", "text": f"Error In SubSet Retieval: {str(e)}"}]

@app.get("/test-status")
def test_status() -> Dict[str, str]:
    return {"status": "ok", "message": "FastAPI Endpoint Reached"} 





#LIVE ENDPOINTS IN PIPELINE:
@app.post("/transcribe-original-audio")
def transcribe_original_audio(audio_file: UploadFile = File(...)) -> List[Dict[str, Any]]:
    """
    An endpoint which transcribes a supplied original audio file. Intended for file upload portion of project
    
    Arguments:
        audio_file: The audio file to transcribe

    Returns: A list of dictionaries representing conversational segments

    Notes: To avoid extra N8N nodes and needing to pass data more then necessary, the diarization method is called within this endpoint
    """
    try:    
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.file.read())
            audio_path = str(Path(tmp.name))

        diarization = _diarize.get_diarization(audio_path=audio_path)

        ret = _transcribe.transcribe_original_audio(audio_path=audio_path, diarization=diarization)

        #TODO: Delete Temp?

        return [{"transcription": ret}]
        
    except Exception as e:
        return [{"status": "error", "text": f"Error In Transcribe Original Audio: {str(e)}"}]

@app.post("/index-text")
def index_text(metadata: str) -> List[Dict[str, Any]]:
    """
    An endpoint which indexes supplied transcription, and handles embedding

    Arguments:
        metadata: string json transcription data

    Returns: JSON transcription data with embeddings, etc added
    """
    try: 
        audio_transcriptions = json.loads(metadata)["transcription"]
        texts = [segment["text"] for segment in audio_transcriptions]
        embeddings = _embed.get_embeddings(texts)

        for embedding, transcription in zip(embeddings, audio_transcriptions):
            transcription["embedding"] = embedding

        return audio_transcriptions    
    except Exception as e:
        return [{"status": "error", "text": f"Error In Index Audio: {str(e)}"}]



#OLD/IN PROGRESS


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

        ret = _transcribe.transcribe_seperated_audio(audio_paths=audio_paths, metadata=metadata)

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
        return [{"diarization": _diarize.get_diarization(audio_path=audio_path)}]
    except Exception as e:
        raise RuntimeError(f"Error In Diarized Original Audio: {str(e)}")