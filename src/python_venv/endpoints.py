# from python_venv import _diarize, _embed, _generate, _retrieve, _transcribe
from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import json
import os
from livekit import api
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
ENV_PATH = Path(__file__).resolve().parents[1] / "docker" / ".env"
load_dotenv(dotenv_path=ENV_PATH)
class LiveKitTokenRequest(BaseModel):
    room_name: str
    participant_identity: str
    participant_name: str | None = None

#FastAPI App Initialization
app = FastAPI(title="Core Python Code")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.post("/livekit-token")
def create_livekit_token(payload: LiveKitTokenRequest) -> dict:
    try:
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        print("LIVEKIT_API_KEY:", api_key)
        print("LIVEKIT_API_SECRET exists:", api_secret is not None)

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be set")
        
        token= (
            api.AccessToken()
            .with_identity(payload.participant_identity)
            .with_name(payload.participant_name or payload.participant_identity)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=payload.room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .to_jwt()
        )
        return{
            "server_url": "ws://localhost:7880",
            "participant_token": token,
        }
    except Exception as e:
        return{
            "status": "error",
            "text": f"Error creating LiveKit token: {str(e)}"
        }

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

        segments = _transcribe.transcribe_original_audio(audio_path=audio_path, diarization=diarization)

        os.remove(audio_path)

        segments = _generate.get_generated_roles(segments=segments)

        return [{"transcription": segments}]
        
    except Exception as e:
        return [{"status": "error", "text": f"Error In Transcribe Original Audio: {str(e)}"}]

@app.post("/transcribe-seperated-audio")
def transcribe_seperated_audio():
    #TODO: When Outputs From Livekit Are Known
    pass

#NOTE: This is actually embedding for now all indexing is done by supabase automatically
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





def get_generated_responses(system_prompt_name: str, query:str = None, speaker:str = None, segment_count:int = 50):
    
    query_vector = _embed.get_embeddings(["Medical"])[0]
    
    segments = _retrieve.get_retrieval(query_vector=query_vector, speaker=speaker, segment_count=segment_count)

    segments_str = json.dumps(segments)

    system_prompt = (Path(__file__).resolve().parents[2] / "prompts" / system_prompt_name).read_text()

    return _generate.get_generation(query=f"{query}: {segments_str}", system_prompt=system_prompt)


@app.post("/generate-summary")
def generate_summary(speaker:str = None, segment_count:int = 20) -> str:
    try:
        return get_generated_responses(system_prompt_name="SUMMARIZATION.txt", query=None, speaker=speaker, segment_count=segment_count)
    except Exception as e:
            return [{"status": "error", "text": f"Error In Generate Summary: {str(e)}"}]

@app.post("/generate-analysis")
def generate_analysis(speaker:str = None, segment_count:int = 20) -> str:
    try:
        return get_generated_responses(system_prompt_name="ANALYZER.txt", query=None, speaker=speaker, segment_count=segment_count)
    except Exception as e:
            return [{"status": "error", "text": f"Error In Generate Analysis: {str(e)}"}]

@app.post("/generate-answer")
def generate_answer(query:str, speaker:str = None, segment_count:int = 20) -> str:
    try:
        return get_generated_responses(system_prompt_name="QUESTIONS.txt", query=query, speaker=speaker, segment_count=segment_count)
    except Exception as e:
            return [{"status": "error", "text": f"Error In Generate Answer: {str(e)}"}]







#OLD/IN PROGRESS

#NOTE: Not Tested, As LiveKit Not Setup And This Is Based On Expected LiveKit Outputs, Subject To Change
#@app.post("/transcribe-seperated-audio")
"""
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
"""