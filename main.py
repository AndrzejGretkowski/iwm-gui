#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use("Qt5Agg")

import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import numpy as np
import skimage.io as sio
import scipy.interpolate as interpolate
import scipy.ndimage as nd
from bresen import Probe
from emitter_classes import ConeEmitter, ParallelEmitter
import copy
import gc

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def setCustomSize(x, width, height):
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMinimumSize(QtCore.QSize(width, height))
    x.setMaximumSize(QtCore.QSize(width, height))


class CustomWindow(QtWidgets.QMainWindow):
    def __init__(self, emitters, iterations, angle, file):
        super(CustomWindow, self).__init__()
        # Define the geometry of the main window
        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle("Image is being processed... Please wait...")

        # Create FRAME
        self.FRAME = QtWidgets.QFrame(self)
        self.FRAME.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT = QtWidgets.QGridLayout()
        self.FRAME.setLayout(self.LAYOUT)
        self.setCentralWidget(self.FRAME)

        # Create slider
        self.sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl.setMinimum(0)
        self.sl.setMaximum(1000)
        self.sl.setValue(250)
        self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl.setTickInterval(50)

        # Create progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 2 * int(iterations) + 1)
        self.progress.setValue(0)

        self.LAYOUT.addWidget(self.progress, 0, 0, 1, 2)
        self.show()
        app.processEvents()

        # Create button
        self.btnRestart = QtWidgets.QPushButton("Restart animation")
        self.btnRestart.clicked.connect(self.restart)

        # Create line edits
        self.mes_filter = QtWidgets.QLineEdit()
        self.mes_filter.setReadOnly(True)
        self.mes_back = QtWidgets.QLineEdit()
        self.mes_back.setReadOnly(True)

        # Create image containers
        self.sinogram = None
        self.back = []
        self.low = None

        self.sin_count = 0
        self.back_count = 0
        self.emitters = int(emitters)
        self.iterations = int(iterations)
        self.angle = int(angle)
        self.file = file

        # Place the matplotlib figure
        plt.gray()
        self.figure = plt.figure()
        self.figure.patch.set_facecolor(QtGui.QColor(210, 210, 235, 255).name())
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(111)
        self.ax1.set_title("Sinogram")
        self.ax1.set_xlabel("Iteracje")

        self.figure2 = plt.figure()
        self.figure2.patch.set_facecolor(QtGui.QColor(210, 210, 235, 255).name())
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.add_subplot(111)
        self.ax2.set_title("Transformata")

        self.figure3 = plt.figure()
        self.figure3.patch.set_facecolor(QtGui.QColor(210, 210, 235, 255).name())
        self.canvas3 = FigureCanvas(self.figure3)
        self.ax3 = self.figure3.add_subplot(111)
        self.ax3.set_title("Filtr")

        self.display_sin = np.zeros((self.iterations, self.emitters))

        prober = Probe(self.file)
        blackimg = np.zeros(prober.shape())

        self.main_algo(self.file, self.emitters, self.iterations, self.angle)

        self.plt_1 = self.ax1.imshow(self.display_sin, animated=True)
        self.plt_2 = self.ax2.imshow(blackimg, animated=True)
        self.plt_3 = self.ax3.imshow(blackimg, animated=True)
        self.canvas.draw()
        self.canvas2.draw()
        self.canvas3.draw()

        self.progress.setParent(None)
        self.LAYOUT.removeWidget(self.progress)
        self.LAYOUT.addWidget(self.canvas, 1, 0)
        self.LAYOUT.addWidget(self.canvas2, 1, 1)
        self.LAYOUT.addWidget(self.canvas3, 1, 2)
        self.LAYOUT.addWidget(self.sl, 0, 0, 1, 3)
        self.LAYOUT.addWidget(self.btnRestart, 2, 0)
        self.LAYOUT.addWidget(self.mes_back, 2, 1)
        self.LAYOUT.addWidget(self.mes_filter, 2, 2)

        app.processEvents()

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_plot)

        self.setWindowTitle("Image is being displayed...")

        self.timer.start(self.sl.value())

    def restart(self):
        prober = Probe(self.file)
        blackimg = np.zeros(prober.shape())
        self.display_sin = np.zeros((self.iterations, self.emitters))
        self.plt_1.set_data(self.display_sin)
        self.plt_2.set_data(blackimg)
        self.plt_3.set_data(blackimg)
        self.plt_1.autoscale()
        self.plt_2.autoscale()
        self.plt_3.autoscale()
        self.canvas.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        self.sin_count = 0
        self.back_count = 0
        self.timer.start(self.sl.value())

    def update_plot(self):
        if self.sin_count < self.sinogram.shape[0]:
            self.display_sin[:, self.sin_count] = self.sinogram[:, self.sin_count]
            self.plt_1.set_data(self.display_sin)
            self.plt_1.autoscale()
            self.canvas.draw()
            self.sin_count += 1
            self.timer.start(self.sl.value())

        elif self.back_count < len(self.back):
            new_data = self.back[self.back_count]
            self.plt_2.set_data(new_data)
            self.plt_2.autoscale()
            self.canvas2.draw()
            self.back_count += 1
            self.timer.start(self.sl.value())

        else:
            self.plt_3.set_data(self.low)
            self.plt_3.autoscale()
            self.canvas3.draw()

    def main_algo(self, filename, emitter_count, iteration_count, angle):
        prober = Probe(filename)
        # print(prober.shape())
        emitter = ParallelEmitter(prober.shape(), emitter_count, angle, iteration_count)
        sinogram = np.zeros([iteration_count, emitter_count])

        for index, (sp, ep) in enumerate(emitter):
            result = prober.probe(sp, ep)
            # sinogram[index & 511][index >> 9] = 1 - np.exp(-result)
            sinogram[index % iteration_count][index // emitter_count] = 1 - np.exp(-result)

            if index % emitter_count == 0:
                # print(index)
                self.progress.setValue(self.progress.value() + 1)
                app.processEvents()

        sinogram = normalize(sinogram)
        self.sinogram = sinogram

        sio.imsave('sin.png', sinogram)

        # inv_emit = ParallelEmitter(sinogram.shape, emitter_count, angle, iteration_count)
        # out = np.zeros(sinogram.shape, dtype=np.float64)
        #
        # for index, (sp, ep) in enumerate(inv_emit):
        #     prober.raycast(out, sinogram[index % iteration_count][index // emitter_count], sp, ep)
        #
        #     if index % emitter_count == 0:
        #         self.back.append(copy.deepcopy(out))
        #         self.progress.setValue(self.progress.value() + 1)
        #         app.processEvents()

        angles = np.linspace(0, np.pi, emitter_count)
        size = sinogram.shape[0]
        x = np.linspace(-size / 2, size / 2, size, endpoint=False)
        out = np.zeros((size, size), dtype=np.float64)
        vx, vy = np.meshgrid(x, x)

        for index, a in enumerate(angles):
            interp = interpolate.interp1d(x, sinogram[:, index], fill_value=0, copy=False, bounds_error=False)
            xd = vx * np.cos(a) + vy * np.sin(a)
            ar = interp(xd)
            out += ar

            self.back.append(copy.deepcopy(out))
            self.progress.setValue(self.progress.value() + 1)
            app.processEvents()

        # highpass filter
        self.low = out - nd.gaussian_filter(out, 3)
        self.progress.setValue(self.progress.value() + 1)
        app.processEvents()

        sio.imsave('back.png', normalize(out - self.low))


class PickMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(PickMainWindow, self).__init__()

        # Define the geometry of the main window
        # self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle("Choose your options")

        # Create FRAME_A
        self.FRAME = QtWidgets.QFrame(self)
        self.FRAME.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT = QtWidgets.QGridLayout()
        self.FRAME.setLayout(self.LAYOUT)
        self.setCentralWidget(self.FRAME)

        # Create line edits
        self.onlyInts = QtGui.QIntValidator()
        self.onlyDoubles = QtGui.QDoubleValidator()
        self.onlyDoubles.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.onlyInts.setRange(1, 2048)
        self.onlyDoubles.setRange(0, 180, 2)

        self.emitLbl = QtWidgets.QLabel('Emitter count')
        self.emitEdt = QtWidgets.QLineEdit()

        self.emitLbl.setBuddy(self.emitEdt)
        self.emitEdt.setValidator(self.onlyInts)

        self.iterLbl = QtWidgets.QLabel('Iteration count')
        self.iterEdt = QtWidgets.QLineEdit()

        self.iterLbl.setBuddy(self.iterEdt)
        self.iterEdt.setValidator(self.onlyInts)

        self.angleLbl = QtWidgets.QLabel('Emitters angle')
        self.angleEdt = QtWidgets.QLineEdit()

        self.angleLbl.setBuddy(self.angleEdt)
        self.angleEdt.setValidator(self.onlyDoubles)

        self.fileEdt = QtWidgets.QLineEdit()
        self.fileEdt.setReadOnly(True)

        self.LAYOUT.addWidget(self.emitLbl, 0, 1)
        self.LAYOUT.addWidget(self.emitEdt, 0, 0)

        self.LAYOUT.addWidget(self.iterLbl, 1, 1)
        self.LAYOUT.addWidget(self.iterEdt, 1, 0)

        self.LAYOUT.addWidget(self.angleLbl, 2, 1)
        self.LAYOUT.addWidget(self.angleEdt, 2, 0)

        self.LAYOUT.addWidget(self.fileEdt, 3, 0)

        # Create file picker
        self.fileDlg = QtWidgets.QFileDialog()
        self.fileDlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.fileDlg.setNameFilter("Images (*.jpg *.png)")
        self.fileDlg.setWindowTitle("Pick the image")

        # Create buttons
        self.tryBtn = QtWidgets.QPushButton('Process')
        self.tryBtn.clicked.connect(self.tryBtnAction)

        self.fileBtn = QtWidgets.QPushButton('Pick file')
        self.fileBtn.clicked.connect(self.fileBtnAction)

        self.LAYOUT.addWidget(self.tryBtn, 4, 0, 1, 2)
        self.LAYOUT.addWidget(self.fileBtn, 3, 1)

        self.anotherWindow = None

    def tryBtnAction(self):
        if self.anotherWindow is not None:
            self.anotherWindow.close()
            self.anotherWindow.deleteLater()
            app.processEvents()
        self.anotherWindow = None
        emitters = str(self.emitEdt.text())
        iterations = str(self.iterEdt.text())
        angle = str(self.angleEdt.text())
        file = str(self.fileEdt.text())
        gc.collect()

        self.anotherWindow = CustomWindow(emitters, iterations, angle, file)

    def fileBtnAction(self):
        # fileName = self.fileDlg.getOpenFileName(self, "Open File","","Images (*.png *.jpg)");
        if self.fileDlg.exec_():
            self.fileEdt.setText(self.fileDlg.selectedFiles()[0])


def normalize(a):
    max_el = np.max(a)
    min_el = np.min(a)

    return (a - min_el) / (max_el - min_el)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    myGUI = PickMainWindow()
    myGUI.show()

    sys.exit(app.exec_())
