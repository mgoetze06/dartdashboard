import cv2
from flask import Flask, render_template, Response
import time, datetime
import os

camera = cv2.VideoCapture("/dev/video14")
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
                #print("camera not available")
                path = os.path.join(os.getcwd(),"noconnection.jpg")
                #print(path)
                frame = cv2.imread(path)
                #frame = cv2.GaussianBlur(frame,(25,25),3)
                frame = cv2.blur(frame, (100, 100))
                cv2.putText(frame,"Keine Verbindung zur Kamera!",(100,200),cv2.FONT_HERSHEY_PLAIN,15,(0,0,0),3)
                localtime = datetime.datetime.now()
                cv2.putText(frame,str(localtime),(100,450),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),3)




            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
            if success:
                time.sleep(0.04)
            else:
                time.sleep(5)
        except:
            print("broke: camera not available")
            time.sleep(2)

@app.route('/video_feed_1')
def video_feed_1():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('fullscreen1.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8100)
    #app.run(debug=False)
