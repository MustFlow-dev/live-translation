# IEEE FBU Real-Time AI Translator

This project is an advanced, real-time speech-to-text and translation system developed for IEEE FBU events. It leverages OpenAI's Whisper model for high-accuracy translation and NVIDIA CUDA acceleration for low-latency performance.

## System Architecture

The application consists of a Flask backend and a modern web frontend.
* **Backend:** Python (Flask) handles audio processing, FFmpeg conversion, and Whisper AI inference.
* **Frontend:** HTML5/JS interfaces for the Admin Panel (Mixing Console) and Audience View.
* **AI Core:** OpenAI Whisper (Medium Model) for translation + Transformers (BART) for session reporting.

## Features

* **Real-Time Translation:** Converts Turkish speech to English text instantly with high accuracy.
* **Multi-Microphone Support:** Admin panel allows managing multiple input sources (microphones) simultaneously.
* **GPU Acceleration:** Optimized for NVIDIA RTX 4070 (and other RTX series) using CUDA.
* **Audience Live Stream:** Attendees can view translations in real-time on their mobile devices via QR Code.
* **Smart Filtering:** Custom algorithms to prevent AI hallucinations and silence-induced errors.
* **Session Reporting:** Generates an AI-powered summary of the entire session.

## Prerequisites

To run this project, ensure you have the following installed:

* **Python 3.11** (Recommended for stability)
* **NVIDIA Drivers & CUDA Toolkit** (For GPU acceleration)
* **FFmpeg:** `ffmpeg.exe` and `ffprobe.exe` must be placed in the project root directory.

## Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/ieee-fbu-translator.git](https://github.com/aJaxxd-code/ieee-fbu-translator.git)
    cd ieee-fbu-translator
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup FFmpeg**
    Download FFmpeg builds and place `ffmpeg.exe` and `ffprobe.exe` next to `app.py`.

## Usage

1.  **Start the Server**
    Run the application using Python:
    ```bash
    python app.py
    ```

2.  **Access Admin Panel**
    Open your browser and navigate to `http://localhost:5000`.

3.  **Connect Audience**
    Project the QR Code displayed on the Admin Panel to the screen.

4.  **Start Translating**
    * Click "+" to add a microphone channel.
    * Select the input device and speaker name.
    * Click "START RECORDING".

## Troubleshooting

* **"Model Loading" takes too long:** The first run downloads the Whisper model (approx. 1.5GB). Subsequent runs will be instant.
* **Silence/Hallucinations:** The system includes a DBFS filter. Ensure the microphone input level is sufficient.

## License

This project is open-source and available under the MIT License.