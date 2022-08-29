import cv2
import mediapipe as mp
import numpy as np
import autopy
import pyautogui as pug
import time 


# initializing the mediapipe library and creating Drawing and hands objects
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) 

# Defining the Global Constant 
width_cam, Height_cam = 640, 440
smoothening = 7
# finding the Width, Height of screen
width_scr, height_scr = autopy.screen.size()
frameR= 100
plocX, plocY = 0, 0
clocX, clocY = 0, 0
# definig the array of index of all finger tips
tipId = [4, 8, 12, 16, 20]

# Function to findposition of co-ordinates and depth of input frame
def findPosition(img):
    X_lst = []
    Y_lst = []
    land_mkslst = []
    if results.multi_hand_landmarks:
        for id, land_mks in enumerate(results.multi_hand_landmarks[0].landmark):
            height,width,depth = img.shape
            cx, cy = int(land_mks.x*width), int(land_mks.y*height)
            X_lst.append(cx)
            Y_lst.append(cy)
            land_mkslst.append([id, cx, cy])
            cv2.circle(img, (cx, cy), 5, (240, 22, 51), cv2.FILLED)
        xmin, xmax = min(X_lst), max(X_lst)
        ymin, ymax = min(Y_lst), max(Y_lst)
        bbox = xmin, ymin, xmax, ymax
        cv2.rectangle(img, (bbox[0],bbox[1]),
                              (bbox[2]+20, bbox[3]+20), (213, 235, 21), 2)
    return land_mkslst
    
# returns the length between two points in list of list of landmarks
def findDistance(pos1, pos2, land_mkslst):
    
    x1, y1 = land_mkslst[pos1][1], land_mkslst[pos1][2]
    x2, y2 = land_mkslst[pos2][1], land_mkslst[pos2][2]     
    length = pow(abs((pow((x2-x1),2)-pow((y2-y1),2))), 0.5)
    return length
    
    
# returns a list of 1's or 0's for all five fingers 
def fingersUp(land_mkslst):
    global tipId
    fingers = []
    # if Thunmb is up returns 0 if down returns 1
    try:
        if land_mkslst[tipId[0]][1] > land_mkslst[tipId[0]-1][1]:
             fingers.append(1)
        else:
            fingers.append(0)
    except:
        pass

    # if any of four fingers are up it retruns 1 otherwiae returns 0 to that finger index
    for i in range(1,5):
        try:
            if land_mkslst[tipId[i]][2] < land_mkslst[tipId[i]-1][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        except:
            break
    return fingers


############################################### CODE INITIALIZATION ##################################################


cap = cv2.VideoCapture(0)

while(1):
    _, img = cap.read()
    #converting frame BGR to RGB
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    #Making image not changable for processing ease
    img.flags.writeable=False

    results = hands.process(img)

    img.flags.writeable=True

    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

    # Drawing landmarks in input frame
    if results.multi_hand_landmarks:
        for num, h_landmks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(img,h_landmks,mp_hands.HAND_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(245, 218, 86),thickness=2,circle_radius=3),
                                            mp_drawing.DrawingSpec(color=(245, 218, 86),thickness=2,circle_radius=3))
                                        
   
    land_mkslst = findPosition(img)
    fingers = fingersUp(land_mkslst)
    # print(fingers)

    # taking x and y co-ordinate Index and Middel finger
    if len(land_mkslst)!=0:
        x1, y1 = land_mkslst[8][1:]
        x2, y2 = land_mkslst[12][1:]
    
    # move cursor if index finger is up and thumb is down    
    try:
        if fingers[1]==1 and fingers[2]==0 and fingers[0]==1:
            x3 = np.interp(x1, (frameR, width_cam - frameR), (0, width_scr))
            y3 = np.interp(y1, (frameR, Height_cam - frameR), (0, height_scr))
            clocX = plocX + (x3 - plocX)/smoothening
            clocY = plocY + (y3 - plocY)/smoothening
            autopy.mouse.move(width_scr-clocX, clocY)
            plocX, plocY = clocX, clocY
    except:
        pass

    # Right click if Index finger and middle finger is up and distance between them is less than 15
    try:
        if fingers[1]==1 and fingers[2]==1:
            if findDistance(8, 12, land_mkslst) < 15:
                pug.click(button='right')
    except:
        pass

    # Left click if Thumb is up and distance between Thumb and Index finger is less than 15
    try:
        if fingers[0]==0:
            if findDistance(4, 8, land_mkslst) < 15:
                pug.click(button='left')
    except:
        pass

    # Scroll Down on fist gesture
    try: 
        if(fingers[0]==1 and fingers[1]==0 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0):
            pug.scroll(-100)
            time.sleep(0.5)
            
    except:
        pass

    # Scroll Up if Middle Ring & Pinky finger is up
    try:
        if(fingers[0]==1 and fingers[1]==0 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1):
            pug.scroll(100)
            time.sleep(0.5)
            
    except:
        pass

    try:
        if fingers[0]==1 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==0:
            break 
    except:
        pass 
    
    cv2.imshow('Air-Mouse', cv2.flip(img, 1))
    cv2.waitKey(1)
    

cap.release()
cv2.destroyAllWindows()
