import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
fgbg = cv.createBackgroundSubtractorMOG2()
prevFrame = None
currFrame = None

# steps outlined in https://arxiv.org/pdf/1907.05281.pdf

def start():
    print("beginning program")
    # backgroundSegmentation()
    # featureExtraction('test/test01.jpg')
    # filterKeypoints()
    # manual()

    # Supposed to bring up a video feed of camera, but not working on my computer
    
    ret, frame = cap.read()
    prevFrame = frame
    currFrame = frame

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        fgmask = backgroundSegmentation(frame)
        prevFrame = currFrame
        currFrame = fgmask
        # img, kp, des = featureExtraction(currFrame)
       
        cv.imshow('frame1',  filterKeypoints(prevFrame, currFrame))
        if (cv.waitKey(1) & 0xFF) == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def backgroundSegmentation(frame):
    print("Step 1: find silhouette of foreground")
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html
    # https://www.pyimagesearch.com/2020/07/27/opencv-grabcut-foreground-segmentation-and-extraction/ -> has explanations
    fgmask = fgbg.apply(frame)
    # cv.imwrite(name,fgmask)
    return fgmask

def featureExtraction(frame): # should take in an image (or N x N x 3 matrix that represents an image)
    print("Step 2: find features of image")
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_surf_intro/py_surf_intro.html -> not sure this works with a venv
    # https://docs.opencv.org/master/da/df5/tutorial_py_sift_intro.html

    # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    sift = cv.SIFT_create()
    kp, des = sift.detectAndCompute(frame,None)
    img = cv.drawKeypoints(frame, kp, outImage = None, color=(255,0,0))
    cv.drawKeypoints(frame, kp, img)
    return img, kp, des

'''
def featureExtractionForImgPath(imgPath):
    print("Step 2: find features of image")
    img = cv.imread(imgPath)
    gray= cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    sift = cv.SIFT_create()
    kp, des = sift.detectAndCompute(gray,None)
    img=cv.drawKeypoints(gray,kp,img)
    cv.imwrite(imgPath[0:-4] + "_KEYPOINTS.jpg",img)
    return img, kp, des
'''

def filterKeypoints(prevFrame, currFrame):
    print("Step 3: filter features within silhouette")
    frame1, frame1_kp, frame1_des = featureExtraction(prevFrame)
    frame2, frame2_kp, frame2_des = featureExtraction(currFrame)
    if len(frame2_kp)==0:
        frame2 = frame1
        frame2_des = frame1_des
        frame2_kp = frame1_kp
    #-- Step 2: Matching descriptor vectors with a FLANN based matcher
    # Since SURF is a floating-point descriptor NORM_L2 is used
    matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
    knn_matches = matcher.knnMatch(frame1_des, frame2_des, 2)
    #-- Filter matches using the Lowe's ratio test
    ratio_thresh = 0.75
    good_matches = []
    for m,n in knn_matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)
    #-- Draw matches
    img_matches = np.empty((max(frame1.shape[0], frame2.shape[0]), frame1.shape[1]+frame2.shape[1], 3), dtype=np.uint8)
    cv.drawMatches(frame1, frame1_kp, frame2, frame2_kp, good_matches, img_matches, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # cv.imwrite("MATCHES.jpg", img_matches)
    return img_matches



def manual():
    print("Step 4: ?")
    img = cv.imread('test/test05.png')
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    face_cascade = cv.CascadeClassifier('xml/haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        img = cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        # cv.imwrite("FACES.jpg", roi_color)
    

def matchKeypointsFrameToFrame():
    print("Step 5: match keypoints")
    # https://docs.opencv.org/3.4/d5/d6f/tutorial_feature_flann_matcher.html

if __name__ == "__main__":
    start()