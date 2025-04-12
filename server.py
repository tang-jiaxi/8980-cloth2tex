import shutil
import sys
from flask import Flask, request, send_file
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "experiments"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/generate_texture", methods=["POST"])
def generate_texture():
    
    # Expecting two image files and a garment type ID
    front = request.files.get("front")
    back = request.files.get("back")
    garment_id = request.form.get("garment", "11_skirt") #always skirt for now

    if not front or not back:
      return "Missing front/back image", 400

    # Create session information
    session_name = datetime.now().strftime("%m%d_%H%M%S")
    input_dir = os.path.join(UPLOAD_FOLDER, session_name)
    os.makedirs(input_dir, exist_ok=True)
    scale = "1.0" 

    # Save a copy of raw files to disk
    front_path = os.path.join(input_dir, "front.jpg")
    back_path = os.path.join(input_dir, "back.jpg")
    front.save(front_path)
    back.save(back_path)

    #Copy to cloth2tex's input directory
    cloth_input_dir = os.path.join("imgs", garment_id, session_name)
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
        "--d", session_name,
        "--steps_one", "1",
        "--steps_two", "1"
    ]
    subprocess.run(command)

    # Send back texture file
    texture_path = os.path.join(RESULTS_FOLDER, session_name, "x_texture_uv_1000.jpg")
    if not os.path.exists(texture_path):
        return "Texture generation failed", 500
    return send_file(texture_path, mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
