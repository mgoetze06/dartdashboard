import cv2
from flask import Flask, render_template, Response
import time, datetime
import os
import subprocess
import gphoto2 as gp
import imutils
import io
import numpy as np

#camera = cv2.VideoCapture("/dev/video14")
#camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#print("Frame default resolution: (" + str(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "; " + str(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) + ")")
#camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)#(7680, 4320
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#1920#
#1080

#1280.0
#720.0

#print("Frame resolution set to: (" + str(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "; ")
app = Flask(__name__)



subprocess.run(["pkill", "-f", "gphoto2"])


#locale.setlocale(locale.LC_ALL, '')
#logging.basicConfig(
#    format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
callback_obj = gp.check_result(gp.use_python_logging())
camera = gp.check_result(gp.gp_camera_new())
gp.check_result(gp.gp_camera_init(camera))
# required configuration will depend on camera type!
print('Checking camera config')
# get configuration tree
config = gp.check_result(gp.gp_camera_get_config(camera))
# find the image format config item
# camera dependent - 'imageformat' is 'imagequality' on some
OK, image_format = gp.gp_widget_get_child_by_name(config, 'imageformat')
if OK >= gp.GP_OK:
    # get current setting
    value = gp.check_result(gp.gp_widget_get_value(image_format))
    # make sure it's not raw
    if 'raw' in value.lower():
        print('Cannot preview raw images')
        exit
# find the capture size class config item
# need to set this on my Canon 350d to get preview to work at all
OK, capture_size_class = gp.gp_widget_get_child_by_name(
    config, 'capturesizeclass')
if OK >= gp.GP_OK:
    # set value
    value = gp.check_result(gp.gp_widget_get_choice(capture_size_class, 2))
    gp.check_result(gp.gp_widget_set_value(capture_size_class, value))
    # set config
    gp.check_result(gp.gp_camera_set_config(camera, config))
# capture preview image (not saved to camera memory card)
print('Capturing preview image')

def gen_frames():
    while True:
        try:
            #success, frame = camera.read()  # read the camera frame
            a = datetime.datetime.now()
            camera_file = gp.check_result(gp.gp_camera_capture_preview(camera))
            file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            # display image
            data = memoryview(file_data)
            #print(type(data), len(data))
            #print(data[:10].tolist())
            image_io = io.BytesIO(file_data)
            #image = Image.open(image_io)
            #image.show()
            #print(image.size)
            #print(image_io)
            image_io.seek(0)
            #org_img = cv2.imdecode(np.frombuffer(image_io.read(), np.uint8), 1)
            #scr_w,scr_h = 1920,1080
            #if org_img.shape[1] > 1920:
            #    org_img = imutils.resize(org_img, width=1920)

            #if not success:
            #    #print("camera not available")
            #    path = os.path.join(os.getcwd(),"noconnection.jpg")
            #    #print(path)
            #    frame = cv2.imread(path)
            #    #frame = cv2.GaussianBlur(frame,(25,25),3)
            #    frame = cv2.blur(frame, (100, 100))
            #    cv2.putText(frame,"Keine Verbindung zur Kamera!",(100,200),cv2.FONT_HERSHEY_PLAIN,15,(0,0,0),3)
            #    localtime = datetime.datetime.now()
            #    cv2.putText(frame,str(localtime),(100,450),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),3)




            #ret, buffer = cv2.imencode('.jpg', org_img)
            #frame = buffer.tobytes()
            frame = image_io.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
            #if success:
            #    time.sleep(0.04)
            #else:
            #    time.sleep(5)
        except:
            print("broke: camera not available")
            #time.sleep(2)

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
