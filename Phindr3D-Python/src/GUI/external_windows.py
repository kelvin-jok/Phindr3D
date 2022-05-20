# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.spatial import distance
import numpy as np
from PIL import Image
import sys

#Matplotlib Figure and Interactive Mouse-Click Callback Classes
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class interactive_points(object):
    def __init__(self, xdata, ydata, sc):
        self.xdata=xdata
        self.ydata=ydata
        self.scbounds=sc

        class buildImageViewer(QWidget):
            def __init__(self):
                super().__init__()
                self.resize(1000, 1000)
                self.setWindowTitle("ImageViewer")
                grid = QGridLayout()

                #info layout
                info_box = QVBoxLayout()
                file_info=QLineEdit("FileName:\n")
                file_info.setAlignment(Qt.AlignTop)
                file_info.setReadOnly(True)
                ch_info=QLineEdit("Channels\n")
                ch_info.setAlignment(Qt.AlignTop)
                ch_info.setReadOnly(True)
                file_info.setFixedWidth(200)
                file_info.setMinimumHeight(350)
                ch_info.setFixedWidth(200)
                ch_info.setMinimumHeight(350)
                info_box.addStretch()
                info_box.addWidget(file_info)
                info_box.addWidget(ch_info)
                info_box.addStretch()

                #projection layout
                pjt_box = QGroupBox("Projection Type")
                pjt_type= QHBoxLayout()
                slice_btn = QRadioButton("Slice")
                mit_btn = QRadioButton("MIT")
                montage_btn = QRadioButton("Montage")
                pjt_type.addStretch()
                pjt_type.addWidget(slice_btn)
                pjt_type.addWidget(mit_btn)
                pjt_type.addWidget(montage_btn)
                pjt_type.addStretch()
                pjt_type.setSpacing(100)
                pjt_box.setLayout(pjt_type)

                #image plot layout
                matplotlib.use('Qt5Agg')

                x = []
                y = []
                # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
                # x=
                # y=
                main_plot = MplCanvas(self, width=12, height=12, dpi=100)
                main_plot.fig.set_facecolor('#f0f0f0')
                main_plot.axes.scatter(x, y)
                main_plot.axes.get_xaxis().set_visible(False)
                main_plot.axes.get_yaxis().set_visible(False)

                # adjustbar layout
                adjustbar = QSlider(Qt.Vertical)
                adjustbar.setFixedWidth(50)
                adjustbar.setStyleSheet(
                    "QSlider::groove:vertical {background-color: #8DE8F6; border: 1px solid;height: 700px;margin: 0px;}"
                    "QSlider::handle:vertical {background-color: #8C8C8C; border: 1px silver; height: 30px; width: 10px; margin: -5px 0px;}")

                #parent layout
                grid.addLayout(info_box, 0, 0)
                grid.addWidget(main_plot, 0, 1)
                grid.addWidget(pjt_box, 1, 1, Qt.AlignCenter)
                grid.addWidget(adjustbar, 0, 2)

                self.setLayout(grid)

        self.winc = buildImageViewer()

    def __call__(self, event):

        #for debugging
        '''
        if event.button is MouseButton.LEFT:
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                      ('double' if event.dblclick else 'single', event.button,
                       event.x, event.y, event.xdata, event.ydata))
        '''

        if event.inaxes is not None:
            #find x & y axis tolerance
            xlim=self.scbounds.axes.get_xlim()
            ylim=self.scbounds.axes.get_ylim()
            xtol=0.015*abs(abs(xlim[0])-abs(xlim[1]))+np.exp(-(abs(abs(xlim[0])-abs(xlim[1]))/500))/50
            ytol=0.015*abs(abs(ylim[0])-abs(ylim[1]))+np.exp(-(abs(abs(ylim[0])-abs(ylim[1]))/500))/50

            #when clicked locate closest data point
            pt_closest= distance.cdist([(event.xdata,event.ydata)], list(zip(self.xdata,self.ydata))).argmin()
            xclose=self.xdata[pt_closest]
            yclose=self.ydata[pt_closest]

            #create pop-up figure and plot if clicked data point within tolerance
            plt.figure(1)

            if xclose-xtol < event.xdata < xclose+xtol and yclose-ytol < event.ydata < yclose+ytol:
                winc=self.winc
                winc.show()