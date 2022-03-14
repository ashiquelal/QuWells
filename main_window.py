
import sys

# import some PyQt5 modules
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from PyQt5.uic import loadUi

from matplotlib.figure import Figure

# import MatPlotLib module and setting it to Qt env
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 


class MainWindow(QMainWindow):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        
        QMainWindow.__init__(self)
        self.eqn_elt = [['a','b'],['a','b','c']]
        self.eqn_list = [self.linear,self.quadratic]

        self.ui = loadUi("ui_main_window.ui",self)        

        # self.line.returnPressed.connect(self.plotter)
        self.ui.combo.currentTextChanged.connect(self.on_combobox_changed)

    def on_combobox_changed(self):
        self.eqn = self.ui.combo.currentIndex()
        self.todo = self.eqn_list[self.eqn-1]
        for i in self.eqn_elt[self.eqn-1]:
            globals()[f"self.button{i}"] = QtWidgets.QDoubleSpinBox()
            self.ui.formLayout.addRow(i, globals()[f"self.button{i}"])
            globals()[f"self.button{i}"].valueChanged.connect(self.todo)

    def linear(self):
        x = np.linspace(float(self.ui.xmin_text.text()),float(self.ui.xmax_text.text()),int(self.ui.steps_text.text()))
        y = float(globals()[f"self.buttona"].text())*x + float(globals()[f"self.buttonb"].text())
        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.plot(x,y)
        self.ui.MplWidget.canvas.draw()

    def quadratic(self):
        x = np.linspace(float(self.ui.xmin_text.text()),float(self.ui.xmax_text.text()),int(self.ui.steps_text.text()))
        y = float(globals()[f"self.buttona"].text())*(x**2) + float(globals()[f"self.buttonb"].text())*x +float(globals()[f"self.buttonc"].text())
        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.plot(x,y)
        self.ui.MplWidget.canvas.draw()

    def plotter(self):
        self.ui.MplWidget.canvas.axes.plot(np.ones(10))
        self.ui.MplWidget.canvas.draw()
        self.button1 = QtWidgets.QPushButton("Button 1")
        self.ui.formLayout.addRow("&Name:", self.button1)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())