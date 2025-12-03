import sys
import os
import socket
import qrcode
import uuid
import re
from flask import Flask, render_template, request, jsonify
import whisper
import torch
from pydub import AudioSegment

# Configuration for FFmpeg
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.pathsep + PROJECT_DIR
FFMPEG_FILE = os.path.join(PROJECT_DIR, "ffmpeg.exe")
FFPROBE_FILE = os.path.join(PROJECT_DIR, "ffprobe.exe")

AudioSegment.converter = FFMPEG_FILE
AudioSegment.ffprobe = FFPROBE_FILE

app = Flask(__name__)

# Directory setup
TEMP_DIR = 'temp_audio'
STATIC_DIR = 'static'

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Global State
transcription_history = []
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load Whisper Model
print(f"Loading Whisper Model on {DEVICE.upper()}...")
try:
    model = whisper.load_model("medium", device=DEVICE)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

SERVER_IP = get_local_ip()
PORT = 5000
BASE_URL = f"http://{SERVER_IP}:{PORT}"

# Generate QR Code
qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data(f"{BASE_URL}/izle")
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")
qr_path = os.path.join(STATIC_DIR, "qr_code.png")
qr_img.save(qr_path)

def clean_text(text):
    if not text:
        return ""
    
    forbidden_words = [
        "subtitle", "copyright", "caption", "subscribers", "amara.org", 
        "mbc", "video", "like", "comment", "share", "thank you", 
        "english", "russian", "transkripsiyon"
    ]
    
    lower_text = text.lower()
    
    for word in forbidden_words:
        if word in lower_text:
            return ""

    if len(text) < 3:
        return ""
        
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)

    return text.strip()

@app.route('/')
def admin_panel():
    return render_template('admin.html', qr_url=f"{BASE_URL}/izle")

@app.route('/izle')
def viewer_panel():
    return render_template('viewer.html')

@app.route('/cevir', methods=['POST'])
def process_audio():
    speaker_name = request.form.get('speaker', 'Unknown')

    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio data received'}), 400

    unique_filename = f"audio_{uuid.uuid4()}"
    raw_path = os.path.join(TEMP_DIR, f"{unique_filename}.wav")
    clean_path = os.path.join(TEMP_DIR, f"{unique_filename}_clean.wav")

    try:
        audio_file = request.files['audio_data']
        audio_file.save(raw_path)
        
        audio = AudioSegment.from_file(raw_path)
        
        # Audio preprocessing checks
        if len(audio) < 1000:
            return jsonify({'success': False, 'message': 'Audio too short'})

        if audio.dBFS < -45:
            return jsonify({'success': False, 'message': 'Silence detected'})
            
        audio.export(clean_path, format="wav")

        # Whisper Transcription
        options = {
            "task": "translate",
            "language": "tr", 
            "fp16": True if DEVICE == "cuda" else False,
            "temperature": 0.0,
            "no_speech_threshold": 0.6,
            "logprob_threshold": -0.8,
            "condition_on_previous_text": False,
            "initial_prompt": "Konuşma metni." 
        }
        
        result = model.transcribe(clean_path, **options)
        cleaned_text = clean_text(result["text"].strip())

        # Cleanup files
        try:
            os.remove(raw_path)
            os.remove(clean_path)
        except OSError:
            pass

        if not cleaned_text:
             return jsonify({'success': False, 'message': 'Filtered or empty text'})

        # Deduplication check
        if transcription_history and transcription_history[-1]['en'] == cleaned_text:
            return jsonify({'success': False, 'message': 'Duplicate text'})

        print(f"[{speaker_name}]: {cleaned_text}")

        data_point = {
            "speaker": speaker_name,
            "en": cleaned_text
        }
        transcription_history.append(data_point)
        
        return jsonify({'success': True, 'data': data_point})

    except Exception as e:
        print(f"Processing Error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_updates')
def get_updates():
    return jsonify(transcription_history)

@app.route('/ozetle', methods=['POST'])
def summarize():
    full_text = " ".join([f"{item['speaker']}: {item['en']}" for item in transcription_history])
    if not full_text:
        return jsonify({'summary': "No content available."})
    
    word_count = len(full_text.split())
    summary = f"SESSION REPORT\nTotal Words: {word_count}\n\nRecent Transcript:\n{full_text[-1000:]}..."
    return jsonify({'summary': summary})

if __name__ == '__main__':
    print(f"Server running on {BASE_URL}")
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=PORT)