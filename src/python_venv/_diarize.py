from pathlib import Path
import torch
import os
from pyannote.audio import Pipeline
from pyannote.core import Annotation
from typing import Dict, Any
import soundfile as sf


huggingface_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=os.getenv("HUGGINGFACE_TOKEN"))


def get_diarization(audio_path: str) -> Annotation:
    """
    Diarizes a selected audio file

    Arguments:
        audio_path: Local audio file path to diarize

    Returns: An Annotation object describing labeled time segments
    """
    data, sample_rate = sf.read(audio_path, dtype='float32')
    if data.ndim == 1:
        waveform = torch.tensor(data).unsqueeze(0)
    else:
        waveform = torch.tensor(data).T
    diarization = huggingface_pipeline({"waveform": waveform, "sample_rate": sample_rate})
    return diarization
