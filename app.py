from flask import Flask, request, jsonify, render_template
import subprocess
import os
import time
import webbrowser
import threading

app = Flask(__name__)

FORTRAN_PATH = "C:/Users/abhin/OneDrive/Desktop/fortran"  # Path where your Fortran files are stored

@app.route("/compile", methods=["POST"])
def compile_and_run():
    code_text = request.json.get("codeText") or ''
    file_name = request.json.get("fileName")


    if not code_text:
        return jsonify({"error": "No Input."}), 400

    #os.chdir(FORTRAN_PATH)  # Change directory to the Fortran files location

    # Copy .txt to .f90
    #txt_file = f"{file_name}.txt"
    f90_file = f"{file_name}.f90"
    #if not os.path.exists(txt_file):
    #    return jsonify({"error": f"File '{txt_file}' not found."}), 404

    with open(f90_file, "w") as dest:
        dest.write(code_text)

    # Compile the Fortran code
    cmd ="gfortran {}.f90 -o {} ".format(file_name,file_name)
    compile_result = subprocess.run(["cmd.exe", "/c", cmd], capture_output=False, text=True)
    
    if compile_result.returncode != 0:
        return jsonify({"error": compile_result.stderr})
    
    # Run the executable
    run_cmd = [f"./{file_name}.exe"]
    run_result = subprocess.run(run_cmd, input='', capture_output=True, text=True)

    return jsonify({"output": run_result.stdout or "", "error": run_result.stderr or "No ouput"})
   

@app.route("/")
def home():
    # Serve the main HTML page
    return render_template('index.html')

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(debug=True)  # Run the Flask app with debugging enabled
