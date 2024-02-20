import cv2
from flask import Flask, render_template, Response
import time, datetime
import os
import subprocess
#import gphoto2 as gp
from skimage.morphology import thin
from skimage import exposure
import imutils
import io
import numpy as np
from flask import request

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


try:
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
except:
    print("gphoto nicht gefunden.")


backSub = cv2.createBackgroundSubtractorKNN(20)
max_frame_ignore_counter = 10
frame_ignore_counter = nonzero_frames = 0
dart_found = False
slider1 = 2000
slider2 = 7000

setupPoints = []

def computeDartToPosition(image_opened):
    ocv = thin(image_opened)
    dst = cv2.cornerHarris(exposure.rescale_intensity(ocv, out_range='uint8'),2,3,0.04)
    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst,None)
    # Threshold for an optimal value, it may vary depending on the image.
    #image_opened[dst>0.01*dst.max()]=[0,0,255]
    image_opened[dst>0.01*dst.max()]=255

    ret, dst = cv2.threshold(dst,0.1*dst.max(),255,0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(image_opened,np.float32(centroids),(5,5),(-1,-1),criteria)

    x = []
    y = []
    for i in range(1, len(corners)):
        #print(corners[i])
        x.append(corners[i][0])
        y.append(corners[i][1])

    avg_x = round(np.mean(x))
    avg_y = round(np.mean(y))

    print(avg_x)
    print(avg_y)

    cv2.circle(image_opened,(avg_x,avg_y),30,(255,0,0))

    max_x = 0
    max_y = 0
    dist = 0

    for x_ in x:
        for y_ in y:
            if np.sqrt((y_*y_)+(x_*x_))>dist:
                max_x = x_
                max_y = y_
        
    cv2.circle(image_opened,(round(max_x),round(max_y)),10,(0,255,0))

    return (round(max_x),round(max_y))

def gen_frames():
    global max_frame_ignore_counter,frame_ignore_counter,dart_found,nonzero_frames,slider2,slider1,setupPoints
    while True:
        try:

            #camerashutter 1/80 f4.5 canon dslr 1100d

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
            org_img = cv2.imdecode(np.frombuffer(image_io.read(), np.uint8), 1)
            #scr_w,scr_h = 1920,1080
            if org_img.shape[1] > 1080:
                org_img = imutils.resize(org_img, width=1080)
            fgMask = backSub.apply(org_img)
            if not dart_found:
                nonzero = np.count_nonzero(fgMask)
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
                if nonzero < 8000:
                    localtime = datetime.datetime.now()
                    cv2.putText(org_img,str(localtime),(10,20),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
                    cv2.putText(org_img,str(nonzero),(10,40),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
                    redImg = np.zeros(org_img.shape, org_img.dtype)
                    redImg[:,:] = (0, 0, 255)
                    redMask = cv2.bitwise_and(redImg, redImg, mask=fgMask)
                    cv2.addWeighted(redMask, 1, org_img, 1, 0, org_img)

                if nonzero > 1000 and nonzero < 7000:
                    nonzero_frames += 1
                    if nonzero_frames > 3:
                        
                        dart_center = computeDartToPosition(fgMask)
                        dart_found = True
                        nonzero_frames = 0

            if dart_found and frame_ignore_counter < max_frame_ignore_counter:
                frame_ignore_counter += 1
                cv2.circle(org_img,(dart_center[0],dart_center[1]),50,(255,255,255),2)
                cv2.circle(org_img,(dart_center[0],dart_center[1]),15,(153,153,0),4)
                cv2.circle(org_img,(dart_center[0],dart_center[1]),3,(255,0,0),3)
            else:
                frame_ignore_counter = 0
                dart_found = False


            ret, buffer = cv2.imencode('.jpg', org_img)
            frame = buffer.tobytes()
            #frame = image_io.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
            #if success:
            #    time.sleep(0.04)
            #else:
            #    time.sleep(5)
        except:
            #print("broke: camera not available")
            path = os.path.join(os.getcwd(),"camera-webserver-videostream","noconnection.jpg")
            #print(path)
            frame = cv2.imread(path)
            frame = cv2.GaussianBlur(frame,(25,25),3)
            frame = cv2.blur(frame, (100, 100))
            cv2.putText(frame,"Keine Verbindung zur Kamera!",(100,200),cv2.FONT_HERSHEY_PLAIN,5,(0,0,0),3)
            localtime = datetime.datetime.now()
            cv2.putText(frame,str(localtime),(100,300),cv2.FONT_HERSHEY_PLAIN,5,(0,0,0),3)
            cv2.putText(frame,str(slider1),(100,400),cv2.FONT_HERSHEY_PLAIN,5,(0,0,0),3)
            cv2.putText(frame,str(slider2),(100,500),cv2.FONT_HERSHEY_PLAIN,5,(0,0,0),3)
            for point in setupPoints:
                cv2.circle(frame,(point[0],point[1]),3,(255,0,0),10)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            #frame = image_io.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.5)

@app.route('/video_feed_1')
def video_feed_1():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('fullscreen1.html')

@app.route('/send/<data>')
def send_ir_command(data):
    global slider1,slider2
    print("Recieved: ", data)
    if "slider" in data:
        split = data.split("-")
        inputname = split[0]
        inputvalue = split[1]
        print(inputname,inputvalue)

        if inputname == "slider1":
            slider1 = inputvalue
        else:
            if inputname == "slider2":
                slider2 = inputvalue
    else:
        print("point recieved: ", data)

        split = data.split("-")
        x = split[0].split("x")[1]
        y = split[1].split("y")[1]  

        setupPoints.append((int(x),int(y)))

    return "{} - OK".format(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8100)
    #app.run(debug=False)
