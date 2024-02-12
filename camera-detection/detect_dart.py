from skimage.morphology import opening,diamond,thin
import imutils
import cv2, os
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
from skimage.filters import threshold_triangle
from skimage import exposure

debug = True
points = []
img_global = None
#%matplotlib inline

def show_images(images, titles=None):
    fig, ax = plt.subplots(ncols=len(images), figsize=(len(images)*5,5))

    for idx, image in enumerate(images):
        ax[idx].imshow(image, cmap='gray')
        ax[idx].axis(False)
        if(titles != None):
            ax[idx].set_title(titles[idx])
    return

def executeTransformation(img,matrix):

    result = cv2.warpPerspective(img, matrix, (1080, 1080))
    flipped = cv2.flip(result, 1)
    #result_hist = cv2.equalizeHist(flipped)

    return flipped


def click_event_transformation(event, x, y, flags, params): 
    global img_global
    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
  
        # displaying the coordinates 
        # on the Shell 
        if len(points) < 4:
            points.append([x,y])
            print(x, ' ', y)
        else:
            print("already done")

        # displaying the coordinates 
        # on the image window 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        #cv2.putText(image, str(x) + ',' +str(y), (x,y), font, 1, (255, 0, 0), 2) 
        cv2.circle(img_global,(x,y),5,(255, 0, 0))
        cv2.imshow('Click Points for Image Transformation', img_global) 



def setupTransformation(image):
    global img_global
    pts2 = np.float32([[540, 0], [0, 540],[540, 1080],[1080, 540]])
    if os.path.exists("setup_points.csv"):
        pts1 = genfromtxt("setup_points.csv", delimiter=',',dtype=np.float32)  
    else:
        img_global = np.copy(image)
        cv2.imshow('Click Points for Image Transformation',img_global)
        cv2.setMouseCallback('Click Points for Image Transformation', click_event_transformation) 
        cv2.waitKey(0) 
        cv2.destroyAllWindows() 
        pts1 = np.float32(points)
        #print(pts1)




    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    np.savetxt("setup_points.csv", pts1, delimiter=",")
    return matrix
    


def createSegments(img):
    segments = []

    return segments




def detectDart(background=None,img_new_dart=None):
    if background is None:
        background = cv2.imread("C:\projects\DartDashboard\camera-detection\images\\test1.jpg")
    if img_new_dart is None:
        img_new_dart = cv2.imread("C:\projects\DartDashboard\camera-detection\images\\test12.jpg")
    img_diff = cv2.absdiff(background, img_new_dart)
    if img_diff.shape[1] > 1080:
        img_diff = imutils.resize(img_diff, width=1080)

    if debug:
        print(np.mean(img_diff))
        print(img_diff.dtype)
        cv2.imshow("image of differences (img_diff)",img_diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    gray = cv2.cvtColor(img_diff, cv2.COLOR_BGR2GRAY)
    thresh = threshold_triangle(gray)
    img_bin = gray > thresh


    image_opened = opening(opening(img_bin),footprint=diamond(2))


    if debug:
        cv2.imshow("img after morphology",exposure.rescale_intensity(image_opened, out_range='uint8'))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return exposure.rescale_intensity(image_opened, out_range='uint8')

def computeDartToPosition(image_opened):
    ocv = thin(image_opened)
    dst = cv2.cornerHarris(exposure.rescale_intensity(ocv, out_range='uint8'),2,3,0.04)
    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst,None)
    # Threshold for an optimal value, it may vary depending on the image.
    #image_opened[dst>0.01*dst.max()]=[0,0,255]
    image_opened[dst>0.01*dst.max()]=255
    if debug:
        cv2.imshow("img corner Harris detection",exposure.rescale_intensity(image_opened, out_range='uint8'))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

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
    if debug:
        cv2.putText(image_opened,"Schwerpunkt",(avg_x,avg_y-50),1,1,(255,0,0))
        cv2.putText(image_opened,"Spitze",(round(max_x),round(max_y)-20),1,1,(255,0,0))
        cv2.imshow("img circle distance",exposure.rescale_intensity(image_opened, out_range='uint8'))
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    return (round(max_x),round(max_y))

if __name__ == "__main__":

    img = cv2.imread("C:\projects\DartDashboard\camera-detection\images\\test1.jpg")
    if img.shape[1] > 1080:
        img = imutils.resize(img, width=1080)
    matrix = setupTransformation(img)
    background = np.copy(img)
    background_trans = executeTransformation(img,matrix)

    cv2.imshow("Background",background_trans)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    newDartimg = cv2.imread("C:\projects\DartDashboard\camera-detection\images\\test.JPG")
    if newDartimg.shape[1] > 1080:
        newDartimg = imutils.resize(newDartimg, width=1080)
    dart = detectDart(background=background,img_new_dart=newDartimg)
    if debug:
        cv2.imshow("dart",dart)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    newDartimg_trans = executeTransformation(dart,matrix)
    if debug:
        cv2.imshow("newDartimg",newDartimg_trans)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(newDartimg_trans.dtype)
    dart_center = computeDartToPosition(newDartimg_trans)


    newDartimg = executeTransformation(newDartimg,matrix)
    cv2.circle(newDartimg,(dart_center[0],dart_center[1]),50,(255,255,255),2)
    cv2.circle(newDartimg,(dart_center[0],dart_center[1]),15,(153,153,0),4)
    cv2.circle(newDartimg,(dart_center[0],dart_center[1]),3,(255,0,0),3)
    cv2.imshow("dart",newDartimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("dart_detection_20240111.jpg",newDartimg)



    