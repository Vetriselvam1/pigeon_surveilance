import os
import time
import threading
import serial
from flask import Flask, render_template, Response, jsonify
import cv2
from picamera2 import Picamera2
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

# Setup directories for captured images and videos
captured_images_dir = os.path.join('static', 'captured_images')
captured_videos_dir = os.path.join('static', 'captured_videos')
os.makedirs(captured_images_dir, exist_ok=True)
os.makedirs(captured_videos_dir, exist_ok=True)

# Initialize the PiCamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration())
picam2.start()

# Initialize the serial connection to Arduino (adjust the port accordingly)
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Change port to your Arduino's port
time.sleep(2)  # Wait for the serial connection to establish

# Function to generate frames from the camera
def generate_frames():
    while True:
        frame = picam2.capture_array()  # Capture the frame as a numpy array
        _, encoded_frame = cv2.imencode('.jpg', frame)  # Encode as JPEG
        frame_bytes = encoded_frame.tobytes()

        # Yield the frame as byte data in the required format for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.1)  # Adjust this for frame rate


# Route to capture and save an image
@app.route('/capture_image')
def capture_image():
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    image_filename = f'{timestamp}.jpg'
    image_path = os.path.join(captured_images_dir, image_filename)

    # Capture the image and save it to the static folder
    frame = picam2.capture_array()
    cv2.imwrite(image_path, frame)

    return jsonify({"status": "success", "message": "Image captured", "filename": image_filename})

# Route to toggle video recording
is_recording = False
video_stream = None

def record_video():
    global video_stream
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    video_filename = f'{timestamp}.mp4'
    video_path = os.path.join(captured_videos_dir, video_filename)
    
    # Use H264 codec for better compatibility
    fourcc = cv2.VideoWriter_fourcc(*'H264')  # Or try 'MJPG' if H264 doesn't work

    # Capture first frame to get the resolution
    frame = picam2.capture_array()
    height, width, _ = frame.shape

    # Initialize VideoWriter with the frame's resolution
    video_stream = cv2.VideoWriter(video_path, fourcc, 30.0, (width, height))

    start_time = time.time()
    while is_recording and (time.time() - start_time < 600):  # Record for up to 10 minutes
        frame = picam2.capture_array()
        video_stream.write(frame)
        time.sleep(0.05)  # Shorter sleep for better responsiveness

    video_stream.release()

# Route to stream video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Home route for testing

@app.route('/toggle_recording')
def toggle_recording():
    global is_recording
    if is_recording:
        # Stop recording
        is_recording = False
        return jsonify({"status": "recording_stopped"})
    else:
        # Start recording in a background thread
        is_recording = True
        threading.Thread(target=record_video, daemon=True).start()
        return jsonify({"status": "recording_started"})

# Route to show captured media
@app.route('/show_media')
def show_media():
    images = os.listdir(captured_images_dir)
    videos = os.listdir(captured_videos_dir)
    images = [image for image in images if image.endswith(".jpg")]
    videos = [video for video in videos if video.endswith(".mp4")]
    return render_template('show_media.html', images=images, videos=videos)

# Route to handle Arduino communication
@app.route('/start', methods=['POST'])
def start():
    # Send 'f' to Arduino to start servo loop
    arduino.write(b'f')
    return 'Started'

@app.route('/wings', methods=['POST'])
def wings():
    # Send 'w' to Arduino to control the wings
    arduino.write(b'w')
    return 'Wings controlled'

@app.route('/righthead', methods=['POST'])
def righthead():
    # Send 'r' to Arduino to move the head to the right
    arduino.write(b'r')
    return 'Head turned to the right'

@app.route('/lefthead', methods=['POST'])
def lefthead():
    # Send 'l' to Arduino to move the head to the left
    arduino.write(b'l')
    return 'Head turned to the left'

@app.route('/stop', methods=['POST'])
def stop():
    # Send 's' to Arduino to stop and set servos to 90 degrees
    arduino.write(b's')
    return 'Stopped'

# Home route for testing
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    try:
        # Ensure the app runs on the local network
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port, threaded=True)
    finally:
        # Release the camera when the app stops
        picam2.stop()
        arduino.close()  # Close the Arduino serial connection
