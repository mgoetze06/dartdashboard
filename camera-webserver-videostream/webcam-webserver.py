import cv2
from flask import Flask, render_template, Response
import time

camera = cv2.VideoCapture(0)
#camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
print("Frame default resolution: (" + str(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "; " + str(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) + ")")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)#(7680, 4320
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#1920#
#1080

#1280.0
#720.0

print("Frame resolution set to: (" + str(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "; ")
app = Flask(__name__)

def gen_frames():
    while True:
        try:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            time.sleep(0.04)
        except:
            time.sleep(0.08)

@app.route('/video_feed_1')
def video_feed_1():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('fullscreen1.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
    #app.run(debug=False)