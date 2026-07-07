from flask import Flask, render_template, request, jsonify, send_file
from threading import Thread
import os
from engine import run_engine

app = Flask(__name__)

UPLOAD_FOLDER = "pdfs"
OUTPUT_FOLDER = "output"

# Engine writes here too, but app.py saves uploads before the engine
# thread starts, so the folder must exist up front or f.save() crashes
# on the very first request.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

progress_status = {
    "progress": 0,
    "status": "Idle",
    "done": False,
    "file": None,
    "profiles": [],
    "logs": []
}

# =========================
# BACKGROUND TASK
# =========================
def run_engine_async():
    global progress_status

    try:
        progress_status["progress"] = 10
        progress_status["status"] = "📄 Reading PDFs..."
        
        result = run_engine(callback=update_progress)

        progress_status["progress"] = 100
        progress_status["status"] = "✅ Completed"
        progress_status["done"] = True

        progress_status["file"] = result["output_file"]
        progress_status["profiles"] = result["profiles"]
        progress_status["logs"] = result["logs"]

    except Exception as e:
        progress_status["status"] = f"Error: {str(e)}"
        progress_status["done"] = True


# =========================
# PROGRESS CALLBACK
# =========================
def update_progress(percent, message):
    progress_status["progress"] = percent
    progress_status["status"] = message

    # store logs
    progress_status["logs"].append(f"{percent}% - {message}")


# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    global progress_status

    # Reset
    progress_status = {
        "progress": 0,
        "status": "Starting...",
        "done": False,
        "file": None,
        "profiles": [],
        "logs": []
    }

    # Save PDFs
    files = request.files.getlist("pdfs")
    for f in files:
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)

    # Start background thread
    thread = Thread(target=run_engine_async)
    thread.start()

    return jsonify({"status": "started"})


@app.route("/status")
def status():
    return jsonify(progress_status)


@app.route("/download")
def download():
    import os

    file_path = progress_status.get("file")

    if not file_path or not os.path.exists(file_path):
        return "File not ready or missing", 400

    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )


if __name__ == "__main__":
    app.run(debug=True)