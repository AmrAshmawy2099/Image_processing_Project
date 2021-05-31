from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle,
                             QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import cv2
import os
import numpy as np
from Line_Detection_Functions import CheckForGoal
from PIL import Image


class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle("Image Processing")

        # call media player:
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        # play Button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play)

        #Get Frame Button:
        self.GetFramee = QPushButton()
        self.GetFramee.clicked.connect(self.getFrame)
        self.GetFramee.setText("start processing")

        # Play Frame Button:
        self.playFramee = QPushButton()
        self.playFramee.clicked.connect(self.playframe)
        self.playFramee.setText("load output video")


        # horizontal slider:
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # error label:
        self.err_label = QLabel()
        self.err_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)



        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        # fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playBtn)
        controlLayout.addWidget(self.GetFramee)
        controlLayout.addWidget(self.playFramee)
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
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())

        if self.fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.fileName)))
            self.playBtn.setEnabled(True)
    def getFrame(self):
        videopath=self.fileName
        Goal, self.Video_path, Image_path = CheckForGoal(videopath)

        CheckForGoal(videopath)
        img = Image.open(Image_path)
        img.show()

    def playframe(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.Video_path)))
        #self.playBtn.setEnabled(True)


    def exitCall(self):
        sys.exit(exec_())

    def play(self):
        # x = self.fileName
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


def main():
    app = QApplication(sys.argv)
    player = Main()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()