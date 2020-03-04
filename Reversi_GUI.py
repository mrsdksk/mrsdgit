#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as tic
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import random

INIT_WIDTH  = 800
INIT_HEIGHT = 800
INIT_DPI    = 100.0

EMPTY =  0
BLACK =  1
WHITE = -1
BOARD_SIZE = 8

MODE_BATTLE = 0
MODE_BLACK  = 1
MODE_WHITE  = 2
MODE_AUTO   = 3

WAIT_TIME = 500

TEXT_STYLE1 = 'QLabel {border:4px solid #000000;background-color: #f0f8ff;font: bold 24px; color: black; border-radius: 24;}'
TEXT_STYLE2 = 'QLabel {border:4px solid #000000;background-color: #ff0000;font: bold 24px; color: black; border-radius: 24;}'
TEXT_STYLE3 = 'QLabel {background-color: #f0f8ff;font: bold 16px; color: red;}'
TEXT_STYLE4 = 'QLabel {background-color: #f0f8ff;font: bold 16px; color: blue;}'
TEXT_STYLE5 = 'QLabel {background-color: #f0f8ff;font: bold 16px; color: black;}'

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        #self.setAcceptDrops(True)
        self.setFixedSize(INIT_WIDTH, INIT_HEIGHT)
        self.setGeometry(500, 35, INIT_WIDTH, INIT_HEIGHT)
        self.setWindowTitle('Reversi')
        self.setWindowIcon(QtGui.QIcon('Reversi.png'))
        self.plotarea = QtGui.QWidget(self)
        self.plotarea.setGeometry(0, 0, INIT_WIDTH, INIT_HEIGHT)

        self.fig = plt.figure(1,facecolor = '#f0f8ff')
        self.fig.set_dpi(INIT_DPI)
        self.fig.set_figwidth(INIT_WIDTH/INIT_DPI)
        self.fig.set_figheight(INIT_HEIGHT/INIT_DPI)
        self.cvs = FigureCanvasQTAgg(self.fig)
        self.cvs.setParent(self.plotarea)
        self.cvs.mpl_connect('button_press_event', self.buttonPressEvent)
        self.ax = [[0 for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.ax[i][j] = self.fig.add_subplot(8,8,8*i+j+1)
                self.ax[i][j].patch.set_facecolor('green')
                self.ax[i][j].set_aspect('equal')
                self.ax[i][j].set_xticklabels([]) 
                self.ax[i][j].set_yticklabels([])

        self.battle_mode = 0
        self.get_mode_Window()
        self.F_auto_stop = 0
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.com_turn)
        if self.battle_mode == MODE_AUTO:
            if self.F_auto_stop == 0:
                self.current_timer.setSingleShot(False)
        else:
            self.current_timer.setSingleShot(True)
        self.init_UI()
        self.init_data()

        #--TextBox----------------------------------------------------------
        self.textbox1 = QtGui.QLabel(self)
        self.textbox1.setGeometry(180, 35, 120, 50)
        self.textbox1.setStyleSheet(TEXT_STYLE2)
        self.textbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox1.setFont(QtGui.QFont("meiryo UI"))
        self.textbox1.setText("BLACK")

        self.textbox2 = QtGui.QLabel(self)
        self.textbox2.setGeometry(520, 35, 120, 50)
        self.textbox2.setStyleSheet(TEXT_STYLE1)
        self.textbox2.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox2.setFont(QtGui.QFont("meiryo UI"))
        self.textbox2.setText("WHITE")

        self.textbox3 = QtGui.QLabel(self)
        self.textbox3.setGeometry(310, 35, 200, 50)
        self.textbox3.setStyleSheet('QLabel {background-color: #f0f8ff;font: bold 48px; color: black;}')
        self.textbox3.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox3.setFont(QtGui.QFont("meiryo UI"))
        self.score(self.data)

        self.textbox4 = QtGui.QLabel(self)
        self.textbox4.setGeometry(100, 50, 75, 35)
        self.textbox4.setStyleSheet(TEXT_STYLE3)
        self.textbox4.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox4.setFont(QtGui.QFont("meiryo UI"))

        self.textbox5 = QtGui.QLabel(self)
        self.textbox5.setGeometry(645, 50, 75, 35)
        self.textbox5.setStyleSheet(TEXT_STYLE3)
        self.textbox5.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox5.setFont(QtGui.QFont("meiryo UI"))
        #--------------------------------------------------------------------------

    def init_UI(self):
        undoAction = QtGui.QAction("&Undo", self)
        undoAction.setShortcut('Ctrl+Z')
        undoAction.triggered.connect(self.undo_multiple)

        moveAction = QtGui.QAction("&Move on", self)
        moveAction.setShortcut('Ctrl+Y')
        moveAction.triggered.connect(self.move_multiple)

        resetAction = QtGui.QAction('&Reset', self)
        resetAction.setShortcut('Ctrl+R')
        resetAction.triggered.connect(self.game_reset)

        stopAction = QtGui.QAction('&Start/Stop', self)
        stopAction.setShortcut('Ctrl+P')
        stopAction.triggered.connect(self.auto_stop)

        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+W')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Menu')
        fileMenu.addAction(undoAction)
        fileMenu.addAction(moveAction)
        fileMenu.addAction(resetAction)
        fileMenu.addAction(stopAction)
        fileMenu.addAction(exitAction)        

    def init_data(self):
        self.data = [[0 for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)]
        self.data[3][4] = BLACK
        self.data[4][3] = BLACK
        self.data[3][3] = WHITE
        self.data[4][4] = WHITE
        self.player = BLACK
        self.turn_number = 0
        self.move_number = 0
        self.old_data = []
        self.old_invert = []
        self.move_on = []
        self.move_data = []
        print("Start!")
        if self.battle_mode == MODE_WHITE:
            self.current_timer.start(WAIT_TIME)
        elif self.battle_mode == MODE_AUTO:
            self.current_timer.start(WAIT_TIME)
            self.F_auto_stop = 0
            self.current_timer.setSingleShot(False)
        self.imshow_draw(self.data)

    def buttonPressEvent(self, event):        
        if 100 <= event.x <= 700 and 100 <= event.y <= 700:
            self.x, self.y = self.pressed_coordinate(event.x, event.y)
            co_invert = []
            co_invert = self.invert_coordinate(self.player, self.x, self.y, self.data)
            self.update(self.player, self.x, self.y, self.data, co_invert)
            if self.is_com_mode() == 1:
                if self.com_turn_check() == 1:
                    self.current_timer.start(WAIT_TIME)

    def update(self, player, x, y, data, invert_co):
        ret1 = self.put_check(x, y, data)
        if invert_co != []:
            if ret1 == 1:
                data[y][x] = player
                self.turn_number = self.turn_number + 1
                self.move_number = 0
                self.old_data.append([y, x])
                self.old_invert.append(invert_co)
                self.data = self.invert(player, invert_co, data)
                self.imshow_draw(self.data)
                self.player = self.switch_player(player)
                self.score(self.data)
                self.show_text_reset()
                ret5 = self.finish_check(data)
                if ret5 == 1:
                    print("Game Set!")
                    self.show_game_set()
                else:
                    ret2 = self.pass_check(self.player, self.data)
                    if ret2 == 1:
                        print("Pass!")
                        self.show_pass(self.player)
                        tmp_pl = self.switch_player(self.player)
                        ret3 = self.pass_check(tmp_pl, self.data)
                        ret4 = self.finish_check(self.data)
                        if ret3 == 1 or ret4 == 1:
                            print("Game Set!")
                            self.show_game_set()
                        else:
                            self.player = self.switch_player(self.player)
                            self.com_check = 1
                    else:
                        self.com_check = 1
            else:
                pass
        else:
            print("You can put your stone at another place.")

    def imshow_draw(self, data):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                c1 = patches.Circle(xy=(0, 0), radius=0.5, fc='k', ec='k')
                c2 = patches.Circle(xy=(0, 0), radius=0.5, fc='w', ec='k')
                c3 = patches.Circle(xy=(0, 0), radius=0.51, fc='green', ec='green')
                if data[j][i] == BLACK:
                    self.ax[j][i].add_patch(c1)
                elif data[j][i] == WHITE:
                    self.ax[j][i].add_patch(c2)
                else:
                    self.ax[j][i].add_patch(c3)             
                self.ax[j][i].set_xlim(-0.6,0.6)
                self.ax[j][i].set_ylim(-0.6,0.6)              
                self.ax[j][i].tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
        plt.subplots_adjust(wspace = .005, hspace = .005)
        self.cvs.draw()

    def switch_player(self, player):
        player = -player
        self.show_turn(player)
        return player

    def pressed_coordinate(self, x, y):
        n = 0
        m = 0
        while n < BOARD_SIZE:
            if 100 + 75*n <= x < 100 +75*(n+1):
                co_x = n
                break
            else:
                n = n + 1
        while m < BOARD_SIZE:
            if 100 + 75*m <= y < 100 +75*(m+1):
                co_y = 7 - m
                break
            else:
                m = m + 1
        return co_x, co_y

    def invert_coordinate(self, player, x, y, data):
        unit = [-1, 0, 1]        
        co_inv = []
        for a in unit:
            for b in unit:
                tmp = []
                direction = 0
                if a == 0 and b == 0:
                    continue
                while(True):
                    direction = direction + 1
                    dx = x + direction * a
                    dy = y + direction * b
                    if 0 <= dx < BOARD_SIZE and 0 <= dy < BOARD_SIZE:
                        check = data[dy][dx]
                        if check == EMPTY:
                            break
                        elif check == player:
                            if tmp != []:
                                co_inv.extend(tmp)
                            break
                        else:
                            tmp.append([dy, dx])
                    else:
                        break
        return co_inv

    def invert(self, player, co_inv, data):
        for i in range(len(co_inv)):
            data[co_inv[i][0]][co_inv[i][1]] = player
        return data

    def put_check(self, x, y, data):
        ret = 0
        if data[y][x] == EMPTY:
            ret = 1
        return ret

    def pass_check(self, player, data):
        ret = 0
        inv_co = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if data[j][i] != EMPTY:
                    continue
                inv_co.extend(self.invert_coordinate(player, i, j, data))
        if inv_co == []:
            ret = 1
        else:
            ret = 0
        return ret

    def finish_check(self, data):
        j = 0
        zero_exist = 0
        while j < BOARD_SIZE:
            if EMPTY in data[j]:
                break
            else:
                if j == BOARD_SIZE - 1:
                    zero_exist = 1
                j = j + 1
        return zero_exist

    def score(self, data):
        score_b = 0
        score_w = 0
        for j in range(BOARD_SIZE):
            score_b = score_b + data[j].count(BLACK)
            score_w = score_w + data[j].count(WHITE)
        self.score_black = score_b
        self.score_white = score_w
        if 0 <= self.score_black < 10:
            if 0 <= self.score_white < 10:
                self.textbox3.setText(str(self.score_black) + "   " + str(self.score_white))
            else:
                self.textbox3.setText(" " + str(self.score_black) + "   " + str(self.score_white))                
        else:
            if 0 <= self.score_white < 10:
                self.textbox3.setText(str(self.score_black) + "   " + " " + str(self.score_white))
            else:
                self.textbox3.setText(str(self.score_black) + "   " + str(self.score_white))

    def show_turn(self, player):
        if player == BLACK:
            self.textbox1.setStyleSheet(TEXT_STYLE2)
            self.textbox2.setStyleSheet(TEXT_STYLE1)
        elif player == WHITE:
            self.textbox1.setStyleSheet(TEXT_STYLE1)
            self.textbox2.setStyleSheet(TEXT_STYLE2)
        else:
            pass

    def show_pass(self, player):
        if player == BLACK:
            self.textbox4.setText("Pass!")
            self.textbox4.setStyleSheet(TEXT_STYLE5)
        elif player == WHITE:
            self.textbox5.setText("Pass!")
            self.textbox5.setStyleSheet(TEXT_STYLE5)
        else:
            pass

    def show_text_reset(self):
        self.textbox4.setText("")
        self.textbox5.setText("")

    def show_game_set(self):
        self.textbox1.setStyleSheet(TEXT_STYLE1)
        self.textbox2.setStyleSheet(TEXT_STYLE1)
        if self.score_black > self.score_white:
            self.textbox4.setText("Win!")
            self.textbox4.setStyleSheet(TEXT_STYLE3)
            self.textbox5.setText("Lose")
            self.textbox5.setStyleSheet(TEXT_STYLE4)
        elif self.score_black < self.score_white:
            self.textbox4.setText("Lose")
            self.textbox4.setStyleSheet(TEXT_STYLE4)
            self.textbox5.setText("Win!")
            self.textbox5.setStyleSheet(TEXT_STYLE3)
        else:
            self.textbox4.setText("Draw")
            self.textbox4.setStyleSheet(TEXT_STYLE5)
            self.textbox5.setText("Draw")
            self.textbox5.setStyleSheet(TEXT_STYLE5)

    def undo_multiple(self):
        if self.turn_number > 0:
            self.undo_multiple_sub()
            if self.is_com_mode() == 1:
               self.undo_multiple_sub() 
        else:
            pass

    def undo_multiple_sub(self):
        self.turn_number = self.turn_number - 1
        self.move_number = self.move_number + 1           
        old_invert = self.old_invert.pop(self.turn_number)
        old_data = self.old_data.pop(self.turn_number)
        self.move_on.append(old_invert)
        self.move_data.append(old_data)
        self.data = self.invert(self.player, old_invert, self.data)
        self.data[old_data[0]][old_data[1]] = EMPTY
        self.player = self.switch_player(self.player)
        self.imshow_draw(self.data)
        self.score(self.data)

    def move_multiple(self):
        if self.move_number > 0:
            self.move_number = self.move_number - 1
            self.turn_number = self.turn_number + 1
            move_on = self.move_on.pop(self.move_number)
            move_data = self.move_data.pop(self.move_number)
            self.old_invert.append(move_on)
            self.old_data.append(move_data)
            self.data = self.invert(self.player, move_on, self.data)
            self.data[move_data[0]][move_data[1]] = self.player
            self.player = self.switch_player(self.player)
            self.com_check = 1
            self.imshow_draw(self.data)
            self.score(self.data)
            if self.is_com_mode() == 1:
                if self.com_turn_check() == 1:
                    self.current_timer.start(WAIT_TIME)
        else:
            pass

    def game_reset(self):
        self.init_data()
        self.score(self.data)
        self.show_text_reset()
        self.show_turn(self.player)
    
    def com_put_select_max(self, player, data):
        tmp = []
        max_co = []
        put_max_co = [0, 0]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if data[j][i] != EMPTY:
                    continue
                tmp = self.invert_coordinate(player, i, j, data)
                if len(max_co) <= len(tmp):
                    max_co = tmp
                    put_max_co = [j, i]
        return max_co, put_max_co

    def com_put_select_random(self, player, data):
        tmp = []
        random_co = []
        put_random_co = [0, 0]
        tmp_list = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if data[j][i] != EMPTY:
                    continue
                tmp = self.invert_coordinate(player, i, j, data)
                if tmp != []:
                    tmp_list.append([j, i, tmp])
        if tmp_list != []:
            put_random_co[0], put_random_co[1], random_co = random.choice(tmp_list)
        return random_co, put_random_co

    def com_turn(self):
        #com_co, put_com_co =  self.com_put_select_max(self.player, self.data)
        com_co, put_com_co =  self.com_put_select_random(self.player, self.data)
        self.update(self.player, put_com_co[1], put_com_co[0], self.data, com_co)
        if self.battle_mode != MODE_AUTO:
            self.com_check = 0

    def com_turn_check(self):
        return self.com_check

    def get_mode_Window(self):
        subwindow = SubWindow(self)
        subwindow.show()

    def set_param(self, param):
        self.battle_mode = param

    def is_com_mode(self):
        ret = 0
        if self.battle_mode == MODE_BLACK or self.battle_mode == MODE_WHITE:
            ret = 1
        return ret
    
    def auto_stop(self):
        if self.battle_mode == MODE_AUTO:
            self.current_timer.setSingleShot(True)
            if self.F_auto_stop == 0:
                self.F_auto_stop = 1
            else:
                self.F_auto_stop = 0
                self.current_timer.setSingleShot(False)
        else:
            pass


class SubWindow:
    def __init__(self, parent = None):
        self.w = QtGui.QDialog(parent)
        self.w.setFixedSize(400, 300)
        self.w.setGeometry(750, 250, 400, 300)
        self.w.setWindowTitle('Select Mode')
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

        self.radio1 = QtGui.QRadioButton('Battle Mode')
        self.radio1.setCheckable(True)
        self.radio1.setFont(font1)
        self.radio1.clicked.connect(self.clicked)
        self.radio1.setChecked(True)
        self.radio2 = QtGui.QRadioButton('vs. WHITE')
        self.radio2.setFont(font1)
        self.radio2.clicked.connect(self.clicked)
        self.radio3 = QtGui.QRadioButton('vs. BLACK')
        self.radio3.setFont(font1)
        self.radio3.clicked.connect(self.clicked)
        self.radio4 = QtGui.QRadioButton('Auto Battle Mode')
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
            self.mode = MODE_BATTLE
        elif self.radio2.isChecked() == True:
            self.mode = MODE_BLACK
        elif self.radio3.isChecked() == True:
            self.mode = MODE_WHITE
        elif self.radio4.isChecked() == True:
            self.mode = MODE_AUTO
        else:
            pass        

    def show(self):
        self.w.exec_()

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
