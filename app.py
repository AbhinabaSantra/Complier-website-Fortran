from flask import Flask, request, Response, render_template, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import threading
import time
import webbrowser
import uuid
import shutil

app = Flask(__name__)
CORS(app)
active_processes = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    file_name = data.get("fileName", "").strip()
    code_text = data.get("codeText", "")

    if not file_name or not code_text:
        return jsonify({"error": "Missing filename or code"}), 400

    # Create a secure temporary working directory
    session_id = str(uuid.uuid4())
    work_dir = os.path.join(tempfile.gettempdir(), f"fortran_{session_id}")
    os.makedirs(work_dir, exist_ok=True)

    f90_file_path = os.path.join(work_dir, f"{file_name}.f90")

    try:
        with open(f90_file_path, "w") as f:
            f.write(code_text)

        # Compile the Fortran code safely
        compile_cmd = ["gfortran", f"{file_name}.f90", "-o", file_name]
        result = subprocess.run(compile_cmd, cwd=work_dir, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        # Store session info for input
        active_processes[file_name] = {"work_dir": work_dir, "session": session_id}
        return jsonify({"message": "Compiled successfully.", "session_id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/run_stream/<session_id>/<file_name>")
def run_stream(session_id, file_name):
    process_key = f"{session_id}_{file_name}"
    proc_info = active_processes.get(file_name)
    if not proc_info or proc_info["session"] != session_id:
        return Response("Invalid session or file name.", status=404)

    def generate():
        run_path = os.path.join(proc_info["work_dir"], file_name)
        proc = subprocess.Popen(
            [run_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        active_processes[process_key] = proc

        for line in iter(proc.stdout.readline, ''):
            yield f"data: {line}\n\n"
            if "?" in line or "READ" in line.upper():
                yield f"event: wait_input\ndata: waiting\n\n"

        proc.stdout.close()
        proc.wait()

        shutil.rmtree(proc_info["work_dir"], ignore_errors=True)
        active_processes.pop(process_key, None)

    return Response(generate(), content_type="text/event-stream")

@app.route("/send_input", methods=["POST"])
def send_input():
    data = request.get_json()
    session_id = data.get("session_id")
    file_name = data.get("fileName")
    user_input = data.get("input", "") + "\n"

    process_key = f"{session_id}_{file_name}"
    proc = active_processes.get(process_key)

    if proc:
        try:
            proc.stdin.write(user_input)
            proc.stdin.flush()
            return jsonify({"message": "Input sent."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "No active process."}), 404

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
