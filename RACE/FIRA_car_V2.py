# @ 2020, Copyright Amirmohammad Zarif
# Compatible with firasimulator version 1.0.1 or higher
import FiraAuto
import time
import cv2
from functions import *
from time import sleep
#Calling the class
car = FiraAuto.car()

#connecting to the server (Simulator)
car.connect("127.0.0.1", 25001)

REFRENCE = 128
CURRENT_PXL = 128
SECOND_PXL = 128
#Counter variable
counter = 0
slope = 1
debug_mode = True
#control part
kp = 1
ki = 0.2
kd = 0.2
previous_error = 0
integral = 0
steer = 0
dt = 0.05
sensors = [1500,1500,1500]
position = 'right'
#sleep for 3 second to make sure that client connected to the simulator 
time.sleep(3)
time1 = time.time()
try:
    while(True):  
        if ((sensors[2]!=1500 or sensors[1]!=1500) and (position=='right')):
            error = REFRENCE - SECOND_PXL 

        elif ((sensors[0]!=1500 or sensors[1]!=1500) and (position=='left')):
            error = REFRENCE - SECOND_PXL 

        else:
            error = REFRENCE - CURRENT_PXL 

        integral = integral + error * dt
        if (ki * integral) > 10:
            integral = 10/ki
        derivative = (error - previous_error) / dt

        # steer = -(kp * error + ki * integral + kd * derivative)
        steer = -(kp * error)
        # print(steer)
        car.setSteering(steer)
        counter = counter + 1
        car.setSpeed(60)
        car.getData()
        if(counter > 4):
            sensors = car.getSensors() 
            frame = car.getImage()
            

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_frame, np.array([20,0,115]), np.array([50,255,130]))
            mask[0:110,:]=0
            points, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sorted_points = sorted(points, key=len)

            main_mask = cv2.fillPoly(np.zeros((256,256)), pts =[sorted_points[-1]], color=(255))
            second_mask = cv2.fillPoly(np.zeros((256,256)), pts =[sorted_points[-2]], color=(255))
            obstacle_mask = cv2.inRange(frame, np.array([170,170,160]), np.array([255,190,180]))
            obstacle_mask2 = cv2.inRange(frame, np.array([104,88,77]), np.array([255,211,93]))
            obstacle_res = cv2.bitwise_or(obstacle_mask, obstacle_mask2)

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame = cv2.blur(hsv_frame,(6,6))
            yellow_mask = cv2.inRange(hsv_frame, np.array([0,95,0]), np.array([31,255,255]))


            points, _ = cv2.findContours(obstacle_res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sorted_points = sorted(points, key=len)
            try:
                if cv2.contourArea(sorted_points[-1])>25:
                    x,y,w,h = cv2.boundingRect(sorted_points[-1])
                    mean_obstacle = np.mean(np.where(obstacle_res[y:y+h,x:x+w]>0), axis=1)[1] 

                    yellow_roi = np.mean(np.where(yellow_mask[y:y+h, :]>0), axis=1)[1] 

                    if mean_obstacle<yellow_roi:
                        print('obstacle is on left')
                    else:
                        print('obstacle is on right')

                    frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            except:
                pass

            cv2.imshow('frame',frame)
            cv2.imshow('right lane mask',main_mask)
            cv2.imshow('left lane mask',second_mask)
            cv2.imshow('obstacle mask',obstacle_res)
            cv2.imshow('yellow mask',yellow_mask)
            

            CURRENT_PXL = np.mean(np.where(main_mask[120:150,:]>0), axis=1)[1]
            SECOND_PXL = np.mean(np.where(second_mask[120:150,:]>0), axis=1)[1]

            if np.isnan(CURRENT_PXL): CURRENT_PXL = 128
            if np.isnan(SECOND_PXL): SECOND_PXL = 128

            a,slope = detect_yellow_line(frame)

            if slope<0:
                position = 'left'
            else:
                position = 'right'
            cv2.putText(a, position, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('yellow line', a)
            key = cv2.waitKey(1)
            # if key == ord('w'):
            #     cv2.imwrite('./obstacle_frame.jpg', frame)
        previous_error = error
        # sleep(dt)
        
finally:
    car.stop()