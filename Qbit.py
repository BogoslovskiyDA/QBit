from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsScene, QMessageBox
from PyQt5.QtCore import QTimer
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

Form, _ = uic.loadUiType("file.ui")

class Ui(QtWidgets.QDialog, Form):

    Teta = 0.0
    Phi = 0.0
    TetaSh = 0.0
    PhiSh = 0.0

    Cos2Teta = 0.0
    Sin2Teta = 0.0

    #Матрицы операторов
    I = np.array([[1, 0], [0, 1]])
    PaulX = np.array([[0, 1], [1, 0]])
    PaulY = np.array([[0, complex(0, -1)], [complex(0, 1), 0]])
    PaulZ = np.array([[1, 0], [0, -1]])
    H = np.array([[1/np.sqrt(2), 1/np.sqrt(2)], [1/np.sqrt(2), -1/np.sqrt(2)]])

    q = np.array([[0.0], [0.0]], dtype=complex)
    qSh = np.array([[0.0], [0.0]], dtype=complex)
    A = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=complex)

    x0 = 0
    y0 = 0
    z0 = 0

    #Метки, для ориентации в работе формы
    FlagW = False
    Flag_draw_2 = False
    Flag_do_gate = 0
    Flag_Xgate = False
    Flag_Ygate = False
    Flag_Zgate = False
    Flag_Hgate = False
    FlagTime = False

    #Углы просмотра сцены
    Alpha3D = 30.0
    Beta3D = -30.0
    moveAlpha3D = 30.0
    moveBeta3D = -30.0

    #Создание точек для рисования сферы
    u, v = np.mgrid[0:2 * np.pi:10j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)

    my_counter = 1

    movePhi = 0.0
    moveTeta = 0.0
    ePhi = 0.0
    eTeta = 0.0
    Hook = 0.5

    '''Создание ивентов. Сопоставление функций с действиями на форме.'''
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.label.setFont(QFont('Consolas', 14))
        self.label_2.setFont(QFont('Consolas', 14))
        self.label_3.setFont(QFont('Consolas', 14))
        self.label_4.setFont(QFont('Consolas', 14))
        self.label_7.setFont(QFont('Consolas', 14))
        self.label_13.setFont(QFont('Consolas', 14))
        self.label_14.setFont(QFont('Consolas', 14))
        self.sliderTeta.valueChanged.connect(self.printSliderTeta)
        self.sliderPhi.valueChanged.connect(self.printSliderPhi)
        self.bDo.clicked.connect(self.bDoPressed)
        self.alphaB.clicked.connect(self.draw_ellipse)
        self.pushButton_4.clicked.connect(self.draw_ellipse2)
        self.pushButton.clicked.connect(self.draw_ellipse3)
        self.pushButton_2.clicked.connect(self.draw_ellipse4)
        self.pushButton_5.clicked.connect(self.draw_ellipse5)
        self.timerButton.clicked.connect(self.startMoveTimer)
        self.pauseButton.clicked.connect(self.pauseTimer)
        self.deleteButton.clicked.connect(self.deleteTimer)
        self.timerButton_3.clicked.connect(self.startMoveTimer_2)
        self.pauseButton_3.clicked.connect(self.pauseTimer_2)
        self.deleteButton_3.clicked.connect(self.deleteTimer_2)

        self.doubleSpinBox.valueChanged.connect(self.spinBoxChange)
        self.doubleSpinBox_2.valueChanged.connect(self.spinBoxChange2)
        self.doubleSpinBox_4.valueChanged.connect(self.spinBoxChange4)
        self.doubleSpinBox_5.valueChanged.connect(self.spinBoxChange5)

        self.comboBox.currentIndexChanged.connect(self.changeStep)
        self.comboBox_2.currentIndexChanged.connect(self.changeStep_2)

        self.bClear.clicked.connect(self.bClearPressed)
        self.pushButton_3.clicked.connect(self.swap)
        self.checkBox.stateChanged.connect(self.line_edit_I)
        self.checkBox_2.stateChanged.connect(self.line_edit_X)
        self.checkBox_3.stateChanged.connect(self.line_edit_Y)
        self.checkBox_5.stateChanged.connect(self.line_edit_Z)
        self.checkBox_6.stateChanged.connect(self.line_edit_H)
        self.checkBox_4.stateChanged.connect(self.line_edit_P)
        self.sliderTeta.setValue(0)

    '''Перенос значения с счётчика на поле ввода'''
    def spinBoxChange4(self):
        self.lineEdit_6.setText(f'{round(self.doubleSpinBox_4.value(), 4)}')

    '''Перенос значения с счётчика на поле ввода'''
    def spinBoxChange5(self):
        self.lineEdit_7.setText(f'{round(self.doubleSpinBox_5.value(), 4)}')

    '''Вобор шага для счётчика в выдвигающемся поле'''
    def changeStep(self):
        if (self.comboBox.currentIndex() == 0):
            step = round(np.pi/6, 4)
            self.doubleSpinBox.setSingleStep(step)
            self.doubleSpinBox.setValue(0.0)
        else:
            step = round(np.pi/4, 4)
            self.doubleSpinBox.setSingleStep(step)
            self.doubleSpinBox.setValue(0.0)

    '''Вобор шага для счётчика в выдвигающемся поле'''
    def changeStep_2(self):
        if (self.comboBox_2.currentIndex() == 0):
            step = round(np.pi/6, 4)
            self.doubleSpinBox_2.setSingleStep(step)
            self.doubleSpinBox_2.setValue(0.0)
        else:
            step = round(np.pi/4, 4)
            self.doubleSpinBox_2.setSingleStep(step)
            self.doubleSpinBox_2.setValue(0.0)

    '''Прекращение рисования спинового резонанса. Очищение второго окна'''
    def deleteTimer_2(self):
        #Изменение доступности некоторых кнопок
        self.pauseButton_3.setEnabled(False)
        self.timerButton.setEnabled(True)
        self.doubleSpinBox_3.setEnabled(True)
        self.bDo.setEnabled(True)
        self.bClear.setEnabled(True)
        self.pauseButton_3.setText('Пауза')
        timer_2.stop()
        self.FlagTime = False
        self.my_counter = 1
        self.deleteButton_3.setEnabled(False)
        self.label_3.setText('0.0')
        self.label_4.setText('0.0')
        scene = QGraphicsScene(self)
        self.graphicsView_2.setScene(scene)

    '''Пауза/продолжить отрисовку спинового резонанса'''
    def pauseTimer_2(self):
        if (timer_2.isActive()):
            timer_2.stop()
            self.pauseButton_3.setText('Продолжить')
        else:
            timer_2.start(300)
            self.pauseButton_3.setText('Пауза')

    '''Начать отрисовку спинового резонанса. Запуск таймера.'''
    def startMoveTimer_2(self):
        self.Hook = self.doubleSpinBox_3.value()
        self.my_counter = 1
        # Изменение доступности некоторых кнопок
        self.timerButton.setEnabled(False)
        self.doubleSpinBox_3.setEnabled(False)
        self.pauseButton_3.setEnabled(True)
        self.deleteButton_3.setEnabled(True)
        self.bClear.setEnabled(False)
        self.bDo.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pauseButton_3.setText('Пауза')
        self.FlagTime = True
        self.eTeta = self.Teta
        self.ePhi = self.Phi
        self.moveAlpha3D = self.Alpha3D
        self.moveBeta3D = self.Beta3D
        timer_2.start(250)

    '''Отрисовка спинового резонанса во втором окне'''
    def draw_move_2(self):
        if (self.my_counter == 200):
            self.my_counter = 0

        self.my_counter += 1

        self.moveTeta = self.my_counter * np.pi / 100
        self.movePhi = np.pi + self.Hook*self.moveTeta*0.5

        #Создание кубита. Рисование сферы и осей
        plt.close()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x, self.y, self.z, color="black", lw=0.5)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        frame1.axes.yaxis.set_ticklabels([])
        frame1.axes.zaxis.set_ticklabels([])
        x, y, z = self.convert_3d_plot_move(0, 0, 1)
        ax.quiver(0, 0, 0, x, y, z, length=1.0, color='red', lw=4)

        ax.quiver(0, 0, 0, 0, 0, 1.7, length=1.0, color='green', lw=1)
        ax.text(0, 0, 1.8, 'Z', rotation=38, fontsize=10)
        ax.text(0, 0, 1.2, '|0>', rotation=38, fontsize=13, color='red')
        ax.text(0, 0, -1.2, '|1>', rotation=38, fontsize=13, color='red')

        ax.quiver(0, 0, 0, 0, -1.7, 0, length=1.0, color='green', lw=1)
        ax.text(0, -1.8, 0, 'X', rotation=38, fontsize=10)

        ax.quiver(0, 0, 0, 1.7, 0, 0, length=1.0, color='green', lw=1)
        ax.text(1.8, 0, 0, 'Y', rotation=38, fontsize=10)

        ax.view_init(elev=self.moveAlpha3D, azim=self.moveBeta3D)
        ax.dist = 9
        ax.grid(False)
        scene = QGraphicsScene(self)
        scene.setSceneRect(100, 100, 300, 300)
        canvas = FigureCanvas(fig)
        canvas.setGeometry(0, 0, 500, 500)
        scene.addWidget(canvas)
        self.graphicsView_2.setScene(scene)
        self.label_3.setText(f'{round(np.cos(self.moveTeta/2) ** 2, 4)}')
        self.label_4.setText(f'{round(np.sin(self.moveTeta/2) ** 2, 4)}')

    '''Прекращение рисования прецессии. Очищение второго окна'''
    def deleteTimer(self):
        # Изменение доступности некоторых кнопок
        self.pauseButton.setEnabled(False)
        self.timerButton_3.setEnabled(True)
        self.bDo.setEnabled(True)
        self.bClear.setEnabled(True)
        self.pauseButton.setText('Пауза')
        timer.stop()
        self.FlagTime = False
        self.my_counter = 1
        self.deleteButton.setEnabled(False)
        self.label_3.setText('0.0')
        self.label_4.setText('0.0')
        scene = QGraphicsScene(self)
        self.graphicsView_2.setScene(scene)

    '''Пауза/продолжить отрисовку прецессии'''
    def pauseTimer(self):
        if (timer.isActive()):
            timer.stop()
            self.pauseButton.setText('Продолжить')
        else:
            timer.start(300)
            self.pauseButton.setText('Пауза')

    '''Начать отрисовку прецессиии. Запуск таймера.'''
    def startMoveTimer(self):
        self.my_counter = 1
        # Изменение доступности некоторых кнопок
        self.timerButton_3.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.bClear.setEnabled(False)
        self.bDo.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pauseButton.setText('Пауза')
        self.FlagTime = True
        self.moveTeta = self.Teta
        self.ePhi = self.Phi
        self.moveAlpha3D = self.Alpha3D
        self.moveBeta3D = self.Beta3D
        timer.start(250)

    '''Отрисовка прецессии во втором окне'''
    def draw_move(self):
        if (self.my_counter == 200):
            self.my_counter = 0

        self.my_counter += 1

        self.movePhi = self.ePhi + self.my_counter * np.pi / 100

        # Создание кубита. Рисование сферы и осей
        plt.close()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x, self.y, self.z, color="black", lw=0.5)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        frame1.axes.yaxis.set_ticklabels([])
        frame1.axes.zaxis.set_ticklabels([])
        x, y, z = self.convert_3d_plot_move(0, 0, 1)
        ax.quiver(0, 0, 0, x, y, z, length=1.0, color='red', lw=4)

        ax.quiver(0, 0, 0, 0, 0, 1.7, length=1.0, color='green', lw=1)
        ax.text(0, 0, 1.8, 'Z', rotation=38, fontsize=10)
        ax.text(0, 0, 1.2, '|0>', rotation=38, fontsize=13, color='red')
        ax.text(0, 0, -1.2, '|1>', rotation=38, fontsize=13, color='red')

        ax.quiver(0, 0, 0, 0, -1.7, 0, length=1.0, color='green', lw=1)
        ax.text(0, -1.8, 0, 'X', rotation=38, fontsize=10)

        ax.quiver(0, 0, 0, 1.7, 0, 0, length=1.0, color='green', lw=1)
        ax.text(1.8, 0, 0, 'Y', rotation=38, fontsize=10)

        ax.view_init(elev=self.moveAlpha3D, azim=self.moveBeta3D)
        ax.dist = 9
        ax.grid(False)
        scene = QGraphicsScene(self)
        scene.setSceneRect(100, 100, 300, 300)
        canvas = FigureCanvas(fig)
        canvas.setGeometry(0, 0, 500, 500)
        scene.addWidget(canvas)
        self.graphicsView_2.setScene(scene)
        self.label_3.setText(f'{round(self.Cos2Teta ** 2, 4)}')
        self.label_4.setText(f'{round(self.Sin2Teta ** 2, 4)}')

    '''Получение 3d координат точки по изменяющимся во времени углам'''
    def convert_3d_plot_move(self, x, y, z):
        tx = (x - self.x0)*np.cos(self.movePhi) - np.sin(self.movePhi)*((y-self.y0)*np.cos(self.moveTeta) - (z-self.z0)*np.sin(self.moveTeta))
        ty = (x - self.x0)*np.sin(self.movePhi) + np.cos(self.movePhi)*((y-self.y0)*np.cos(self.moveTeta) - (z-self.z0)*np.sin(self.moveTeta))
        tz = (y - self.y0)*np.sin(self.moveTeta) + (z - self.z0)*np.cos(self.moveTeta)
        return tx, ty, tz

    '''Считывание значения с счётчика и установка этого значения на слайдере'''
    def spinBoxChange(self):
        self.sliderTeta.setValue(round(self.doubleSpinBox.value()*100/np.pi))
        self.sliderPhi.setValue(round(self.doubleSpinBox_2.value() * 100 / np.pi))
        self.label_14.setText(f'{round(self.doubleSpinBox_2.value(), 4)}')
        self.label_13.setText(f'{round(self.doubleSpinBox.value(), 4)}')

    '''Считывание значения с счётчика и установка этого значения на слайдере'''
    def spinBoxChange2(self):
        self.sliderTeta.setValue(round(self.doubleSpinBox.value() * 100 / np.pi))
        self.sliderPhi.setValue(round(self.doubleSpinBox_2.value() * 100 / np.pi))
        self.label_14.setText(f'{round(self.doubleSpinBox_2.value(), 4)}')
        self.label_13.setText(f'{round(self.doubleSpinBox.value(), 4)}')

    '''Открытие окна ввода для гейта I'''
    def line_edit_I(self):
        if self.checkBox.isChecked():
            self.lineEdit.setEnabled(True)
            self.Flag_do_gate += 1
        else:
            self.lineEdit.setEnabled(False)
            self.Flag_do_gate -= 1

    '''Открытие окна ввода для гейта X'''
    def line_edit_X(self):
        if self.checkBox_2.isChecked():
            self.lineEdit_2.setEnabled(True)
            self.Flag_do_gate += 1
            self.Flag_Xgate = True
        else:
            self.lineEdit_2.setEnabled(False)
            self.Flag_Xgate = False
            self.Flag_do_gate -= 1

    '''Открытие окна ввода для гейта Y'''
    def line_edit_Y(self):
        if self.checkBox_3.isChecked():
            self.lineEdit_3.setEnabled(True)
            self.Flag_Ygate = True
            self.Flag_do_gate += 1
        else:
            self.lineEdit_3.setEnabled(False)
            self.Flag_Ygate = False
            self.Flag_do_gate -= 1

    '''Открытие окна ввода для гейта Z'''
    def line_edit_Z(self):
        if self.checkBox_5.isChecked():
            self.lineEdit_4.setEnabled(True)
            self.Flag_do_gate += 1
        else:
            self.lineEdit_4.setEnabled(False)
            self.Flag_do_gate -= 1

    '''Открытие окна ввода для гейта H'''
    def line_edit_H(self):
        if self.checkBox_6.isChecked():
            self.lineEdit_5.setEnabled(True)
            self.Flag_do_gate += 1
        else:
            self.lineEdit_5.setEnabled(False)
            self.Flag_do_gate -= 1

    '''Открытие окон ввода для фазового сдвига'''
    def line_edit_P(self):
        if self.checkBox_4.isChecked():
            self.lineEdit_6.setEnabled(True)
            self.lineEdit_7.setEnabled(True)
            self.doubleSpinBox_4.setEnabled(True)
            self.doubleSpinBox_5.setEnabled(True)
            self.Flag_do_gate += 1
        else:
            self.lineEdit_6.setEnabled(False)
            self.lineEdit_7.setEnabled(False)
            self.doubleSpinBox_4.setEnabled(False)
            self.doubleSpinBox_5.setEnabled(False)
            self.Flag_do_gate -= 1

    '''Проверка выбранных операторов и формирование матрицы преобразований'''
    def bDoPressed(self):
        if (self.Flag_do_gate == 0):
            QMessageBox.about(self, "Ошибка", "Выберите оператор")
            return
        FlagEx = True
        if self.checkBox.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            try:
                txt = self.lineEdit.text()
                if (txt == ''):
                    c = 1
                else:
                    txt = re.sub(r"\s+", "", txt, flags=re.UNICODE)
                    c = complex(txt)
                    if (c.real == 0 and c.imag == 0):
                        QMessageBox.about(self, "Ошибка", "Вводимое не должно быть нулём")
                        FlagEx = False
                self.A += c * self.I
            except:
                QMessageBox.about(self, "Ошибка I", "Вводимое должно быть комплексным числом")
                FlagEx = False
        if self.checkBox_2.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            self.Flag_Xgate = True
            try:
                txt = self.lineEdit_2.text()
                if (txt == ''):
                    c = 1
                else:
                    txt = re.sub(r"\s+", "", txt, flags=re.UNICODE)
                    c = complex(txt)
                    if (c.real == 0 and c.imag == 0):
                        QMessageBox.about(self, "Ошибка", "Вводимое не должно быть нулём")
                        FlagEx = False
                self.A += c * self.PaulX
            except:
                QMessageBox.about(self, "Ошибка X", "Вводимое должно быть комплексным числом")
                FlagEx = False
                self.Flag_Xgate = False
        if self.checkBox_3.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            self.Flag_Ygate = True
            try:
                txt = self.lineEdit_3.text()
                if (txt == ''):
                    c = 1
                else:
                    txt = re.sub(r"\s+", "", txt, flags=re.UNICODE)
                    c = complex(txt)
                    if (c.real == 0 and c.imag == 0):
                        QMessageBox.about(self, "Ошибка", "Вводимое не должно быть нулём")
                        FlagEx = False
                self.A += c * self.PaulY
            except:
                QMessageBox.about(self, "Ошибка Y", "Вводимое должно быть комплексным числом")
                FlagEx = False
                self.Flag_Ygate = False
        if self.checkBox_5.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            try:
                txt = self.lineEdit_4.text()
                if (txt == ''):
                    c = 1
                else:
                    txt = re.sub(r"\s+", "", txt, flags=re.UNICODE)
                    c = complex(txt)
                    if (c.real == 0 and c.imag == 0):
                        QMessageBox.about(self, "Ошибка", "Вводимое не должно быть нулём")
                        FlagEx = False
                self.A += c * self.PaulZ
            except:
                QMessageBox.about(self, "Ошибка Z", "Вводимое должно быть комплексным числом")
                FlagEx = False
            self.Flag_Zgate = True
        if self.checkBox_6.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            try:
                txt = self.lineEdit_5.text()
                if (txt == ''):
                    c = 1
                else:
                    txt = re.sub(r"\s+", "", txt, flags=re.UNICODE)
                    c = complex(txt)
                    if (c.real == 0 and c.imag == 0):
                        QMessageBox.about(self, "Ошибка", "Вводимое не должно быть нулём")
                        FlagEx = False
                self.A += c * self.H
            except:
                QMessageBox.about(self, "Ошибка H", "Вводимое должно быть комплексным числом")
                FlagEx = False
            self.Flag_Hgate = True
        if self.checkBox_4.isChecked():
            self.FlagW = True
            self.Flag_draw_2 = True
            try:
                txt1 = self.lineEdit_6.text()
                txt2 = self.lineEdit_7.text()
                if (txt1 == ''):
                    phi1 = complex(0, 0)
                else:
                    txt1 = re.sub(r"\s+", "", txt1, flags=re.UNICODE)
                    phi1 = complex(txt1)
                if (txt2 == ''):
                    phi2 = complex(0, 0)
                else:
                    txt2 = re.sub(r"\s+", "", txt2, flags=re.UNICODE)
                    phi2 = complex(txt2)
                self.A += np.array([[1, 0], [0, np.exp(complex(0, phi2 - phi1))]])
            except:
                QMessageBox.about(self, "Ошибка P", "Вводимое должно быть комплексным числом")
                FlagEx = False
        if (FlagEx):
            if (self.FlagW):
                self.pushButton_3.setEnabled(True)
            self.matrix()

    '''Вычисление углов, после действия операторов на кубит'''
    def matrix(self):
        ex = 0

        #Проверка унитарности
        if (round(np.conj(self.A.T)[0][0], 3) == round(np.linalg.inv(self.A)[0][0], 3)):
            ex += 1
        if (round(np.conj(self.A.T)[0][1], 3) == round(np.linalg.inv(self.A)[0][1], 3)):
            ex += 1
        if (round(np.conj(self.A.T)[1][0], 3) == round(np.linalg.inv(self.A)[1][0], 3)):
            ex += 1
        if (round(np.conj(self.A.T)[1][1], 3) == round(np.linalg.inv(self.A)[1][1], 3)):
            ex +=1

        if (ex == 4):
            #Если действует один оператор
            if (self.Flag_do_gate == 1):
                if (self.Flag_Xgate):
                    self.TetaSh = abs(self.Teta - np.pi)
                    self.PhiSh = -self.Phi + 2*np.pi
                elif (self.Flag_Ygate):
                    self.TetaSh = -self.Teta + np.pi
                    self.PhiSh = -self.Phi + np.pi
                else:
                    self.qSh = self.A.dot(self.q)
                    p_1 = np.sqrt((self.qSh[0][0].real)**2 + (self.qSh[0][0].imag)**2)
                    self.TetaSh = 2*np.arccos(round(p_1, 5))
                    phi_1 = 0.0
                    phi_2 = 0.0
                    if (self.qSh[0][0].real > 0.0 and self.qSh[0][0].imag >= 0.0):
                        phi_1 = round(np.arctan(self.qSh[0][0].imag/self.qSh[0][0].real), 5)
                    elif (self.qSh[0][0].real < 0.0 and self.qSh[0][0].imag >= 0.0):
                        phi_1 = np.pi - np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                    elif (self.qSh[0][0].real < 0.0 and self.qSh[0][0].imag < 0.0):
                        phi_1 = np.pi + np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                    elif (self.qSh[0][0].real > 0.0 and self.qSh[0][0].imag < 0.0):
                        phi_1 = 2*np.pi - np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                    elif (round(self.qSh[0][0].real,2) == 0.0 and self.qSh[0][0].imag > 0.0):
                        phi_1 = np.pi/2
                    elif (round(self.qSh[0][0].real,2) == 0.0 and self.qSh[0][0].imag < 0.0):
                        phi_1 = 3*np.pi/2

                    if (self.qSh[1][0].real > 0.0 and self.qSh[1][0].imag >= 0.0):
                        phi_2 = np.arctan(self.qSh[1][0].imag/self.qSh[1][0].real)
                    elif (self.qSh[1][0].real < 0.0 and self.qSh[1][0].imag >= 0.0):
                        phi_2 = np.pi - np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                    elif (self.qSh[1][0].real < 0.0 and self.qSh[1][0].imag < 0.0):
                        phi_2 = np.pi + np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                    elif (self.qSh[1][0].real > 0.0 and self.qSh[1][0].imag < 0.0):
                        phi_2 = 2*np.pi - np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                    elif (round(self.qSh[1][0].real, 2) == 0.0 and self.qSh[1][0].imag > 0.0):
                        phi_2 = np.pi/2
                    elif (round(self.qSh[1][0].real, 2) == 0.0 and self.qSh[1][0].imag < 0.0):
                        phi_2 = 3*np.pi/2

                    self.PhiSh = np.abs(phi_2 - phi_1)
            #Если действуют несколько операторов
            else:
                self.qSh = self.A.dot(self.q)
                p_1 = np.sqrt((self.qSh[0][0].real) ** 2 + (self.qSh[0][0].imag) ** 2)
                self.TetaSh = 2 * np.arccos(round(p_1, 5))
                phi_1 = 0.0
                phi_2 = 0.0
                if (self.qSh[0][0].real > 0.0 and self.qSh[0][0].imag >= 0.0):
                    phi_1 = round(np.arctan(self.qSh[0][0].imag / self.qSh[0][0].real), 5)
                elif (self.qSh[0][0].real < 0.0 and self.qSh[0][0].imag >= 0.0):
                    phi_1 = np.pi - np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                elif (self.qSh[0][0].real < 0.0 and self.qSh[0][0].imag < 0.0):
                    phi_1 = np.pi + np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                elif (self.qSh[0][0].real > 0.0 and self.qSh[0][0].imag < 0.0):
                    phi_1 = 2 * np.pi - np.arctan(abs(self.qSh[0][0].imag / self.qSh[0][0].real))
                elif (round(self.qSh[0][0].real, 2) == 0.0 and self.qSh[0][0].imag > 0.0):
                    phi_1 = np.pi / 2
                elif (round(self.qSh[0][0].real, 2) == 0.0 and self.qSh[0][0].imag < 0.0):
                    phi_1 = 3 * np.pi / 2

                if (self.qSh[1][0].real > 0.0 and self.qSh[1][0].imag >= 0.0):
                    phi_2 = np.arctan(self.qSh[1][0].imag / self.qSh[1][0].real)
                elif (self.qSh[1][0].real < 0.0 and self.qSh[1][0].imag >= 0.0):
                    phi_2 = np.pi - np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                elif (self.qSh[1][0].real < 0.0 and self.qSh[1][0].imag < 0.0):
                    phi_2 = np.pi + np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                elif (self.qSh[1][0].real > 0.0 and self.qSh[1][0].imag < 0.0):
                    phi_2 = 2 * np.pi - np.arctan(abs(self.qSh[1][0].imag / self.qSh[1][0].real))
                elif (round(self.qSh[1][0].real, 2) == 0.0 and self.qSh[1][0].imag > 0.0):
                    phi_2 = np.pi / 2
                elif (round(self.qSh[1][0].real, 2) == 0.0 and self.qSh[1][0].imag < 0.0):
                    phi_2 = 3 * np.pi / 2

                self.PhiSh = np.abs(phi_2 - phi_1)

            self.draw_graph_second()
            self.label_3.setText(f'{round(np.cos(self.TetaSh/2)**2, 4)}')
            self.label_4.setText(f'{round(np.sin(self.TetaSh/2)**2, 4)}')
        else:
            QMessageBox.about(self, "Ошибка", "Условие унитарности не выполнено")
        self.A[:] = 0.0

    '''Возвращение формы в начально состояние. Очистка второго окна'''
    def bClearPressed(self):
        self.sliderTeta.setValue(0)
        self.sliderPhi.setValue(0)
        self.FlagW = False
        self.Flag_draw_2 = False
        self.Flag_Ygate = False
        self.Flag_Xgate = False
        scene = QGraphicsScene(self)
        self.graphicsView_2.setScene(scene)
        self.pushButton_3.setEnabled(False)
        self.Flag_do_gate = 0
        self.doubleSpinBox_4.setValue(0.0)
        self.doubleSpinBox_5.setValue(0.0)
        self.doubleSpinBox_4.setEnabled(False)
        self.doubleSpinBox_5.setEnabled(False)
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit_3.setText('')
        self.lineEdit_4.setText('')
        self.lineEdit_5.setText('')
        self.lineEdit_5.setText('')
        self.lineEdit_6.setText('')
        self.lineEdit_7.setText('')
        self.checkBox.setCheckState(False)
        self.checkBox_2.setCheckState(False)
        self.checkBox_3.setCheckState(False)
        self.checkBox_4.setCheckState(False)
        self.checkBox_5.setCheckState(False)
        self.checkBox_6.setCheckState(False)
        self.doubleSpinBox.setValue(0.0)
        self.doubleSpinBox_2.setValue(0.0)
        self.Flag_do_gate = 0
        self.label_3.setText("0.0")
        self.label_4.setText("0.0")

    '''Перенос углов с второго окна на первое'''
    def swap(self):
        t1 = self.label_3.text()
        t2 = self.label_4.text()
        self.q[0][0] = np.cos(self.TetaSh/2)
        self.q[1][0] = np.sin(self.TetaSh/2) * np.exp(complex(0, self.PhiSh))
        self.Teta = self.TetaSh
        if (self.PhiSh < 0.0):
            self.Phi = 2*np.pi + self.PhiSh
        else:
            self.Phi = self.PhiSh
        self.q = self.qSh

        tet = round(self.Teta*100/np.pi)
        self.sliderTeta.setValue(tet)

        ph = round(self.Phi * 100 / np.pi)
        self.sliderPhi.setValue(np.abs(int(ph)))

    '''Считывание изменения с слайдера угла Тета. Вызов перерисовки окон.'''
    def printSliderTeta(self):
        self.Teta = round(self.sliderTeta.value()*np.pi/100, 4)
        self.Cos2Teta = np.cos(self.Teta/2)
        if (self.sliderTeta.value() == 100):
            self.Cos2Teta = 0.0
        self.Sin2Teta = np.sin(self.Teta/2)

        self.q[0][0] = self.Cos2Teta
        self.q[1][0] = self.Sin2Teta*np.exp(complex(0, self.Phi))
        if (self.Flag_draw_2):
            self.bDoPressed()
        else:
            self.draw_graph_first()
        self.label_13.setText(f'{round(self.Teta, 4)}')
        self.label_14.setText(f'{round(self.Phi, 4)}')
        self.label.setText(f'{round(self.Cos2Teta**2, 4)}')
        self.label_2.setText(f'{round(self.Sin2Teta**2, 4)}')

    '''Считывание изменения с слайдера угла Фи. Вызов перерисовки окон.'''
    def printSliderPhi(self):
        self.Phi = self.sliderPhi.value()*np.pi/100

        self.q[0][0] = self.Cos2Teta
        self.q[1][0] = self.Sin2Teta * np.exp(complex(0, self.Phi))
        if (self.Flag_draw_2):
            self.bDoPressed()
        else:
            self.draw_graph_first()
        self.label_13.setText(f'{round(self.Teta, 4)}')
        self.label_14.setText(f'{round(self.Phi, 4)}')
        self.label.setText(f'{round(self.Cos2Teta ** 2, 4)}')
        self.label_2.setText(f'{round(self.Sin2Teta ** 2, 4)}')

    '''Изменение угла просмотра кубита'''
    def draw_ellipse(self):
        self.Alpha3D += 10
        if (self.Flag_draw_2):
            self.bDoPressed()
            self.draw_graph_second()
        elif (self.FlagTime):
            self.draw_graph_first()
        else:
            self.draw_graph_first()

    '''Изменение угла просмотра кубита'''
    def draw_ellipse2(self):
        self.Alpha3D -= 10
        if (self.Flag_draw_2):
            self.bDoPressed()
            self.draw_graph_second()
        elif (self.FlagTime):
            self.draw_graph_first()
        else:
            self.draw_graph_first()

    '''Изменение угла просмотра кубита'''
    def draw_ellipse3(self):
        self.Beta3D -= 10
        if (self.Flag_draw_2):
            self.bDoPressed()
            self.draw_graph_second()
        elif (self.FlagTime):
            self.draw_graph_first()
        else:
            self.draw_graph_first()

    '''Изменение угла просмотра кубита'''
    def draw_ellipse4(self):
        self.Beta3D += 10
        if (self.Flag_draw_2):
            self.bDoPressed()
            self.draw_graph_second()
        elif (self.FlagTime):
            self.draw_graph_first()
        else:
            self.draw_graph_first()

    '''Изменение угла просмотра кубита. Возвращение в исходное положение'''
    def draw_ellipse5(self):
        self.Beta3D = -30
        self.Alpha3D = 30
        if (self.Flag_draw_2):
            self.bDoPressed()
            self.draw_graph_second()
        elif (self.FlagTime):
            self.draw_graph_first()
        else:
            self.draw_graph_first()

    '''Получение 3d координат точки для первого окна'''
    def convert_3d_plot_first(self, x, y, z):
        tx = (x - self.x0)*np.cos(self.Phi) - np.sin(self.Phi)*((y-self.y0)*np.cos(self.Teta) - (z-self.z0)*np.sin(self.Teta))
        ty = (x - self.x0)*np.sin(self.Phi) + np.cos(self.Phi)*((y-self.y0)*np.cos(self.Teta) - (z-self.z0)*np.sin(self.Teta))
        tz = (y - self.y0)*np.sin(self.Teta) + (z - self.z0)*np.cos(self.Teta)
        return tx, ty, tz

    '''Получение 3d координат точки для второго окна'''
    def convert_3d_plot_second(self, x, y, z):
        tx = (x - self.x0)*np.cos(self.PhiSh) - np.sin(self.PhiSh)*((y-self.y0)*np.cos(self.TetaSh) - (z-self.z0)*np.sin(self.TetaSh))
        ty = (x - self.x0)*np.sin(self.PhiSh) + np.cos(self.PhiSh)*((y-self.y0)*np.cos(self.TetaSh) - (z-self.z0)*np.sin(self.TetaSh))
        tz = (y - self.y0)*np.sin(self.TetaSh) + (z - self.z0)*np.cos(self.TetaSh)
        return tx, ty, tz

    '''Отрисовка первого окна'''
    def draw_graph_first(self):
        # Создание кубита. Рисование сферы и осей
        plt.close()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x, self.y, self.z, color="black", lw=0.5)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        frame1.axes.yaxis.set_ticklabels([])
        frame1.axes.zaxis.set_ticklabels([])
        x, y, z = self.convert_3d_plot_first(0, 0, 1)
        ax.quiver(0, 0, 0, x, y, z, length=1.0, color='red', lw=4)

        ax.quiver(0, 0, 0, 0, 0, 1.7, length=1.0, color='green', lw=1)
        ax.text(0, 0, 1.8, 'Z', rotation=38, fontsize=10)
        ax.text(0, 0, 1.2, '|0>', rotation=38, fontsize=13, color='red')
        ax.text(0, 0, -1.2, '|1>', rotation=38, fontsize=13, color='red')

        ax.quiver(0, 0, 0, 0, -1.7, 0, length=1.0, color='green', lw=1)
        ax.text(0, -1.8, 0, 'X', rotation=38, fontsize=10)

        ax.quiver(0, 0, 0, 1.7, 0, 0, length=1.0, color='green', lw=1)
        ax.text(1.8, 0, 0, 'Y', rotation=38, fontsize=10)

        ax.view_init(elev=self.Alpha3D, azim=self.Beta3D)
        ax.dist = 9
        ax.grid(False)
        scene = QGraphicsScene(self)
        scene.setSceneRect(100, 100, 300, 300)
        canvas = FigureCanvas(fig)
        canvas.setGeometry(0, 0, 500, 500)
        scene.addWidget(canvas)
        self.graphicsView.setScene(scene)

    '''Одновременная отрисока двух окон'''
    def draw_graph_second(self):
        # Создание кубита для перого окна. Рисование сферы и осей
        plt.close()
        plt2.close()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x, self.y, self.z, color="black", linewidth=0.5)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        frame1.axes.yaxis.set_ticklabels([])
        frame1.axes.zaxis.set_ticklabels([])
        xx, yy, zz= self.convert_3d_plot_first(0, 0, 1)
        ax.quiver(0, 0, 0, xx, yy, zz, length=1.0, color='red', lw=4)

        ax.quiver(0, 0, 0, 0, 0, 1.7, length=1.0, color='green', lw=1)
        ax.text(0, 0, 1.8, 'Z', rotation=38, fontsize=10)
        ax.text(0, 0, 1.2, '|0>', rotation=38, fontsize=13, color='red')
        ax.text(0, 0, -1.2, '|1>', rotation=38, fontsize=13, color='red')

        ax.quiver(0, 0, 0, 0, -1.7, 0, length=1.0, color='green', lw=1)
        ax.text(0, -1.8, 0, 'X', rotation=38, fontsize=10)

        ax.quiver(0, 0, 0, 1.7, 0, 0, length=1.0, color='green', lw=1)
        ax.text(1.8, 0, 0, 'Y', rotation=38, fontsize=10)

        ax.view_init(elev=self.Alpha3D, azim=self.Beta3D)
        ax.dist = 9
        ax.grid(False)
        scene = QGraphicsScene(self)
        scene.setSceneRect(100, 100, 300, 300)
        canvas = FigureCanvas(fig)
        canvas.setGeometry(0, 0, 500, 500)
        scene.addWidget(canvas)

        # Создание кубита для второго окна. Рисование сферы и осей
        fig2 = plt2.figure()
        ax2 = fig2.gca(projection='3d')
        ax2.plot_wireframe(self.x, self.y, self.z, color="black", lw=0.5)
        frame1 = plt2.gca()
        frame1.axes.xaxis.set_ticklabels([])
        frame1.axes.yaxis.set_ticklabels([])
        frame1.axes.zaxis.set_ticklabels([])
        xx, yy, zz = self.convert_3d_plot_second(0, 0, 1)
        ax2.quiver(0, 0, 0, xx, yy, zz, length=1.0, color='red', lw=4)

        ax2.quiver(0, 0, 0, 0, 0, 1.7, length=1.0, color='green', lw=1)
        ax2.text(0, 0, 1.8, 'Z', rotation=38, fontsize=10)
        ax2.text(0, 0, 1.2, '|0>', rotation=38, fontsize=13, color='red')
        ax2.text(0, 0, -1.2, '|1>', rotation=38, fontsize=13, color='red')

        ax2.quiver(0, 0, 0, 0, -1.7, 0, length=1.0, color='green', lw=1)
        ax2.text(0, -1.8, 0, 'X', rotation=38, fontsize=10)

        ax2.quiver(0, 0, 0, 1.7, 0, 0, length=1.0, color='green', lw=1)
        ax2.text(1.8, 0, 0, 'Y', rotation=38, fontsize=10)

        ax2.view_init(elev=self.Alpha3D, azim=self.Beta3D)
        ax2.dist = 9
        ax2.grid(False)
        scene2 = QGraphicsScene(self)
        scene2.setSceneRect(100, 100, 300, 300)
        canvas2 = FigureCanvas(fig2)
        canvas2.setGeometry(0, 0, 500, 500)
        scene2.addWidget(canvas2)
        self.graphicsView.setScene(scene)
        self.graphicsView_2.setScene(scene2)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Ui()
    w.show()
    timer = QTimer()
    timer.timeout.connect(w.draw_move)
    timer_2 = QTimer()
    timer_2.timeout.connect(w.draw_move_2)
    sys.exit(app.exec_())
