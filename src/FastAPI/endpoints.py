from fastapi import FastAPI, UploadFile, File, Form
import torch
from pyannote.audio import Pipeline
import soundfile as sf
from typing import List, Dict, Any
from groq import Groq
import os
from pathlib import Path
import tempfile
from pydub import AudioSegment
import json
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Pyannote Diarization")

HUGGINGFACE_TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "HuggingFace_token.txt"
GROQ_TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "Groq_token.txt"

with open(HUGGINGFACE_TOKEN_PATH, "r") as f:
    huggingface_token = f.read().strip()

with open(GROQ_TOKEN_PATH, "r") as f:
    groq_token = f.read().strip()   

huggingface_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=huggingface_token)

groq_client = Groq(api_key=groq_token)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')





@app.get("/status")
async def status_check():
    return {"status": "ok", "message": "FastAPI Endpoint Reached"} 






def get_diarization(audio_path: str) -> Dict[str, Any]:
    try:
        data, sample_rate = sf.read(audio_path, dtype='float32')
        if data.ndim == 1:
            waveform = torch.tensor(data).unsqueeze(0)
        else:
            waveform = torch.tensor(data).T

        diarization = huggingface_pipeline({"waveform": waveform, "sample_rate": sample_rate})
        return diarization
    except Exception as e:
        raise RuntimeError(f"Pyannote Diarization Error: {str(e)}")


def get_transcription(audio_path: str) -> Dict[str, Any]:
    with open(audio_path, "rb") as f:
        try:
            result = groq_client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                response_format="verbose_json"
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Groq Transcription Error: {str(e)}")
    return result

def get_embeddings(texts: List[str]) -> List[List[float]]:
    try:
        embeddings = embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True                                    
        )
        return embeddings.tolist()
    except Exception as e:
        raise RuntimeError(f"Embedding Generation Error: {str(e)}")





@app.post("/diarize-original-audio")
async def diarize_original_audio(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio.read())
            audio_path = str(Path(tmp.name))

        diarization = get_diarization(audio_path=audio_path)
        ret = []

        for turn, speaker in diarization.speaker_diarization:
            ret.append({
                "speaker": speaker,
                "start": round(turn.start, 2),
                "end": round(turn.end, 2)
            })

        return ret
    
    except Exception as e:
        raise RuntimeError(f"Error In Diarized Original Audio: {str(e)}")

@app.post("/transcribe-separated-audio")
def transcribe_separated_audio(audio_files: List[UploadFile] = File(...), metadata: str = Form(...)) -> dict:
    try:
        audio_participants = json.loads(metadata)
        ret = []

        for id, (audio_file, audio_participant) in enumerate(zip(audio_files, audio_participants)):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.file.read())
                audio_path = str(Path(tmp.name))

            transcription = get_transcription(audio_path=audio_path)

            for segment in transcription.segments:
                ret.append({
                    "speaker": "SPEAKER_" + str(id),
                    "start": audio_participant["start"] + segment.start,
                    "end": audio_participant["start"] + segment.end,
                    "text": segment.text
                })

        return ret
    except Exception as e:
        raise RuntimeError(f"Error In Transcribe Separated Audio: {str(e)}")
    
@app.post("/transcribe-original-audio")
def transcribe_original_audio(audio_file: UploadFile = File(...)):
    try:    
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.file.read())
            audio_path = str(Path(tmp.name))

        ret = []
        audio_diarization = get_diarization(audio_path=audio_path).speaker_diarization
        audio = AudioSegment.from_file(audio_path)

        for segment, speaker in audio_diarization:

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_segment:
                audio[int(segment.start*1000):int(segment.end*1000)].export(tmp_segment.name, format="wav")
                segment_path = str(Path(tmp_segment.name))

            #NOTE: ALready Diarized, So Assume Block Text Within Segment
            transcription = get_transcription(audio_path=segment_path)

            ret.append({
                "speaker": speaker,
                "start": segment.start,
                "end": segment.end,
                "text": transcription.text
            })

        return ret
    except Exception as e:
        return {"status": "error", "text": f"Error In Transcribe Original Audio: {str(e)}"}

@app.post("/index-audio")
def index_audio(metadata: Any):

    try: 
        #NOTE: Since audio comes from conversation, and we already divide by noticable gaps (live) or change or speaker (pyannote)
        # going to assume those form sufficient chunks for indexing.

        audio_transcriptions = metadata #json.loads(metadata)
        texts = [segment["text"] for segment in audio_transcriptions]
        embeddings = get_embeddings(texts)

        for embedding, transcription in zip(embeddings, audio_transcriptions):
            transcription["embedding"] = embedding

        return audio_transcriptions
    except Exception as e:
        return {"status": "error", "text": f"Error In Index Audio: {str(e)}"}

