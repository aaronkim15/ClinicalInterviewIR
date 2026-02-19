# Project Setup (Windows)

## Initial Requirements
- Python
- Pip
- Docker Desktop
- ffmpeg


## Step 1: Setup Docker Image
Run The Following In The Command Line To Setup Then Activate Docker Image. You Can Confirm Setup By Checking Within The Images Tab In Docker Desktop. 

```bash
docker build -t n8n_image:latest .
docker compose up -d
```

## Step 2: Setup N8N
N8N Runs Within Docker, And Can Be Accessed Using http://localhost:5678. 
Within In Create A New Flow, Then Press (...), Then Import From File. Select Flow From The src/n8n folder. Then Press Publish To Use. (See Step 5 For Credentials)

## Step 3: Setup Python Virtual Environment
Within The Command Line Select The src/FastAPI Folder. Create, Then Activate Then Load Imports Into The New Environment
```
python3 -m venv script_env

.\script_env\Scripts\Activate.ps1

pip install -r ../../setup/env_requirements.txt
```
## Step 4: Setup FastAPI
Within The src/FastAPI Folder In The Command Line, Run The Following To Publish The Endpoints. Confirm Setup With http://localhost:8000/status
```
uvicorn endpoints:app --host 0.0.0.0 --port 8000 --reload
```
NOTE: Auth Tokens Are Required For Hugging Face And Groq. See Code For Exact Requirements, Place Yours Within The tokens Folder.

## Step 5: Setup Supabase
Create A Supabase Account If You Dont Have One. Within SQL Editor, Enable vector Extension
```
create extension if not exists vector;
```
From Here Create The Segment Table Using The Create Statement Within setup/supabase_segments.sql.

Finally, Linking Your Supabase Account With N8N, Within The Supabase Node, Create A Credential Matching Your Supabase Account. You Can Find Account Details Under The Connect Button Within Supabase

NOTE: Depending On Default Settings, You May Also Need To Update Your Insert Policy. (TODO: Wrap Into File) Not Sure If These Settings Will Work For Everyone But For Now Ive Attached A Photo With A Simple Anon Policy.

## Step 6: Running Front End
From Here You Can Activate The Front End. Activate The src/Frontend Folder Within Command Line, Then Run
```bash
open index.html
```

NOTE: The File Upload Pipeline Is Complete, Feel Free To Test It With A Simple .WAV File. Ive Confirmed Everything Works As Is, SO LONG As Your Credentials And Tokens Are Setup Properly. 

Many Of The Errors I Experienced Earlier Had To Do With Tokens, And Reading The Python Errors, As Well As N8N Errors Will Help You Understand How To Fix Any Problems You Encounter.