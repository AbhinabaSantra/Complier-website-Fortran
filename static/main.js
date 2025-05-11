
function compileAndRun() {
      const fileName = document.querySelector(".fileName").value;
      const codeText = document.querySelector(".codeText").value;
      document.getElementById("output").textContent = "";

      fetch("/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName, codeText })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) return alert(data.error);
        listenToOutput(fileName);
      });
    }

    function listenToOutput(fileName) {
      const eventSource = new EventSource(`/run_stream/${fileName}`);
      const output = document.getElementById("output");

      eventSource.onmessage = function (event) {
        output.textContent += event.data +'\n';
      };

      eventSource.addEventListener("wait_input", function () {
        document.getElementById("inputBox").style.display = "block";
      });

      eventSource.onerror = function () {
        eventSource.close();
      };
    }

    function sendInput() {
      const fileName = document.querySelector(".fileName").value;
      const input = document.getElementById("inputField").value;
      const output = document.getElementById("output");
      inputValue = input + '\n'  
      output.textContent+=inputValue
      fetch("/send_input", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName, input })
      })
      .then(() => {
        document.getElementById("inputField").value = "";
      });
    }