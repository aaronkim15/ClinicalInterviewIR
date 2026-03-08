# Project Setup (Windows)

## Initial Requirements For Computer
- Python
- Pip
- Docker Desktop
- ffmpeg

## Environment Variable Fields
-GROQ_API_KEY
-HUGGINGFACE_TOKEN
-SUPABASE_URL
-SUPABASE_KEY
-LIVEKIT_API_KEY
-LIVEKIT_API_SECRET


## Setup Docker Image
Create And Then Activate Docker Image
```bash
cd src/docker
docker build -t n8n_image:latest .
docker compose --env-file ../../.env up -d
```

## Setup Python Virtual Environment + FastAPI
Create, Activate, Install Dependancies For Environement, Then Host FastAPI Endpoints. Success Can Be Tested Using http://localhost:8000/test-status
```bash
cd src/python_venv
python3 -m venv script_env
.\script_env\Scripts\Activate.ps1
pip install -r python_env_dependancies.txt

cd ..
uvicorn python_venv.endpoints:app --host 0.0.0.0 --port 8000 --reload
```

## Setup Supabase
Within Supabase SQL Editor, Run The Following:
```
create extension if not exists vector;
```
Then Paste The Contents Of src/supabase/supabase_segments.sql And Execute


Then Paste The Contents Of The src/supabase/supabase_segments.sql And Execute.
From Here, Use Your Supabase Credentials For The Supabase Node In N8N Flow

NOTE: Depending On The Cred Used, May Need To Setup Insert Policy: Please Find Mine Within src/supabase/supabase_segment_policy.png

## Setup N8N
Runs Within Docker And Can Be Accessed Using http://localhost:5678. 
Select "Create A New Flow", (...), "Import From File", Select Flow From src/n8n. 

NOTE: Supabase Credentials May Be Required (see Supabase Below)


## Running Front End
```bash
cd src/frontend
start index.html
```

NOTE: The File Upload Pipeline Is Complete From Front End To Supabase, Feel Tree To Test It With A Moderately Sized .WAV File. Everything Does Work, SO LONG As Your Credentials And Tokens Are Setup Properly. Reading The Python Error Messages And N8N Error Messages Will Help If You Experience Anything Weird