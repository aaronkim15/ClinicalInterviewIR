from pyannote.audio import Pipeline
import os
from pathlib import Path
import tempfile
import soundfile as sf
import torch

TOKEN_PATH  =Path(__file__).parent.parent.parent / "tokens" / "HuggingFace_token.txt"

with open(TOKEN_PATH, "r") as f:
    token = f.read().strip()

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=token)

audio_path = "C:/Users/ldunc/Downloads/testAudio.mp3"


data, sample_rate = sf.read(audio_path, dtype='float32')

if data.ndim == 1:
    waveform = torch.tensor(data).unsqueeze(0)
else:
    waveform = torch.tensor(data).T 

diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})

print("After Making Pipeline")

# -------------------------
# Print results
# -------------------------
# diarization is now a DiarizeOutput
# for segment, track in diarization.segments.items():
#     speaker = track  # this is the label
#     start = segment.start
#     end = segment.end
#     print(f"{start:.1f}-{end:.1f} -> {speaker}")

# diarization is your DiarizeOutput object
for turn, speaker in diarization.speaker_diarization:
    print(f"{speaker} speaks between t={turn.start:.3f}s and t={turn.end:.3f}s")


