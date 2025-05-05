import shutil
import sys
from flask import Flask, request, send_file
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "experiments"
TEXTURE_FILE = "0_texture_uv_400.jpg"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Flask server is up!"

@app.route("/generate_texture", methods=["POST"])
def generate_texture():
    
    # Expecting two image files and a garment type ID
    front = request.files.get("front")
    back = request.files.get("back")
    garment_id = request.form.get("garment", "11_skirt") #always skirt for now
    print("📥 Received POST at /generate_texture")
    print("📥 Front image:", front)
    print("📥 Back image:", back)

    if not front or not back:
      return "Missing front/back image", 400

    # # Create session information
    session_id = datetime.now().strftime("%m%d_%H%M%S")
    input_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(input_dir, exist_ok=True)
    scale = "1.0" 
    steps_one = "51"
    steps_two = "401"

    # Save a copy of raw files to disk
    front_path = os.path.join(input_dir, "front.jpg")
    back_path = os.path.join(input_dir, "back.jpg")
    front.save(front_path)
    back.save(back_path)

    #Copy to cloth2tex's input directory
    cloth_input_dir = os.path.join("imgs", garment_id, session_id)
    os.makedirs(cloth_input_dir, exist_ok=True)
    shutil.copy(front_path, os.path.join(cloth_input_dir, "front.jpg"))
    shutil.copy(back_path, os.path.join(cloth_input_dir, "back.jpg"))

    # Run inference to generate texture
    # step1: how detailed the shape is
    # step2: how detailed the texture is
    command = [
        sys.executable, "phase1_inference.py",
        "--g", garment_id,
        "--s", scale,
        "--d", session_id,
        "--steps_one", steps_one,
        "--steps_two", steps_two
    ]
    subprocess.Popen(command, stdout=None, stderr=None) #run non-blocking command

    # Uncomment to test with existing texture file
    # mock_result(session_id)

    # Send back session ID immediately
    print(f"📂 Session created: {session_id}")
    return {"status": "started", "session": session_id}, 202

@app.route("/generate_texture_demo", methods=["POST", "GET"])
def generate_texture_demo():
    print("🧪 Running demo texture generation")

    # Hardcoded paths for demo images
    garment_id = "11_skirt"
    demo_front = os.path.join("imgs", "demo", "front.jpg")
    demo_back = os.path.join("imgs", "demo", "back.jpg")

    if not os.path.exists(demo_front) or not os.path.exists(demo_back):
        return "❌ Demo images not found", 404

    # Create session info
    session_id = datetime.now().strftime("demo_%m%d_%H%M%S")
    input_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(input_dir, exist_ok=True)
    scale = "1.0"
    steps_one = "51"
    steps_two = "401"

    # Copy demo images into input and cloth2tex folders
    front_path = os.path.join(input_dir, "front.jpg")
    back_path = os.path.join(input_dir, "back.jpg")
    shutil.copy(demo_front, front_path)
    shutil.copy(demo_back, back_path)

    cloth_input_dir = os.path.join("imgs", garment_id, session_id)
    os.makedirs(cloth_input_dir, exist_ok=True)
    shutil.copy(front_path, os.path.join(cloth_input_dir, "front.jpg"))
    shutil.copy(back_path, os.path.join(cloth_input_dir, "back.jpg"))

    # Kick off inference
    command = [
        sys.executable, "phase1_inference.py",
        "--g", garment_id,
        "--s", scale,
        "--d", session_id,
        "--steps_one", steps_one,
        "--steps_two", steps_two
    ]
    subprocess.Popen(command, stdout=None, stderr=None)

    print(f"🧪 Demo session created: {session_id}")
    return {"status": "started", "session": session_id}, 202

@app.route("/status/<session_id>")
def check_status(session_id):
    result_path = os.path.join(RESULTS_FOLDER, session_id, TEXTURE_FILE)
    is_ready = os.path.exists(result_path)
    print(f"⌛ {is_ready}")
    return {"ready": is_ready}, 200

@app.route("/result/<session_id>")
def download_result(session_id):
    print(f"📩 Requested: {session_id}")
    texture_path = os.path.join(RESULTS_FOLDER, session_id, TEXTURE_FILE)
    print(f"✅ Found texture path: {texture_path}")
    if not os.path.exists(texture_path):
        return "Texture not ready", 404
    return send_file(texture_path, mimetype="image/jpeg", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

def mock_result(session_id: str):
    src_path = "/home/eatmelons/Cloth2Tex/experiments/0413_183710/0_texture_uv_400.jpg"
    dst_dir = os.path.join(RESULTS_FOLDER, session_id)
    dst_path = os.path.join(dst_dir, TEXTURE_FILE)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy(src_path, dst_path)
    print(f"📄 Mock result copied to: {dst_path}")