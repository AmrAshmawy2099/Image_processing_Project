from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import cv2
import numpy as np

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle("Image Processing")

        # call media player:
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        #play Button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play)

        # horizontal slider:
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # error label:
        self.err_label = QLabel()
        self.err_label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # process
        getFrameAction = QAction(QIcon('open.png'), '&Process', self)
        getFrameAction.setStatusTip('Get frames')
        getFrameAction.triggered.connect(self.CheckForGoal)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(getFrameAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playBtn)
        controlLayout.addWidget(self.slider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.err_label)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",QDir.homePath())


        if self.fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.fileName)))
            self.playBtn.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        #x = self.fileName
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.set_position(position)

    def handleError(self):
        self.playBtn.setEnabled(False)
        self.err_label.setText("Error: " + self.mediaPlayer.errorString())

    def DetectLine(frame):
        # this function is used to detect the edges of the goal line ( upper edge )
        blurred = cv2.GaussianBlur(frame, (17, 17), 2)
        hlsFrame = cv2.cvtColor(blurred, cv2.COLOR_BGR2HLS)

        lower_threshold = np.uint8([30, 200, 30])
        upper_threshold = np.uint8([255, 255, 255])
        mask = cv2.inRange(hlsFrame, lower_threshold, upper_threshold)

        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (200, 200)))
        mask = cv2.Canny(mask, 50, 150)

        mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))

        lines = cv2.HoughLinesP(mask, rho=1, theta=np.pi / 180, threshold=100,
                                minLineLength=1600, maxLineGap=200)
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
            x1 = (lines[:, :, [0]]).min()
            y1 = (lines[:, :, [1]]).min()
            x2 = (lines[:, :, [2]]).max()
            y2 = (lines[:, :, [3]]).min()
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
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

        mask = cv2.inRange(hsvFrame, lower_blue, upper_blue)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
        if cnts is not None:
            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                center = (int(x), int(y))
                if (radius > 30):
                    return center, radius
                # cv2.imwrite("mask.png", frame)
                # cv2.circle(frame, (int(x), int(y)), int(radius),
                #            (0, 255, 255), 2)
                # cv2.circle(frame, center, 5, (0, 0, 255), -1)

        return -1, -1;

    def checkBallPosition(ball_center, ball_radius, line_edges):
        # first we should do the line equation
        x, y = ball_center
        x1, y1, x2, y2 = line_edges
        slope = (y1 - y2) / (x1 - x2)
        y_line = (x * slope) + y1 - x1
        tolerance = 22
        if (y + ball_radius - tolerance < y_line):
            return "GOAL"

    def CheckForGoal(self):
        #print("here")
        Video_Path=self.fileName
        print(Video_Path)

        ########## Initialize INPUT AND OUTPUT VIDEOS#############
        cap = cv2.VideoCapture(Video_Path)
        #print(cap.isOpened())

        Output_Name = Video_Path.split(".")[0] + "_output.avi"
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        out = cv2.VideoWriter(Output_Name, fourcc, 20, (1920, 1080), True)
        FoundLineFlag = 0
        ret = 1
        line_edges = 0
        ymin = 99999
        ################LOOP ON EVERY FRAME######################
        while ret:
            ret, frame = cap.read()
            if ret:
                ########## ONLY DETECT LINE ONCE BECAUSE IT IS STATIC ###################
                if FoundLineFlag == 0:
                    line_edges = self.DetectLine(frame)
                    if line_edges != -1:
                        FoundLineFlag = 1
                if FoundLineFlag == 1:
                    frame = cv2.line(frame, (line_edges[0], line_edges[1]), (line_edges[2], line_edges[3]), (0, 0, 255),
                                     10)
                #############################################################
                ################## FOR EACH FRAME DETECT THE BALL LOCATION ##############
                ball_center, ball_radius = self.DetectBall(frame)

                if ball_center != -1:
                    ############ IF BALL DETECTED DRAW BALL CONTOURS ############
                    cv2.circle(frame, ball_center, int(ball_radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame, ball_center, 5, (0, 0, 255), -1)
                    ############ Save Maximum Distance the ball has reached #########
                    if ball_center[1] < ymin:
                        ymin = ball_center[1]
                        Closest_Frame = frame.copy()
                    ########### Compare the ball position related to the line #######
                    result = self.checkBallPosition(ball_center, ball_radius, line_edges)
                    if result == "GOAL":
                        ############### ZOOM IN AROUND THE BAll ################
                        cropped_frame = frame[
                                        int(ball_center[1] - ball_radius - 200):int(ball_center[1] + ball_radius + 200),
                                        int(ball_center[0] - ball_radius - 200):int(ball_center[0] + ball_radius + 200)]
                        cropped_frame = cv2.resize(cropped_frame, (1920, 1080))
                        cv2.imwrite(Video_Path.split(".")[0] + "_output.png", cropped_frame)
                        ############## REPEAT THE FRAME THAT THE BALL PASSED THE LINE ###########
                        for i in range(50):
                            out.write(cropped_frame)
                        return "GOAL"

                out.write(frame)
        cv2.imwrite(Video_Path.split(".")[0] + "_output.png", Closest_Frame)
        return "NOT GOAL"

        out.release()

def main():

    app = QApplication(sys.argv)
    player = Main()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()