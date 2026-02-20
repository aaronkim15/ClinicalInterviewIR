from pathlib import Path
from typing import List, Dict, Any
from groq import Groq
import tempfile
from pydub import AudioSegment


TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "Groq_token.txt"

with open(TOKEN_PATH, "r") as f:
    api_key = f.read().strip()   
    groq_client = Groq(api_key=api_key)


def get_transcription(audio_path: str) -> Dict[str, Any]:
    """
    Transcribes Given Audio File Using Groq Whisper API Client

    Args:
        audio_path (str): Path To Audio File To Transcribe

    Returns:
        Dict[str, Any]: Dictionary Representation Of Transcription: Text, Timestamps, Segments, etc
    """
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

def transcribe_original_audio(audio_path:str, diarization:List) -> List[Dict[str, Any]]:

    ret = []    
    audio = AudioSegment.from_file(audio_path)

    for segment, speaker in diarization:

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

        #TODO: Delete Temp File?
    return ret

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