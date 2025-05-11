from flask import Flask, request, Response, render_template
import subprocess
import os
import threading
import time
import webbrowser

app = Flask(__name__)

FORTRAN_PATH = "C:/Users/abhin/OneDrive/Desktop/fortran"
process_dict = {}  # Store subprocesses by session (for input injection)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    file_name = data.get("fileName")
    code_text = data.get("codeText")

    if not file_name or not code_text:
        return {"error": "Missing filename or code"}, 400

    os.chdir(FORTRAN_PATH)
    f90_file = f"{file_name}.f90"
    with open(f90_file, "w") as f:
        f.write(code_text)

    compile_cmd = f"gfortran {f90_file} -o {file_name}"
    result = subprocess.run(["cmd.exe", "/c", compile_cmd], capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}, 400

    return {"message": "Compiled successfully."}

@app.route("/run_stream/<file_name>")
def run_stream(file_name):
    def generate():
        run_cmd = f"./{file_name}.exe"
        proc = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        process_dict[file_name] = proc

        for line in iter(proc.stdout.readline, ''):
            yield f"data: {line}\n\n"
            if "?" in line or "READ" in line.upper():
                yield f"event: wait_input\ndata: waiting\n\n"

        proc.stdout.close()
        proc.wait()

    return Response(generate(), content_type="text/event-stream")

@app.route("/send_input", methods=["POST"])
def send_input():
    data = request.get_json()
    file_name = data.get("fileName")
    user_input = data.get("input", "") + "\n"

    proc = process_dict.get(file_name)
    if proc:
        try:
            proc.stdin.write(user_input)
            proc.stdin.flush()
            return {"message": "Input sent."}
        except Exception as e:
            return {"error": str(e)}, 500
    return {"error": "No active process."}, 404

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
