let sessionId = null;
const BACKEND_URL = 'https://fortran-live-compiler.onrender.com'
    function compileAndRun() {
      const fileName = document.querySelector(".fileName").value.trim();
      const codeText = document.querySelector(".codeText").value.trim();
      const output = document.getElementById("output");
      output.textContent = "";
      sessionId = null;

      fetch(`${BACKEND_URL}/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName, codeText })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) return alert("❌ " + data.error);
        sessionId = data.session_id;
        listenToOutput(fileName, sessionId);
      })
      .catch(err => alert("⚠️ Compilation error: " + err.message));
    }

    function listenToOutput(fileName, sessionId) {
      const eventSource = new EventSource(`${BACKEND_URL}/run_stream/${sessionId}/${fileName}`);
      const output = document.getElementById("output");

      eventSource.onmessage = function (event) {
        output.textContent += event.data + '\n';
      };

      eventSource.addEventListener("wait_input", function () {
        document.getElementById("inputBox").style.display = "block";
      });

      eventSource.onerror = function () {
        eventSource.close();
      };
    }

    function sendInput() {
      const fileName = document.querySelector(".fileName").value.trim();
      const input = document.getElementById("inputField").value.trim();
      const output = document.getElementById("output");
      output.textContent += "> " + input + '\n';
      
      if (!input || !sessionId) return;

      fetch(`${BACKEND_URL}/send_input`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName, input, session_id: sessionId })
      })
      .then(() => {
        document.getElementById("inputField").value = "";
        //document.getElementById("inputBox").style.display = "none";
      })
      .catch(err => alert("⚠️ Failed to send input: " + err.message));
    }