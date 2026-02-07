# Current Requirements
- Python (havnt confirmed version)
- Pip (havent confirmed version)
- Docker (free tier)

## Step 1: Setup N8N
N8N is run through docker, I reccomend opening the application to confirm status. Then through command line, create and activate a docker image using the following 

`docker build -t n8n_image:latest .

docker compose up -d

docker exec n8n_python pip install --upgrade pip
docker exec n8n_python pip install pyannote.audio torch torchaudio ffmpeg-python`


docker compose down
docker rmi n8n_image:latest
