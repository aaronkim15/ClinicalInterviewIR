from pathlib import Path
from typing import List, Dict, Any
from groq import Groq
import tempfile
from pydub import AudioSegment
from groq.types.audio import Transcription
from pyannote.core import Annotation
import os
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_transcription(audio_path: str) -> Transcription:
    """
    Transcribes audio file

    Arguments:
        audio_path: Path to specified audio file

    Returns: A transcription object containing file transcription
    """
    with open(audio_path, "rb") as f:
        result = groq_client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3-turbo",
            response_format="verbose_json"
        )
        return result
     
def transcribe_original_audio(audio_path:str, diarization:Annotation) -> List[Dict[str, Any]]:
    """
    Transcribes an audio file into chunks corrasponding to supplies diarization

    Arguments:
        audio_path: Path to audio to transcribe
        diarization: An annotation object outlining speaker segment timestamps
    
    Returns: A list of dictionaries representing a conversational segment
    """
    ret = []    
    audio = AudioSegment.from_file(audio_path)

    for segment, speaker in diarization.speaker_diarization:

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_segment:
            audio[int(segment.start*1000):int(segment.end*1000)].export(tmp_segment.name, format="wav")
            segment_path = str(Path(tmp_segment.name))

        transcription = get_transcription(audio_path=segment_path)

        ret.append({
            "speaker": speaker,
            "start": segment.start,
            "end": segment.end,
            "text": transcription.text
        })

        os.remove(segment_path)
    return ret


#TODO: Test, As LiveKit hasnt been yet made
def transcribe_seperated_audio(audio_paths:List[str], metadata:Any) -> Any:

    ret = []

    for id, (audio_path, speaker_metadata) in enumerate(zip(audio_paths, metadata)):
            
        transcription = get_transcription(audio_path=audio_path)

        for segment in transcription.segments:
            ret.append({
                "speaker": "SPEAKER_" + str(id),
                "start": speaker_metadata["start"] + segment.start,
                "end": speaker_metadata["start"] + segment.end,
                "text": segment.text
            })

    return ret
