def 






from typing import List
from pyannote.audio import Pipeline


def offline_speaker_seperation(audio_path:str, seperated_path:str, min_speakers:int=2, max_speakers:int=2):

    #Model Pipeline
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=True
    )

    #Applying Pipeline
    seperation = pipeline(audio_path=audio_path, 
                          min_speakers=min_speakers, 
                          max_speakers=max_speakers)
    
    speakers = set()

