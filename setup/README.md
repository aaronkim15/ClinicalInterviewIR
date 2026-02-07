# Current Requirements
- Python (havnt confirmed version)
- Pip (havent confirmed version)
- Docker (free tier)

## Step 1: Setup N8N
N8N is run through docker, I reccomend opening the application to confirm status. Then through command line, activate this folder, create and activate a docker image using the following. Please note that once activated (last line) you can access N8N using http://localhost:5678. (NOT COMPLETE: But please find the started n8n flow within the src/n8n folder, and within n8n import as file.

```bash
docker build -t n8n_image:latest .
docker compose up -d
```

## Step 2: Python Virtual Environment
The Python code required for Pyannote (+possibly more later) is run through FastAPI using a virtual environment outside of Docker (to avoid bloating up our docker with imports). 
Within command line, activate the src/pyannote folder, then create and activate the virtual environment. Please note that when hosted (last line), FastAPI calls are done through http://localhost:8000/<name>

```bash
python3 -m venv script_env

.\script_env\Scripts\Activate.ps1

pip install fastapi uvicorn
pip install python-multipart
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install pyannote.audio ffmpeg-python

uvicorn diarize:app --host 0.0.0.0 --port 8000 --reload
```

## Step 3: Run The Front End
Currently the frontend is a HTML + JS file, within command line, activate the src/frontend folder then run the following. Within this front end, using HTTP call, we activate the n8n flow.

```bash
open index.html
```



