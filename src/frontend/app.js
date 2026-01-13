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

    startLiveVideo() {

    }

    async uploadVideoFile() {
        
        //Obtain Passed File
        const file = this.fileInput.files[0]
        
        //Confirm File Valid
        if (!file) {
            alert("Please Select A Valid Audio File");
            return;
        } 
        
        //Prepare Data
        const data = new FormData();
        data.append("file", file);
        
        try {
            //Send Request
            const response = await fetch("WEBHOOPLOCATIONURL", {
                method: "POST",
                body: data
            });

            //Confirm Response Valid
            if (!response.ok) {
                alert("Recieved Unexpected Request Response: " + response.statusText);
                return;
            }

        //Handle Failed Request
        } catch(err) {
            alert("Error Passing Request:"  + err.message);
        }
    }
}


document.addEventListener('DOMContentLoaded', () => {
    window.controller = new Controller();
});