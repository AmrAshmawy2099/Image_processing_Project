import cv2
import numpy as np

def DetectLine(frame):
    # this function is used to detect the edges of the goal line ( upper edge )
    blurred = cv2.GaussianBlur(frame, (17, 17), 2)
    hlsFrame = cv2.cvtColor(blurred, cv2.COLOR_BGR2HLS)

    lower_threshold = np.uint8([30, 200, 30])
    upper_threshold = np.uint8([255, 255, 255])
    mask = cv2.inRange(hlsFrame, lower_threshold, upper_threshold)

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT,(200,200)))
    mask = cv2.Canny(mask, 50, 150)

    mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))



    lines = cv2.HoughLinesP(mask, rho = 1, theta = np.pi/180, threshold = 100,
                           minLineLength = 1600, maxLineGap =200)
    ############ DEBUGGING COMMENTS ##############
    # print (lines)
    # for line in lines:
    #     x1,y1,x2,y2=line[0]
        # print(x1,x2,y1,y2)
        # cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 5)
    # cv2.imwrite('Blabla.jpg', frame)
    ################################################
    if lines is not None:
        ####################### GET THE UPPER MOST LINE ################
        x1=(lines[:,:,[0]]).min()
        y1 = (lines[:, :, [1]]).min()
        x2=(lines[:,:,[2]]).max()
        y2=(lines[:,:,[3]]).min()
        edges = x1, y1, x2, y2
        ################################################################
        ######### DEBUGGING COMMENTS ####################
        # print("evaluated")
        # print(x1,x2,y1,y2)
        # cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        # cv2.imwrite('Blabla.jpg', frame)
        ##################################################



        return edges
    return -1


def DetectBall(frame):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsvFrame = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([78, 158, 124])
    upper_blue = np.array([138, 255, 255])
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))

    mask = cv2.inRange(hsvFrame, lower_blue, upper_blue)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)

    cnts,_=cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    if cnts is not None:
        if len(cnts)>0:
            c=max(cnts,key=cv2.contourArea)
            ((x,y),radius)= cv2.minEnclosingCircle(c)
            center=(int(x),int(y))
            if (radius>30):
                return center,radius
            # cv2.imwrite("mask.png", frame)
            # cv2.circle(frame, (int(x), int(y)), int(radius),
            #            (0, 255, 255), 2)
            # cv2.circle(frame, center, 5, (0, 0, 255), -1)

    return -1,-1;

def checkBallPosition(ball_center,ball_radius,line_edges):
    #first we should do the line equation
    x,y=ball_center
    x1,y1,x2,y2=line_edges
    slope=(y1-y2)/(x1-x2)
    y_line=(x*slope)+y1-x1
    tolerance=22
    if (y+ball_radius-tolerance<y_line):
        return "GOAL"
def CheckForGoal(Video_Path):
    ########## Initialize INPUT AND OUTPUT VIDEOS#############
    cap = cv2.VideoCapture(Video_Path)
    Output_Name=Video_Path.split(".")[0]+"_output.avi"
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    out = cv2.VideoWriter(Output_Name, fourcc, 20, (1920, 1080), True)
    FoundLineFlag=0
    ret = 1
    line_edges=0
    ymin=99999
    ################LOOP ON EVERY FRAME######################
    while ret:
        ret,frame=cap.read()
        if ret :
            ########## ONLY DETECT LINE ONCE BECAUSE IT IS STATIC ###################
            if FoundLineFlag==0:
                line_edges=DetectLine(frame)
                if line_edges != -1:
                    FoundLineFlag=1
            if FoundLineFlag ==1 :
                frame = cv2.line(frame, (line_edges[0], line_edges[1]), (line_edges[2], line_edges[3]), (0, 0, 255), 10)
            #############################################################
            ################## FOR EACH FRAME DETECT THE BALL LOCATION ##############
            ball_center, ball_radius = DetectBall(frame)

            if ball_center != -1:
                ############ IF BALL DETECTED DRAW BALL CONTOURS ############
                cv2.circle(frame, ball_center, int(ball_radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, ball_center, 5, (0, 0, 255), -1)
                ############ Save Maximum Distance the ball has reached #########
                if ball_center[1]<ymin:
                    ymin=ball_center[1]
                    Closest_Frame=frame.copy()
                ########### Compare the ball position related to the line #######
                result=checkBallPosition(ball_center,ball_radius,line_edges)
                if result == "GOAL":
                    ############### ZOOM IN AROUND THE BAll ################
                    cropped_frame = frame[int(ball_center[1] - ball_radius - 200):int(ball_center[1] + ball_radius + 200),
                                    int(ball_center[0] - ball_radius - 200):int(ball_center[0] + ball_radius + 200)]
                    cropped_frame=cv2.resize(cropped_frame,(1920,1080))
                    cv2.imwrite(Video_Path.split(".")[0]+"_output.png", cropped_frame)
                    ############## REPEAT THE FRAME THAT THE BALL PASSED THE LINE ###########
                    for i in range(50):
                        out.write(cropped_frame)
                    return "GOAL"

            out.write(frame)
    cv2.imwrite(Video_Path.split(".")[0] + "_output.png", Closest_Frame)
    return "NOT GOAL"



    out.release()

########### THIS FUNCTION IS USED TO TEST THE LINE DETECTION ###################
# def drawLine(name):
#     out_name=name.split(".")[0]+"_output.png"
#     frame=cv2.imread(name)
#     line_edges = DetectLine(frame)
#     if line_edges != -1:
#         frame = cv2.line(frame, (line_edges[0], line_edges[1]), (line_edges[2], line_edges[3]), (0, 0, 255), 10)
#         cv2.imwrite(out_name, frame)
################################################################################


#
# print(CheckForGoal('Input_Videos/Goal_1.mp4'))

#
# cv2.waitKey()








