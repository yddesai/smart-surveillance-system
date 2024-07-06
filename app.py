from flask import Flask, render_template, Response
import cv2
import numpy as np
import time
from datetime import datetime
import RPi.GPIO as GPIO
import notify
app = Flask(__name__)

# Ultrasonic sensor configuration
TRIG_PIN = 23
ECHO_PIN = 24
SPEED_OF_SOUND = 34300
LOWER_THRESHOLD = 10
UPPER_THRESHOLD = 100

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Initialize the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(0.1)  # Allow the camera to warm up

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def get_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.002)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * SPEED_OF_SOUND) / 2
    return distance

def detect_motion():
    previous_distance = get_distance()
    current_distance = get_distance()
    change = abs(current_distance - previous_distance)
    if LOWER_THRESHOLD <= change <= UPPER_THRESHOLD:
        print("Motion detected!")
        return True
    return False

def detect_people(frame):
    boxes, weights = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
    # Adjust bounding boxes
    adjusted_boxes = []
    for (x, y, w, h) in boxes:
        x_adjust = int(w * 0.1)
        y_adjust = int(h * 0.1)
        x1, y1 = max(0, x - x_adjust), max(0, y - y_adjust)
        x2, y2 = min(frame.shape[1], x + w + x_adjust), min(frame.shape[0], y + h + y_adjust)
        adjusted_boxes.append((x1, y1, x2, y2))
    return np.array(adjusted_boxes)

def draw_boxes(frame, boxes):
    for (xA, yA, xB, yB) in boxes:
        cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
    return frame

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        if detect_motion():
            boxes = detect_people(frame)
            if len(boxes) > 0:
                frame = draw_boxes(frame, boxes)
                cv2.imwrite(f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg', frame)  
                print("Intruder detected and image saved.")
                notify.send_notification("Intruder detected and image saved.")


        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_cam_frames(camera):
    while True:
        if camera.stopped:
            break
        frame = camera.read()
        if detect_motion():
            boxes = detect_people(frame)
            if len(boxes) > 0:
                frame = draw_boxes(frame, boxes)
                cv2.imwrite(f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg', frame)
                print("Intruder detected and image saved.")
                #send_notification("Intruder detected and image saved.")  # Uncomment if 
        ret, jpeg = cv2.imencode('.jpg',frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            print("frame is none")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
