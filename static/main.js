// JavaScript function to handle button click and send data to backend
function run() {
    fetch("/compile", {
        method: "POST",  // HTTP method
        headers: { "Content-Type": "application/json" },  // Content type header
        body: JSON.stringify({
            codeText: document.querySelector(".codeText").value,  
            fileName: document.querySelector(".fileName").value,    
        })
    })
    .then(res => res.json())  // Parse the JSON response from the Flask server
    .then(data => {
        // Display the program output or error in the <pre> element
        document.getElementById("output").textContent = data.output || data.error;
    });
}
function inputConsole(){
    fetch("/console", {
        method: "POST",  // HTTP method
        headers: { "Content-Type": "application/json" },  // Content type header
        body: JSON.stringify({
            input: document.querySelector(".input").value,  
        })
    })
    .then(res => res.json())  // Parse the JSON response from the Flask server
    .then(data => {
        // Display the program output or error in the <pre> element
        document.getElementById("output").textContent = data.output || data.error;
    });
}
