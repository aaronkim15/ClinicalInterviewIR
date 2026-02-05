##Python And Dependancies For Pyannote Are Within Virtual Env

##ALTERNATIVE: Inside Docker Container

python -m venv pyannote-env
pyannote-env\Scripts\activate
pip install fastapi uvicorn pyannote.audio torch torchaudio librosa
uvicorn main:app --reload --host 0.0.0.0 --port 8000
