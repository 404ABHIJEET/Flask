import vosk
import pyaudio
import json
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Initialize the Flask app and SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*",}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Load the Vosk model for speech recognition
model = vosk.Model("./model1")
recognizer = vosk.KaldiRecognizer(model, 16000)

# Initialize PyAudio for microphone input
mic = pyaudio.PyAudio()
stream = mic.open(rate=16000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=16384)
stream.start_stream()

# Event handler for starting recognition
@socketio.on('start_recognition')
def handle_start_recognition():
    print("Recognition started")
    try:
        while True:
            data = stream.read(16384)
            if recognizer.AcceptWaveform(data):
                # If the recognizer accepts a frame, emit the result
                result = recognizer.Result()
                print(result)  # Print result for debugging
                emit('speech_status', {'started': True})
                emit('speech_result', {'result': json.loads(result)})  
    except Exception as e:
        print(f"Error during recognition: {e}")
        emit('speech_result', {'error': str(e)})

# Event handler to stop recognition
@socketio.on('stop_recognition')
def handle_stop_recognition():
    print("Recognition stopped")
    stream.stop_stream()
    stream.close()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

