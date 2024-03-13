import cv2
from flask import Flask, render_template, Response
import time, datetime
import os
import subprocess
import gphoto2 as gp
from skimage.morphology import thin
from skimage import exposure
import imutils
import io
import numpy as np
from flask import request
from numpy import genfromtxt
import json

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
    restartingGphoto = False
except:
    print("gphoto nicht gefunden.")


backSub = cv2.createBackgroundSubtractorKNN(32)
max_frame_ignore_counter = 12
frame_ignore_counter = nonzero_frames = 0
dart_found = False
slider1 = 700
slider2 = 6400
matrix = None
setupPoints = []
overlayParameters = noConnection = computeDart = False

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

    #cv2.circle(image_opened,(avg_x,avg_y),30,(255,0,0))

    max_x = 0
    max_y = 0
    dist = 0

    for x_ in x:
        for y_ in y:
            if np.sqrt((y_*y_)+(x_*x_))>dist:
                max_x = x_
                max_y = y_
        
    cv2.circle(image_opened,(round(max_x),round(max_y)),30,(255,255,255))
    filename = "dart_" + str(round(max_x)) + "_" + str(round(max_y)) + ".jpg"
    if os.path.exists(filename):
        filename = str(np.random.random(10)) + filename
    cv2.imwrite(filename,image_opened)
    return (round(max_x),round(max_y))

def setupTransformation(pts1):
    global setupPoints
    pts2 = np.float32([[540, 0], [0, 540],[540, 1080],[1080, 540]])

    #    img_global = np.copy(image)
    #    cv2.imshow('Click Points for Image Transformation',img_global)
    #    cv2.setMouseCallback('Click Points for Image Transformation', click_event_transformation) 
    #    cv2.waitKey(0) 
    #    cv2.destroyAllWindows() 
    #pts1 = np.float32(setupPoints)
        #print(pts1)
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    np.savetxt("setup_points.csv", pts1, delimiter=",")
    return matrix

def executeTransformation(img,matrix):

    result = cv2.warpPerspective(img, matrix, (1080, 1080))
    flipped = cv2.flip(result, 1)
    #result_hist = cv2.equalizeHist(flipped)

    return flipped

def gen_frames():
    global max_frame_ignore_counter,noConnection,frame_ignore_counter,dart_found,nonzero_frames,slider2,slider1,setupPoints,matrix,overlayParameters
    while True:
        if not restartingGphoto:
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
                #if org_img.shape[1] > 1080:
                #    org_img = imutils.resize(org_img, width=1080)
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
                    if nonzero < (slider2+1000):
                        localtime = datetime.datetime.now()
                        #cv2.putText(org_img,str(localtime),(10,20),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
                        #cv2.putText(org_img,str(nonzero),(10,40),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
                        redImg = np.zeros(org_img.shape, org_img.dtype)
                        redImg[:,:] = (0, 0, 255)
                        redMask = cv2.bitwise_and(redImg, redImg, mask=fgMask)
                        cv2.addWeighted(redMask, 1, org_img, 1, 0, org_img)
                    if computeDart:
                        if nonzero > slider1 and nonzero < slider2:
                            nonzero_frames += 1
                            if nonzero_frames > 5:
                                
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

            except:
                #print("broke: camera not available")
                path = os.path.join(os.getcwd(),"camera-webserver-videostream","dartscheibe_lowres.jpg")
                #print(path)
                org_img = cv2.imread(path)
                org_img = cv2.GaussianBlur(org_img,(25,25),3)
                org_img = cv2.blur(org_img, (100, 100))
                noConnection = True

            #org_img is a complete image
            if overlayParameters:
                for point in setupPoints:
                    cv2.circle(org_img,(point[0],point[1]),3,(255,0,0),10)
            if matrix is None:
                if len(setupPoints) == 4:
                    matrix = setupTransformation(np.float32(setupPoints))
                else:
                    if os.path.exists("setup_points.csv"):
                        pts1 = genfromtxt("setup_points.csv", delimiter=',',dtype=np.float32) 
                        matrix = setupTransformation(pts1)
                
            if matrix is not None:
                img_to_show = executeTransformation(org_img,matrix)


            else:
                img_to_show = org_img

            if noConnection:
                cv2.putText(img_to_show,"Keine Verbindung zur Kamera!",(10,30),cv2.FONT_HERSHEY_PLAIN,2,(0,0,0),3)
            if overlayParameters:
            
                cv2.putText(img_to_show,str(slider1),(10,110),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
                cv2.putText(img_to_show,str(slider2),(10,150),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1)
            localtime = datetime.datetime.now()


            cv2.putText(img_to_show,str(localtime),(10,int(img_to_show.shape[0]*0.98)),cv2.FONT_HERSHEY_PLAIN,int(img_to_show.shape[0]/450),(0,0,0),2)


            ret, buffer = cv2.imencode('.jpg', img_to_show)
            frame = buffer.tobytes()
            #frame = image_io.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #time.sleep(0.5)
        else:
            time.sleep(0.5)

@app.route('/video_feed')
def video_feed():
    global computeDart
    computeDart = request.args.get('computedart', default = False, type = bool)
    print("Compute Dart Argument from Client: ", computeDart)
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('fullscreen1.html')

@app.route('/reset')
def resetCamera():
    global camera,restartingGphoto
    #gp.check_result(gp.gp_camera_exit(camera))
    restartingGphoto = True
    subprocess.run(["pkill", "-f", "gphoto2"])

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/init')
def initCamera():
    global camera
    try:
        #subprocess.run(["pkill", "-f", "gphoto2"])
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
        restartingGphoto = False

    except:
        print("gphoto nicht gefunden.")#

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 



@app.route('/send/<data>')
def send_ir_command(data):
    global slider1,slider2,matrix,setupPoints,overlayParameters
    print("Recieved: ", data)
    if "slider" in data:
        split = data.split("-")
        inputname = split[0]
        inputvalue = split[1]
        print(inputname,inputvalue)

        if inputname == "slider1":
            slider1 = int(inputvalue)
        else:
            if inputname == "slider2":
                slider2 = int(inputvalue)
    else:
        if "x" in data and "y" in data:
            print("point recieved: ", data)

            split = data.split("-")
            x = split[0].split("x")[1]
            y = split[1].split("y")[1]  

            if len(setupPoints)<4:
                setupPoints.append((int(x),int(y)))
                print(setupPoints)
        else:
            if "setup" in data:
                if os.path.exists("setup_points.csv"):
                    os.remove("setup_points.csv")
                setupPoints.clear()
                matrix = None

            else:
                if "overlay" in data:
                    overlayParameters = not overlayParameters


    return "{} - OK".format(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8100)
    #app.run(debug=False)
