console.log("app.js loaded");

class Controller {
    constructor() {
        this.panels = document.querySelectorAll('.panel');
        this.fileInput = document.getElementById('fileInput');
        this.patientStream = null;
        this.clinicianStream = null;
        this.patientPublication = null;
        this.clinicianPublication = null;
        this.room = null;
    }

    showPanel(id) {
        this.panels.forEach(p => p.classList.remove('active'));
        const panel = document.getElementById(id);
        if (panel) panel.classList.add('active');
    }
    
    async assignAudioDevice(role, event){
        console.log("assignAudioDevice called", role, event);
        const existingLabel = document.getElementById(role === 'patient' ? 'patientAudio' : 'clinicianAudio');
        const assignButton = event.target;

        try{
            //Stop Existing Stream
            if(role === 'patient' && this.patientStream){
                this.patientStream.getTracks().forEach(t => t.stop());
            } else if (role == 'clinician' && this.clinicianStream) {
                this.clinicianStream.getTracks().forEach(t => t.stop());
            }

            //Popup For Access
            const stream = await navigator.mediaDevices.getUserMedia({audio: true});
            const track = stream.getAudioTracks()[0];
            const name = track.label

            if(role === 'patient'){
                this.patientStream = stream;
            } else {
                this.clinicianStream = stream;
            }

            existingLabel.textContent = name;
            assignButton.classList.add('assigned');

        } catch (error) {
            alert(`Failed: ${error.message}`)
        }
    }
    async fetchLiveKitToken(){
        const response = await fetch("http://localhost:8000/livekit-token", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({
                room_name: "test-room",
                participant_identity: `user-${Date.now()}`,
                participant_name: "Frontend User",
            }),
        });

        const data = await response.json();

        if (!response.ok || data.status === "error"){
            throw new Error(data.text || "Failed to fetch LiveKit Token");
        }

        return data;
    }
    async startLiveAudio() {
        console.log("startLiveAudio called");
        const existingStatus = document.getElementById('streamStatus')
        
        try{
            // identifies the patient and the clinician.
            if (!this.patientStream || !this.clinicianStream){
                alert('Please Assign Both Roles Audio')
                return;
            } 
            if (document.getElementById("patientAudio").textContent ===
                document.getElementById("clinicianAudio").textContent){
                alert("Audio sources are identical. Please choose separate sources.");
                return;
            }

            // declares the room has already begun
            if(this.room){
                alert("Live audio is already running.");
                return;
            }

            // change the content on the html to connecting.
            existingStatus.textContent = "Connecting";

            // create variables to store the live kit url and the participant token.
            const { server_url, participant_token } = await this.fetchLiveKitToken();

            console.log("Server URL:", server_url);
            console.log("Got Participant:", participant_token);

            // create a livekit client room.
            const room = new LivekitClient.Room();

            room
                .on(LivekitClient.RoomEvent.Connected, () => {
                    console.log("Connected to LiveKit room");
                })
                .on(LivekitClient.RoomEvent.Disconnected, () =>{
                    console.log("Disconnected from LiveKit room");
                })
                .on(LivekitClient.RoomEvent.ConnectionStateChanged, (state) => {
                    console.log("Connection state:", state);
                });

            await room.connect(server_url, participant_token);
            const patientTrack = this.patientStream.getAudioTracks()[0];
            const clinicianTrack = this.clinicianStream.getAudioTracks()[0];

            if (!patientTrack || !clinicianTrack){
                throw new Error("missing one or more audio tracks");
            }

            this.patientPublication = await room.localParticipant.publishTrack(patientTrack, {
                name: "patient",
                source: LivekitClient.Track.Source.Microphone,
            });

            this.clinicianPublication = await room.localParticipant.publishTrack(clinicianTrack, {
                name: "clinician",
                source: LivekitClient.Track.Source.Microphone,
            });

            this.room = room;
            existingStatus.textContent = "Running";
        } catch(error){
            console.error("LiveKit connection error:", error);
            existingStatus.textContent = "Not Running";
            alert(`Failed to connect to LiveKit: ${error.message}`);
        }
    }

    async stopLiveAudio(){
        const existingStatus = document.getElementById("streamStatus");

        try{
            if(this.room){
                const patientTrack = this.patientStream?.getAudioTracks?.()[0];
                const clinicianTrack = this.clinicianStream?.getAudioTracks?.()[0];

                if (patientTrack){
                    this.room.localParticipant.unpublishTrack(patientTrack);
                }

                if (clinicianTrack){
                    this.room.localParticipant.unpublishTrack(clinicianTrack);
                }

                await this.room.disconnect();
                this.room = null;
                this.patientPublication = null;
                this.clinicianPublication = null;
            }

            existingStatus.textContent = 'Not Running';
        } catch (error){
            console.error("Error disconnecting:", error);
            alert(`Failed to stop LiveKit audio: ${error.message}`);
        }
    }

    async uploadAudioFile() {
        const file = this.fileInput.files[0];
        if (!file) {
            alert('No Audio File Selected')
            return
        } else {
            //Caching Audio File
            const formData = new FormData();
            formData.append('audio', file);

            //Initiating N8N Flow
            try {
                alert("Starting Flow");
                const response = await fetch("http://localhost:5678/webhook/upload-audio", {
                    method: "POST",
                    body: formData
                });
                const data = await response.text();
                alert('N8N Output: ' + JSON.stringify(data))
            } catch(error) {
                alert('Error Uploading File: ' + error);
            }   
        }
    }

    async retrievalModule_1(){

    }

    async retrievalModule_2(){

    }

    async retrievalModule_3(){

    }


    async evaluationModules(){

    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.controller = new Controller();
});