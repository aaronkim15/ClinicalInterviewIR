docker build -t n8n_image:latest .
docker compose up -d

docker exec n8n_python pip install --upgrade pip

#Not Confirmed To Work:
docker exec n8n_python pip install pyannote.audio torch torchaudio ffmpeg-python


docker compose down
docker rmi n8n_image:latest
