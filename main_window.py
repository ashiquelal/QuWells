
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
import scipy.linalg as la
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
        self.eqn_elt = [['w'],['Number of wells','width','depth'],["Angular frequency","Dissociation energy"],["Frequency"],["Distance at which potential is minimum","Magnitude of minimum potential"]]
        self.eqn_list = [self.linear,self.finite,self.morse,self.harmonic,self.lennard]

        self.ui = loadUi("ui_main_window.ui",self)        

        # self.line.returnPressed.connect(self.plotter)
        self.on_combobox_changed()
        self.ui.combo.currentTextChanged.connect(self.on_combobox_changed)

                # plot
        self.plotWidget = FigureCanvas()
        lay = QtWidgets.QVBoxLayout()  
        lay.setContentsMargins(0, 0, 0, 0)      
        lay.addWidget(self.plotWidget)

    def cnct(self,elt,fun=""):
        try:
            elt.disconnect()
        except TypeError:
            pass
        if fun!="":
            elt.connect(fun)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def on_combobox_changed(self):
        self.clearLayout(self.ui.formLayout)
        self.eqn = self.ui.combo.currentIndex()
        self.todo = self.eqn_list[self.eqn]
        
        
        self.cnct(self.ui.steps_text.valueChanged)
        self.cnct(self.ui.n_text.valueChanged)
        self.cnct(self.ui.wave_radio.toggled,lambda : self.todo(calc=False))


        for i in range(len(self.eqn_elt[self.eqn])):

            if i==0 and self.eqn==1:
                globals()[f"self.button{i}"] = QtWidgets.QSpinBox()
                label = QtWidgets.QLabel()
                label.setText(self.eqn_elt[self.eqn][i])
                label.setWordWrap(True)
                self.ui.formLayout.addRow(label, globals()[f"self.button{i}"])
                globals()[f"self.button{i}"].setMinimum(1)
                self.cnct(globals()[f"self.button{i}"].valueChanged,lambda : self.well_inputs())
            else:
                globals()[f"self.button{i}"] = QtWidgets.QDoubleSpinBox()
                label = QtWidgets.QLabel()
                label.setText(self.eqn_elt[self.eqn][i])
                label.setWordWrap(True)
                self.ui.formLayout.addRow(label, globals()[f"self.button{i}"])
                globals()[f"self.button{i}"].setMinimum(1)
                globals()[f"self.button{i}"].setSingleStep(0.1)
                self.cnct(globals()[f"self.button{i}"].valueChanged,lambda : self.todo())

    def well_inputs(self):
        n = int(globals()[f"self.button0"].text())
        # print(n)
        elt = ["separatuion ","width" , "depth "]
        for i in range(4,self.ui.formLayout.rowCount()):
            self.ui.formLayout.removeRow(4)
            try:
                globals().pop(f"self.button{i-1}")
            except KeyError:
                print("tried to delete wrong button")
        
        counter = 3
        if n>1:
            for i in range(2,n+1):
                for j in range(len(elt)):
                    globals()[f"self.button{counter}"] = QtWidgets.QDoubleSpinBox()
                    globals()[f"self.button{counter}"].setMinimum(1)
                    globals()[f"self.button{counter}"].setSingleStep(0.1)
                    self.ui.formLayout.addRow(elt[j]+" "+str(i), globals()[f"self.button{counter}"])
                    self.cnct(globals()[f"self.button{counter}"].valueChanged,lambda : self.todo())
                    counter+=1
            globals()[f"self.button{counter}"] = QtWidgets.QCheckBox()
            self.ui.formLayout.addRow("Calculate", globals()[f"self.button{counter}"])
        # self.cnct(globals()[f"self.button{counter}"].valueChanged,lambda : self.todo())




    def lapst(self,k,del_x):
        lap = (-30*np.diag(np.ones(k)) + 16*np.diag(np.ones(k-1),1) +16*np.diag(np.ones(k-1),-1)-np.diag(np.ones(k-2),-2)-np.diag(np.ones(k-2),2))/(12*(del_x)**2)
        return lap


    def linear(self,calc = True):
        if calc==True:
            w = float(globals()[f"self.button0"].text())
            
            self.k = int(self.ui.steps_text.text())
            self.w=w/2	
            self.xvec = np.linspace(-w,w,self.k)		 							# Defining the space
            self.del_x = self.xvec[1] - self.xvec[0]
            lap = self.lapst(self.k,self.del_x)											# Calling Laplacian operator defined earlier
            h =-(0.5) * lap											# Hamiltonian in hartree atomic units
            self.e,self.v = la.eigh(h)											# Diagonalizing hamiltonian to get energy eigenvalues(e) and corresponding eigen functions(v)
        k = self.k
        w = self.w
        xvec = self.xvec
        e = self.e
        v = self.v
        if self.ui.wave_radio.isChecked():
            v = v
        else :
            v = v*v

        edif = e[1] - e[0]											# Scaling the wavefunction
        maxv0 = np.amax(v)

        v = (v*edif)/(2*maxv0)
        
        self.ui.MplWidget.canvas.axes.clear()
        n = int(self.ui.n_text.text())
        for i in np.arange(n-1,-1,-1):
            self.ui.MplWidget.canvas.axes.plot(xvec,v[:,i] + e[i],label=  'E(a.u.)={}'.format(np.round(e[i]*1000)/1000.0))		# The wavefunction is shifted towards their energy value for ease of interpreting
            plt.axhline(v[0,i] + e[i],-2*w,2*w, ls =   '--')
        self.ui.MplWidget.canvas.draw()

        self.cnct(self.ui.steps_text.valueChanged,lambda : self.todo())
        self.cnct(self.ui.n_text.valueChanged,lambda : self.todo(calc=False))
        

    def finite(self,calc=True):
        d = 0

        for i in range(1,self.ui.formLayout.rowCount()-2,3):
            try:
                d+=float(globals()[f"self.button{i}"].text())
            except (RuntimeError, KeyError):
                break
        if int(globals()[f"self.button0"].text())>1:
            for i in range(3,self.ui.formLayout.rowCount()-2,3):
                try:

                    d+=float(globals()[f"self.button{i}"].text())
                except (RuntimeError, KeyError):
                    break
        self.d = 2*d
        self.k = int(self.ui.steps_text.text())
        self.u = [0]*int(np.round((self.d/4)/(self.d/self.k)))
        self.u +=[-1*float(globals()[f"self.button{2}"].text())]*int(np.round((float(globals()[f"self.button{1}"].text()))/(self.d/self.k)))

        if int(globals()[f"self.button0"].text())>1:
            for i in range(5,self.ui.formLayout.rowCount(),3):
                self.u +=[0]*int(np.round((float(globals()[f"self.button{i-2}"].text()))/(self.d/self.k)))
                self.u +=[-1*float(globals()[f"self.button{i}"].text())]*int(np.round((float(globals()[f"self.button{i-1}"].text()))/(self.d/self.k)))
        self.u += [0]*(self.k-len(self.u))
        self.xvec = np.linspace(-self.d/2,self.d/2,self.k)
        xvec = self.xvec
        self.ui.MplWidget.canvas.axes.clear()

        calc_wave = False
        try :
            if int(globals()[f"self.button0"].text())>1:
                if globals()[f"self.button{self.ui.formLayout.rowCount()-2}"].isChecked():
                    calc_wave = True
            else:  
                calc_wave = True
            if calc_wave:
                if calc==True:
                    
                    del_x = self.xvec[1] - self.xvec[0]
                    lap = self.lapst(self.k,del_x)
                    h = np.zeros((self.k,self.k))
                    [i,j] = np.indices(h.shape)
                    h[i==j]=self.u
                    h += (-0.5)*lap
                    self.e,self.v = la.eigh(h)
                e = self.e
                v = self.v
                # xvec = self.xvec
                if self.ui.wave_radio.isChecked():
                    v = v
                    if np.abs(np.min(v[:,0]))>np.max(v[:,0]):
                        v = -1*v
                else :
                    v = v*v

                edif = e[1] - e[0]											# Scaling the wavefunction
                maxv0 = np.amax(v)
                v = (v*edif)/(2*maxv0)
                n = int(self.ui.n_text.text())
                for i in np.arange(n-1,-1,-1):
                    self.ui.MplWidget.canvas.axes.plot(xvec,v[:,i] + e[i],label=  'E(a.u.)={}'.format(np.round(e[i]*1000)/1000.0))		# The wavefunction is shifted towards their energy value for ease of interpreting
                    plt.axhline(v[0,i] + e[i],-d/2,d/2, ls =   '--')
                self.ui.MplWidget.canvas.draw()
        except KeyError:
            print("Checkbox index is wrong")

        self.ui.MplWidget.canvas.axes.plot(xvec,self.u)
        self.ui.MplWidget.canvas.draw()
        self.cnct(self.ui.steps_text.valueChanged,lambda : self.todo())

        self.cnct(self.ui.n_text.valueChanged,lambda : self.todo(calc=False))
        pass
    
    def morse(self,calc = True):
        minx = -5
        maxx = 11
        if calc==True:
            o = float(globals()[f"self.button0"].text())
            d = float(globals()[f"self.button1"].text())
            self.k = int(self.ui.steps_text.text())
            
            self.d =d
            a = np.sqrt(o/(2*d))

            self.xvec = np.linspace(minx,maxx,self.k)		 							# Defining the space
            del_x = self.xvec[1] - self.xvec[0]
            self.u = d*(np.exp(-2*a*self.xvec)-2*np.exp(-a*self.xvec))
            lap = self.lapst(self.k,del_x)
            h = np.zeros((self.k,self.k))
            [i,j] = np.indices(h.shape)
            h[i==j]=self.u
            h += (-0.5)*lap									# Hamiltonian in hartree atomic units
            self.e,self.v = la.eigh(h)											# Diagonalizing hamiltonian to get energy eigenvalues(e) and corresponding eigen functions(v)
        k = self.k
        d = self.d
        # w = self.w
        xvec = self.xvec
        e = self.e
        v = self.v
        if self.ui.wave_radio.isChecked():
            v = v   
            if np.abs(np.min(v[:,0]))>np.max(v[:,0]):
                v = -1*v
        else :
            v = v*v

        edif = np.abs(e[1] - e[0])											# Scaling the wavefunction
        maxv0 = np.amax(v)

        v = (v*edif)/(maxv0)
        
        self.ui.MplWidget.canvas.axes.clear()
        n = int(self.ui.n_text.text())
        for i in np.arange(n-1,-1,-1):
            self.ui.MplWidget.canvas.axes.plot(xvec,v[:,i] + e[i],label=  'E(a.u.)={}'.format(np.round(e[i]*1000)/1000.0))		# The wavefunction is shifted towards their energy value for ease of interpreting
            self.ui.MplWidget.canvas.axes.axhline(v[0,i] + e[i],minx,maxx, ls =   '--')

        self.ui.MplWidget.canvas.axes.plot(xvec,self.u)	\
            
        self.ui.MplWidget.canvas.axes.set_xlim(-2,7)
        self.ui.MplWidget.canvas.axes.set_ylim(-d-.5,1)
        self.ui.MplWidget.canvas.draw()

        self.cnct(self.ui.steps_text.valueChanged,lambda : self.todo())
        self.cnct(self.ui.n_text.valueChanged,lambda : self.todo(calc=False))

    def lennard(self):
        pass

    def harmonic(self):
        pass
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())