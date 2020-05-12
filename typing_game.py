#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from PyQt4 import QtCore,QtGui
import numpy as np
import matplotlib.pyplot as plt
import sys
import csv
import random
import math

INIT_WIDTH  = 800
INIT_HEIGHT = 600
X = 950
Y = 70
RANGE_X = 1000

CHART_WIDTH  = 0.65
CHART_HEIGHT = 0.2
DEFAULT_X = 0.06
DEFAULT_Y = 0.7

BUTTON_STYLE = 'QPushButton {background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #ddd);\
                 font: bold 16px; color: black;border: 2px solid #555; border-radius: 11;} \
                 QPushButton:hover {background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #bbb);} \
                 QPushButton:pressed {background: qradialgradient(cx: 0.4, cy: -0.1,fx: 0.4, fy: -0.1,radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}'
TEXT_STYLE = 'QLabel {border:2px solid #000000;background-color: white;font: bold 16px; color: black; border-radius: 6;}'

ETM_TIMER = 100
ETM_GAME_TIMER = 300

LEVEL0 = 0
LEVEL1 = 1
LEVEL2 = 2
LEVEL3 = 3

def print_dir(obj, keyword = ''):
    for o in dir(obj):
        if keyword in o:
            print(o)

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        self.setAcceptDrops(True)
        self.setFixedSize(INIT_WIDTH, INIT_HEIGHT)
        self.setWindowTitle('Sushida')
        self.plotarea = QtGui.QWidget(self)
        self.plotarea.setGeometry(0, 0, INIT_WIDTH, INIT_HEIGHT)

        self.fig = plt.figure(1,facecolor = '#f0f8ff')
        self.fig.set_dpi(100)
        self.fig.set_figwidth(INIT_WIDTH/100.0)
        self.fig.set_figheight(INIT_HEIGHT/100.0)
        self.cvs = FigureCanvasQTAgg(self.fig)
        self.cvs.setParent(self.plotarea)

        self.timer = QtCore.QBasicTimer()
        self.game_timer = QtCore.QBasicTimer()
        self.step = 0
        self.gamecount = 0

        self.level = LEVEL0
        self.getSubWindow()

        #self.typing_list = self.getTypinglist()
        #self.typing_list_num = len(self.typing_list)

        self.F_finished = 0
        self.old_question = 0
        self.answerKey = ''
        self.innum = 0

        self.typos = 0

        path = r'C:\Users\K-Morisada\Documents\10_typing_game\Duke_Caboom4.png'
        self.view = QtGui.QGraphicsView(self)
        self.view.setGeometry(0, 448, 800, 152)
        self.view.setSceneRect(0, 0, 200, 150)
        self.item = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(path))
        self.item.setOffset(-(RANGE_X/2), 0)
        self.scene = QtGui.QGraphicsScene()
        self.scene.addItem(self.item)
        self.view.setScene(self.scene)

        self.initUI()
        """
        #--Debug Button------------------------------------------------------
        self.debugbtn = QtGui.QPushButton(self)
        self.debugbtn.setGeometry(700, 50, 85, 30)
        self.debugbtn.setEnabled(True)
        self.debugbtn.clicked.connect(self.debugfn)
        self.debugbtn.setStyleSheet(BUTTON_STYLE)
        self.debugbtn.setText('Debug')
        self.debugbtn.setFont(QtGui.QFont("meiryo UI"))
        #--------------------------------------------------------------------------
        """
        #--Question box-----------------------------------------------------------------
        self.questionbox = QtGui.QLabel(self)
        self.questionbox.setGeometry(100, 250, 600, 50)
        self.questionbox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: black; border-radius: 6;}')
        self.questionbox.setAlignment(QtCore.Qt.AlignCenter)
        self.questionbox.setFont(QtGui.QFont("meiryo UI"))
        self.questionbox.setText("Put 'Ctrl+Space' to start !")
        #---------------------------------------------------------------------------

        #--Question box(JPN)-----------------------------------------------------------------
        self.questionboxjpn = QtGui.QLabel(self)
        self.questionboxjpn.setGeometry(100, 200, 600, 50)
        self.questionboxjpn.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: black; border-radius: 6;}')
        self.questionboxjpn.setAlignment(QtCore.Qt.AlignCenter)
        self.questionboxjpn.setFont(QtGui.QFont("meiryo UI"))
        self.questionboxjpn.setText("'Ctrl+Space'でスタート")
        #---------------------------------------------------------------------------

        #--Answer box----------------------------------------------------------------
        self.answerbox = QtGui.QLabel(self)
        self.answerbox.setGeometry(100, 350, 600, 50)
        self.answerbox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: black; border-radius: 6;}')
        self.answerbox.setAlignment(QtCore.Qt.AlignCenter)
        self.answerbox.setFont(QtGui.QFont("meiryo UI"))
        self.answerbox.setText("")
        #--------------------------------------------------------------------------

        #--Progress bar--------------------------------------------------------------
        #self.progress = QtGui.QProgressBar(self)
        #self.progress.setGeometry(150, 25, 500, 10)
        #self.progress.setTextVisible(False)
        #--------------------------------------------------------------------------

        #--Judge box-----------------------------------------------------------------
        self.judgebox = QtGui.QLabel(self)
        self.judgebox.setGeometry(375, 80, 50, 50)
        self.judgebox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: blue; border-radius: 6;}')
        self.judgebox.setAlignment(QtCore.Qt.AlignCenter)
        self.judgebox.setFont(QtGui.QFont("meiryo UI"))
        self.judgebox.setText("")
        #---------------------------------------------------------------------------

        #--Game Timer box-----------------------------------------------------------------
        self.gametimerbox = QtGui.QLabel(self)
        self.gametimerbox.setGeometry(700, 20, 100, 50)
        self.gametimerbox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: blue; border-radius: 6;}')
        self.gametimerbox.setAlignment(QtCore.Qt.AlignCenter)
        self.gametimerbox.setFont(QtGui.QFont("meiryo UI"))
        self.gametimerbox.setText(str(math.floor(ETM_GAME_TIMER/10)))
        #---------------------------------------------------------------------------

    """
    def debugfn(self):
        self.changeDisplay()
        print("a")
    """

    def initUI(self):
        self.exitAction = QtGui.QAction('&Exit', self)
        self.exitAction.setShortcut('Ctrl+W')
        self.exitAction.triggered.connect(QtGui.qApp.quit)

        self.startAction = QtGui.QAction('&Start', self)
        self.startAction.setShortcut('Ctrl+Space')
        self.startAction.triggered.connect(self.gameStart)

        self.changeLevelAction = QtGui.QAction('&Change level', self)
        self.changeLevelAction.setShortcut('Ctrl+L')
        self.changeLevelAction.triggered.connect(self.getSubWindow)

        self.resetAction = QtGui.QAction('&Reset', self)
        self.resetAction.setShortcut('Esc')
        self.resetAction.triggered.connect(self.resetDisplay)

        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&Menu')
        self.fileMenu.addAction(self.startAction)
        self.fileMenu.addAction(self.resetAction)
        self.fileMenu.addAction(self.changeLevelAction)
        self.fileMenu.addAction(self.exitAction)
    
    def timerEvent(self, event):
        #reference: https://www.youtube.com/watch?v=rQZCvc6gB9Q
        if self.step >= ETM_TIMER:
            self.timer.stop()
            self.changeDisplay()
            self.resetScene()
        else:
            self.step += 1
        #self.progress.setValue(self.step*(100/ETM_TIMER))
        self.judgeAnswer()
        if self.step >= 10:
            self.clrJudgeDisplay()            
        self.redrawScene(self.step)
        self.gameCountdown()

    def resetDisplay(self):
        self.game_timer.stop()
        self.timer.stop()
        #self.progress.setValue(0)
        self.questionboxjpn.setText("'Ctrl+Space'でスタート")
        self.questionbox.setText("Put 'Ctrl+Space' !")
        self.clrAnswer()
        self.gamecount = 0
        self.gametimerbox.setText(str(math.floor(ETM_GAME_TIMER/10)))
        self.startAction.setEnabled(True)
        self.changeLevelAction.setEnabled(True)
        self.resetScene()

    def changeDisplay(self):
        self.setProgress()
        self.setQuestion()
        self.clrAnswer()
        self.clrInnum()

    def setProgress(self):
        self.timer.start(ETM_TIMER, self)
        self.step = 0

    def setQuestion(self):
        while True:
            self.question = random.choice(self.typing_list)
            self.question_eng = self.question[1]
            self.question_jpn = self.question[0]
            if self.is_sameQuestion() == 1:
                break
        self.questionbox.setText(self.question_eng)
        self.questionboxjpn.setText(self.question_jpn)
        self.old_question = self.question_eng
    
    def clrAnswer(self):
        self.answerbox.setText("")
        self.answerKey = ''

    def getAnswer(self):
        return self.answerbox.text()

    def judgeAnswer(self):
        self.answer = self.getAnswer()
        if self.question_eng == self.answer:
            self.judgebox.setText("○")
            self.changeDisplay()
            self.countRightAnswerNum()
    
    def clrJudgeDisplay(self):
        self.judgebox.setText("")

    def is_sameQuestion(self):
        F_chkQuestion = 0
        if self.question_eng != self.old_question:
            F_chkQuestion = 1
        return F_chkQuestion

    def getTypinglist(self):
        typlist_lv0 = [
                    ["たこ", "tako"],   \
                    ["いか", "ika"],\
                    ["まぐろ", "maguro"],           \
                    ["コーヒー", "ko-hi-"], \
                    ["とけい", "tokei"], \
                    ["つくえ", "tukue"]         \
                ]
        typlist_lv3 = [
                    ["僕は明日、昨日の君とデートする", "bokuhaasu,kinounokimitode-tosuru"],   \
                    ["今日はいい天気です", "kyouhaiitenkidesu"],\
                    ["やればできる", "yarebadekiru"],           \
                    ["明日はいい日になる", "asitahaiihininaru"], \
                    ["カフェオレが飲みたい", "kafeoreganomitai"], \
                    ["名探偵コナン", "meitanteikonann"]         \
                ]
        if self.level == LEVEL0:
            typlist = typlist_lv0
        elif self.level == LEVEL1:
            typlist = typlist_lv3
        elif self.level == LEVEL2:
            typlist = typlist_lv3
        elif self.level == LEVEL3:
            typlist = typlist_lv3
        else:
            typlist = typlist_lv3
        return typlist

    def gameStart(self):
        self.game_timer.start(ETM_GAME_TIMER, self)
        self.changeDisplay()
        self.F_finished = 0
        self.startAction.setEnabled(False)
        self.changeLevelAction.setEnabled(False)
        self.clrTypos()
        self.clrRightAnswerNum()

    def timeup(self):
        print("Time Up!")
        print("Right Answer: " + str(self.right_answer_num))
        print("Typos: " + str(self.typos))
        self.F_finished = 1

    def gameCountdown(self):
        if self.gamecount >= ETM_GAME_TIMER:
            self.timeup()
            self.game_timer.stop()
            self.timer.stop()
            #self.progress.setValue(0)
            self.clrAnswer()
            self.questionboxjpn.setText("Time UP !!")
            self.questionbox.setText("Retry: 'Ctrl+Space'")
            self.gamecount = 0
            self.gametimerbox.setText("--")
            self.startAction.setEnabled(True)
            self.changeLevelAction.setEnabled(True)
            self.resetScene()
            self.showResultWindow()
        else:
            self.gamecount += 1
            self.gametimerbox.setText(str(math.floor((ETM_GAME_TIMER-self.gamecount)/10)))

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Control:
                pass
            else:
                key = QtGui.QKeySequence(event.key()).toString()
                if self.F_finished == 0:
                    self.keyOk = self.chkPressKey(key.lower(), self.innum)
                    if self.keyOk == 1:
                        self.incrementNum()
    
    def chkPressKey(self, presskey, i):
        F_keyOk = 0
        if self.question_eng[i] == presskey:
            self.answerKey += self.question_eng[i]
            self.answerbox.setText(str(self.answerKey))
            F_keyOk = 1
        else:
            self.countTypos()
        return F_keyOk
    
    def incrementNum(self):
        if self.innum < len(self.question_eng):
            self.innum += 1
        else:
            self.innum = 0

    def clrInnum(self):
        self.innum = 0

    def countTypos(self):
        self.typos += 1

    def clrTypos(self):
        self.typos = 0

    def countRightAnswerNum(self):
        self.right_answer_num += 1

    def clrRightAnswerNum(self):
        self.right_answer_num = 0

    def redrawScene(self, co_x):
        self.item.setOffset(-(RANGE_X/2) + (RANGE_X/ETM_TIMER)*co_x, 0)
        self.view.setScene(self.scene)

    def resetScene(self):
        self.item.setOffset(-(RANGE_X/2), 0)
        self.view.setScene(self.scene)

    def getSubWindow(self):
        subwindow = SubWindow(self)
        subwindow.show()
        self.typing_list = self.getTypinglist()
        self.typing_list_num = len(self.typing_list)

    def set_param(self, param):
        self.level = param

    def showResultWindow(self):
        resultwindow = ResultWindow(self)
        resultwindow.show()
    
    def getResult(self):
        return self.right_answer_num

    def getTypos(self):
        return self.typos

class SubWindow:
    def __init__(self, parent = None):
        self.w = QtGui.QDialog(parent)
        self.w.setFixedSize(300, 300)
        self.w.setGeometry(800, 250, 300, 200)
        self.w.setWindowTitle('Select Level')
        self.parent = parent
        self.mode = 0

        font1 = QtGui.QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        font1.setWeight(75)
        font1.setFamily("meiryo UI")

        font2 = QtGui.QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setWeight(75)
        font2.setFamily("meiryo UI")

        self.radio1 = QtGui.QRadioButton('Lv.0')
        self.radio1.setCheckable(True)
        self.radio1.setFont(font1)
        self.radio1.clicked.connect(self.clicked)
        self.radio1.setChecked(True)
        self.radio2 = QtGui.QRadioButton('Lv.1')
        self.radio2.setFont(font1)
        self.radio2.clicked.connect(self.clicked)
        self.radio3 = QtGui.QRadioButton('Lv.2')
        self.radio3.setFont(font1)
        self.radio3.clicked.connect(self.clicked)
        self.radio4 = QtGui.QRadioButton('Lv.3')
        self.radio4.setFont(font1)
        self.radio4.clicked.connect(self.clicked)

        self.button = QtGui.QPushButton('OK')
        self.button.setFont(font2)
        self.button.clicked.connect(self.setParamOriginal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        layout.addWidget(self.radio3)
        layout.addWidget(self.radio4)
        layout.addWidget(self.button)

        self.w.setLayout(layout)

    def setParamOriginal(self):
        self.parent.set_param(self.mode)
        self.w.close()

    def clicked(self):
        if self.radio1.isChecked() == True:
            self.mode = LEVEL0
        elif self.radio2.isChecked() == True:
            self.mode = LEVEL1
        elif self.radio3.isChecked() == True:
            self.mode = LEVEL2
        elif self.radio4.isChecked() == True:
            self.mode = LEVEL3
        else:
            pass        

    def show(self):
        self.w.exec_()

class ResultWindow:
    def __init__(self, parent = None):
        self.r = QtGui.QDialog(parent)
        self.r.setFixedSize(300, 300)
        self.r.setGeometry(800, 250, 300, 200)
        self.r.setWindowTitle('Result')
        self.parent = parent
        self.result = self.parent.getResult()
        self.mistake = self.parent.getTypos()

        self.resultbox = QtGui.QLabel()
        #self.resultbox.setGeometry(50, 50, 50, 50)
        self.resultbox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: black; border-radius: 6;}')
        self.resultbox.setAlignment(QtCore.Qt.AlignCenter)
        self.resultbox.setFont(QtGui.QFont("meiryo UI"))
        self.resultbox.setText("Result: " + str(self.result))

        self.typosbox = QtGui.QLabel()
        #self.typosbox.setGeometry(50, 50, 50, 50)
        self.typosbox.setStyleSheet('QLabel {background-color: white;font: bold 28px; color: black; border-radius: 6;}')
        self.typosbox.setAlignment(QtCore.Qt.AlignCenter)
        self.typosbox.setFont(QtGui.QFont("meiryo UI"))
        self.typosbox.setText("Typos: " + str(self.mistake))

        font2 = QtGui.QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setWeight(75)
        font2.setFamily("meiryo UI")

        self.button = QtGui.QPushButton('OK')
        self.button.setFont(font2)
        self.button.clicked.connect(self.closeWindow)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.resultbox)
        layout.addWidget(self.typosbox)
        layout.addWidget(self.button)

        self.r.setLayout(layout)

    def closeWindow(self):
        self.r.close()      

    def show(self):
        self.r.exec_()


def main():
    try:
        app = QtGui.QApplication(sys.argv)
    except:
        pass

    w = Window()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
