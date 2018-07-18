#Condition: It checks 20 consecutive frames and if the Eye Aspect ratio is less
#than 0.3, Alert is generated.

import cv2
import numpy as np
from scipy.spatial import distance
import dlib

def eyeaspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    a=distance.euclidean(eye[1],eye[5])
    b=distance.euclidean(eye[2],eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    c=distance.euclidean(eye[0],eye[3])
    
    # compute the eye aspect ratio
    EAR=(a+b)/(2.0*c)
    
    #return the eye aspect ratio
    return EAR

def shape_to_array(shape,dtype="int"):
    #initialize list of (x,y) coordinates
    coordinates=np.zeros((68,2),dtype=dtype)

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0,68):
        coordinates[i]=(shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coordinates


# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold

EYE_THRESH=0.3
FRAMES_CHECK=20

#initialize the frame counters and total number of blinks
COUNTER=0
#TOTAL_BLINK=0
'''
If the eye aspect ratio falls below a certain threshold and then rises above the threshold, then
we’ll register a “blink” — the EYE_THRESH  is this threshold value. We default it to a value
of 0.3  as this is what has worked best for my applications, but you may need to tune it for your
own application.
COUNTER  is the total number of successive frames that have
an eye aspect ratio less than EYE_THRESH.  
'''

PREDICTOR_PATH="shape_predictor_68_face_landmarks.dat"

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
predictor=dlib.shape_predictor(PREDICTOR_PATH)
detector=dlib.get_frontal_face_detector()

JAWLINE_POINTS = list(range(0, 17))  
RIGHT_EYEBROW_POINTS = list(range(17, 22))  
LEFT_EYEBROW_POINTS = list(range(22, 27))  
NOSE_POINTS = list(range(27, 36))  
RIGHT_EYE_POINTS = list(range(36, 42))  
LEFT_EYE_POINTS = list(range(42, 48))  
MOUTH_OUTLINE_POINTS = list(range(48, 61))  
MOUTH_INNER_POINTS = list(range(61, 68))

#Starting the webcam
cap=cv2.VideoCapture(0)

#loop over frames from the webcam
while 1:
    #capture frame by frame
    ret,frame=cap.read()
    
    #Changing the frame in grayscale
    grayscale=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    #detect faces in the grayscale frame
    rects=detector(grayscale,0)

    #loop over the face detections
    for rect in rects:
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape=predictor(grayscale,rect)
        shape=shape_to_array(shape)
	# extract the left and right eye coordinates, then use the
	# coordinates to compute the eye aspect ratio for both eyes
        left_eye=shape[LEFT_EYE_POINTS]
        right_eye=shape[RIGHT_EYE_POINTS]
        left_ear=eyeaspect_ratio(left_eye)
        right_ear=eyeaspect_ratio(right_eye)
        # average the eye aspect ratio together for both eyes
        ear=(left_ear+right_ear)/2.0
        # compute the convex hull for the left and right eye, then # visualize each of the eyes
        leftEyeHull=cv2.convexHull(left_eye)
        rightEyeHull=cv2.convexHull(right_eye)
        cv2.drawContours(frame,[leftEyeHull],-1,(0,255,0),1)
        cv2.drawContours(frame,[rightEyeHull],-1,(0,255,0),1)

        # check to see if the eye aspect ratio is below the blink
	# threshold, and if so, increment the blink frame counter

        if ear<EYE_THRESH:
            COUNTER+=1
            print(COUNTER)
            if COUNTER>FRAMES_CHECK:
                cv2.putText(frame,"Drowsiness Detected",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
                cv2.putText(frame,"Drowsiness Detected",(10,325),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
        else:
            #reset the eye counter
            COUNTER=0
        cv2.putText(frame,"EAR:{:.2f}".format(ear),(300,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)


    #show the frame
    cv2.imshow("Frame",frame)
    k=cv2.waitKey(1)& 0xFF

    #if the 'q' key was pressed, break the loop
    if k==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
