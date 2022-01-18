import cv2 as cv
import numpy as np
import dlib
import imutils
import keyboard
from math import hypot
import time
from datetime import datetime
from imutils.video import WebcamVideoStream
from plyer import notification
import screen_brightness_control as sbc
from tkinter import*
from tkinter import messagebox
import pyttsx3

#initialization of variables
starttime=0
mface=0
endtime=0
test=True
twenty=0
duration=0
time_2hr=0
timer=0
org=0
original=0
count=0
flag=0
linelength=0
totalratio=0
s_time=0
identifier=True
#Initializing voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 152)
engine.setProperty('volume', 1.0)

#Accessing Webcamera
cap=WebcamVideoStream(src=0).start()

#Loading the face detector and landmard predictor
detector=dlib.get_frontal_face_detector()
predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#Getting initial time 
minute=datetime.now().minute
second=datetime.now().second




#Function to find midpoint
def midpoint(p1,p2):
    return int((p1.x+p2.x)/2),int((p1.y+p2.y)/2)

#Function to find Blink Ratio
def blinkratio(eyept,facial_landmarks):

    #Getting (x,y) coordinates of left and right points
    leftpt=(facial_landmarks.part(eyept[0]).x,facial_landmarks.part(eyept[0]).y)
    rightpt=(facial_landmarks.part(eyept[3]).x,facial_landmarks.part(eyept[3]).y)

    
    #Getting (x,y) coordinates of top and bottom middle points   
    centertop=midpoint(facial_landmarks.part(eyept[1]),facial_landmarks.part(eyept[2]))
    centerbot=midpoint(facial_landmarks.part(eyept[5]),facial_landmarks.part(eyept[4]))

    #Drawing Horizontal and vertical lines using above points
    hor_line=cv.line(frame,leftpt,rightpt,(0,255,0),thickness=1)
    ver_line=cv.line(frame,centertop,centerbot,(0,255,0),thickness=1)

    #To find the length of the horizontal and vertical line
    h_line_length=np.sqrt((leftpt[0]-rightpt[0])**2 + (leftpt[1]-rightpt[1])**2)   
    v_line_length=np.sqrt((centertop[0]-centerbot[0])**2 + (centertop[1]-centerbot[1])**2)
    
    #Finding ratio
    a=v_line_length/h_line_length
    linelength=v_line_length
    return a


pre_ratio=100.0
while True:
    
    try:
        #Reading the video captured using webcamera as frames
        frame=cap.read()
        #Resizing the frame 
        frame=imutils.resize(frame,width=450) 
    except:

        #Displaying a tkinter window
        root=Tk()
        root.withdraw()
        display=messagebox.showinfo("Alert","Unable to access camera, the eye monitoring part will not work but the prior notification will be pushed")
        print(display)
        break

    #Converting frame to gray scale and apply filtering
    gray=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    gray=cv.bilateralFilter(gray,5,1,1)
    
    
    #Putting the count onto the screen
    blinktxt=cv.putText(frame,"Blink:"+str(count),(50,50),cv.FONT_HERSHEY_TRIPLEX,1.0,(0,0,255))
    #Detecting faces in the frames
    faces=detector(gray)
    
    #Multiple Face detection
    if(len(faces)>1):
        if test==True:
            test=False
            notification.notify(
            title = "Warning",
            message="Multiple Faces Detected" ,
            app_icon="teamwork.ico",
            
            timeout=2 )
    else:
        
        for face in faces:

            test=True
            
            

            
            #Plotting Landmarks on detected face
            landmarks=predictor(gray,face)
           
            x,y=face.left(),face.top()
            x1,y1=face.right(),face.bottom()

            #To draw rectagle around the face if detected
            cv.rectangle(frame,(x,y),(x1,y1),(0,0,200),thickness=2)
            lefteyeblinkratio=blinkratio([36,37,38,39,40,41],landmarks)
            rigtheyeblinkratio=blinkratio([42,43,44,45,46,47],landmarks)

            #Calculating the blink ratio
            totalratio=(lefteyeblinkratio+rigtheyeblinkratio)/2

            #Putting the Eye Aspect Ratio onto the screen
            cv.putText(frame,"EAR:"+str(round(totalratio,2)),(300,50),cv.FONT_HERSHEY_TRIPLEX,1.0,(0,0,255))
            

            #To find  eye is closed for 2sec
            if(pre_ratio<0.28 and totalratio<0.28):
                if(s_time==0):

                    s_time=time.time()
                else:

                    e_time=time.time()
                    if((e_time-s_time) < 2):


                        
                        s_time=0
            else:

                #To detect blinks
                if(totalratio>0.30):


                    if (pre_ratio<0.28):

                        
                        count=count+1
                        blinktxt=cv.putText(frame,"Blink:"+str(count),(50,50),cv.FONT_HERSHEY_TRIPLEX,1.0,(0,0,255))
                        s_time=0
        

    blinkcount=count
    pre_ratio=totalratio
    #Calculating blinks for 1min         
    if(((minute<datetime.now().minute) or (minute==59 and datetime.now().minute==0)) and second==datetime.now().second  and blinkcount<15):

        
        minute=datetime.now().minute
        second==datetime.now().second
        blinkcount=0
        count=0  
        timer=timer+1
        
    
    if(((minute<datetime.now().minute) or (minute==59 and datetime.now().minute==0)) and second==datetime.now().second  and blinkcount>15):

        minute=datetime.now().minute
        second=datetime.now().second
        blinkcount=0
        count=0     

    #Displaying captured frames  
    cv.imshow("Frame",frame)

    #Usage and blinks for 2hours
    if(len(faces)==1):
        if(starttime==0):
            starttime=time.time()
            
            
    
    if(len(faces)==0 and starttime!=0):

        endtime=time.time()
        time_diff=endtime-starttime
        duration=duration+time_diff
        starttime=0
    
    if(len(faces)==1):
        endt=time.time()
        endd=round(endt-starttime)
        
        original=endd+round(duration) 
    #To notify for 20mins of screen time
    if(original==1200):
        org=org+original
        previous=original
        original=0
        endd=0
        starttime=0
        duration=0
        if(previous==1200 and original!=1200):
            notification.notify(
            title = "Its 20minutes, You are using system for 20mins",
            message="Please try to look somewhere and try to avoid seeing screen for atlest 20sec" ,
            app_icon="eyeicon.ico",
            
            timeout=2 )
        
        
    #For 2hours    
    if(org==7200):

        notification.notify(
            title = "Alert",
            message="Your using the system for 2hours or more than 2hours.Please give some rest to your eyes" ,
            app_icon="4.ico",
            
            timeout=2 )
        engine.say("Your using the system for 2hours or more than 2hours.")
        engine.say("Please give some rest to your eyes..")
        engine.runAndWait()
        org=0
        curr_brightness=sbc.get_brightness(display=0)
        if(curr_brightness>=80):
            sbc.fade_brightness(60,start=curr_brightness)


    
    if timer==8:
        timer=0
        notification.notify(
            title = "Blink Rate",
            message="Blinkrate is less than the average rate" ,
            app_icon="eyeicon.ico",
            
            timeout=2 )
        engine.say("Your blink rate is lower than the average")
        engine.runAndWait()


    key=cv.waitKey(1)  
    if key==0:
        break

    
#If no camera is detected or camera is unaccessible   
while True:
    if(identifier==False):
        print("Exiting......")
        break

    else:
        try:
            
        
            time.sleep(1200)
            notification.notify(
                    title = "Alert",
                    message="20 minutes usage : DO SOME EYE EXERCISES" ,
                    app_icon="5.ico",
                
                    timeout=1 )
            
            time.sleep(7200)
            notification.notify(
                    title = "Alert",
                    message="Your using the system for 2hours or more than 2hours.Please give some rest to your eyes.." ,
                    app_icon="4.ico",
                
                    timeout=1 )
            engine.say("Your using the system for 2hours or more than 2hours.")
            engine.say("Please give some rest to your eyes..")
            engine.runAndWait()
            curr_brightness=sbc.get_brightness(display=0)
            if(curr_brightness>=80):
                sbc.fade_brightness(60,start=curr_brightness)

        except KeyboardInterrupt:
            print("Exiting.....")
            exit()

cap.stop()
cv.destroyAllWindows()
