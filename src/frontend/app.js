class Controller {
    constructor() {
        this.panels = document.querySelectorAll('.panel');
        this.fileInput = document.getElementById('fileInput');
    }

    showPanel(id) {
        this.panels.forEach(p => p.classList.remove('active'));
        const panel = document.getElementById(id);
        if (panel) panel.classList.add('active');
    }

    startLiveAudio() {
    }

    async uploadAudioFile() {
        const file = this.fileInput.files[0];
        alert('Selected File: ' + (file ? file.name : 'None'));
        if (!file) {
            alert('No Audio File Selected')
            return
        } else {

            /* Caching Audio File*/
            const formData = new FormData();
            formData.append('audio', file);

            /* Initiating N8N Flow */
            try {
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.controller = new Controller();
});