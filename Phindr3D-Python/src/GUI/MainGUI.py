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

from .external_windows import *
from .analysis_scripts import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
import matplotlib.colors as mcolors
import pandas as pd
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.spatial import distance
import numpy as np
from PIL import Image, ImageColor
from PIL import Image
import sys
import os
from pathlib import Path
import random


class MainGUI(QWidget):
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        QMainWindow.__init__(self)
        super(MainGUI, self).__init__()
        self.foundMetadata = False
        self.metadata_file=False
        self.setWindowTitle("Phindr3D")

        self.image_grid=0
        self.rgb_img=[]
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignBottom)

        # All widgets initialized here, to be placed in their proper section of GUI
        loadmeta = QPushButton("Load MetaData")
        setvoxel = QPushButton("Set Voxel Parameters")
        sv = QCheckBox("SV")
        mv = QCheckBox("MV")

        adjust = QLabel("Adjust Image Threshold")
        adjustbar = QSlider(Qt.Horizontal)
        setcolors = QPushButton("Set Channel Colors")
        slicescroll = QLabel("Slice Scroller")
        slicescrollbar = QSlider(Qt.Horizontal)
        previmage = QPushButton("Prev Image")
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here
        def metadataError(buttonPressed):
            if not self.foundMetadata:
                alert = self.buildErrorWindow("Metadata not found!!", QMessageBox.Critical)
                alert.exec()
            elif buttonPressed == "Set Voxel Parameters":
                winp = paramWindow()
                winp.show()
                winp.exec()

        def exportError():
            if not self.foundMetadata:
                alert = self.buildErrorWindow("No variables to export!!", QMessageBox.Critical)
                alert.exec()

        # metadataError will check if there is metadata. If there is not, create error message.
        # Otherwise, execute button behaviour, depending on button (pass extra parameter to
        # distinguish which button was pressed into metadataError()?)
        setvoxel.clicked.connect(lambda: metadataError("Set Voxel Parameters"))
        sv.clicked.connect(lambda: metadataError("SV"))
        mv.clicked.connect(lambda: metadataError("MV"))
        adjustbar.valueChanged.connect(lambda: metadataError("Adjust Image Threshold"))
        setcolors.clicked.connect(lambda: metadataError("Set Channel Colors"))
        slicescrollbar.valueChanged.connect(lambda: metadataError("Slice Scroll"))
        #slicescrollbar.valueChanged.connect(lambda: metadataError("Slice Scroll"))
        nextimage.clicked.connect(lambda: metadataError("Next Image"))
        phind.clicked.connect(lambda: metadataError("Phind"))
        # QScrollBar.valueChanged signal weird, one tap would cause the signal to repeat itself
        # multiple times, until slider reached one end. Thus, changed QScrollBar to QSlider.

        # Declaring menu actions, to be placed in their proper section of the menubar
        menubar = QMenuBar()

        file = menubar.addMenu("File")
        imp = file.addMenu("Import")
        impsession = imp.addAction("Session")
        impparameters = imp.addAction("Parameters")
        exp = file.addMenu("Export")
        expsessions = exp.addAction("Session")
        expparameters = exp.addAction("Parameters")

        metadata = menubar.addMenu("Metadata")
        createmetadata = metadata.addAction("Create Metafile")
        loadmetadata = metadata.addAction("Load Metadata")

        imagetab = menubar.addMenu("Image")
        imagetabnext = imagetab.addAction("Next Image")
        imagetabcolors = imagetab.addAction("Set Channel Colors")

        viewresults = menubar.addAction("View Results")

        about = menubar.addAction("About")

        # Testing purposes
        test = menubar.addMenu("Test")
        switchmeta = test.addAction("Switch Metadata")
        switchmeta.setCheckable(True)

        # Menu actions defined here
        def extractMetadata():
            winz = extractWindow()
            winz.show()
            winz.exec()

        def viewResults():
            winc = resultsWindow()
            winc.show()
            winc.exec()

        # Function purely for testing purposes, this function will switch 'foundMetadata' to true or false
        def testMetadata():
            self.foundMetadata = not self.foundMetadata

        createmetadata.triggered.connect(extractMetadata)
        viewresults.triggered.connect(viewResults)
        imagetabnext.triggered.connect(metadataError)
        imagetabcolors.triggered.connect(metadataError)
        expsessions.triggered.connect(exportError)
        expparameters.triggered.connect(exportError)
        about.triggered.connect(self.aboutAlert)

        switchmeta.triggered.connect(testMetadata)
        # Creating and formatting menubar
        layout.addWidget(menubar)

        # create analysis parameters box (top left box)
        analysisparam = QGroupBox("Analysis Parameters")
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.addWidget(loadmeta, 0, 0, 1, 2)
        grid.addWidget(setvoxel, 1, 0, 1, 2)
        grid.addWidget(sv, 2, 0)
        grid.addWidget(mv, 2, 1)
        grid.addWidget(adjust, 3, 0, 1, 2)
        grid.addWidget(adjustbar, 4, 0, 1, 2)
        analysisparam.setLayout(grid)
        analysisparam.setFixedSize(140, 180)
        layout.addWidget(analysisparam, 1, 0)

        # create image viewing parameters box (bottom left box)
        imageparam = QGroupBox("Image Viewing Parameters")
        imageparam.setAlignment(1)
        vertical = QFormLayout()
        vertical.addRow(setcolors)
        vertical.addRow(slicescroll)
        vertical.addRow(slicescrollbar)
        image_selection = QHBoxLayout()
        image_selection.addWidget(previmage)
        image_selection.addWidget(nextimage)
        vertical.addRow(image_selection)
        imageparam.setLayout(vertical)
        imageparam.setFixedSize(140, 180)
        layout.addWidget(imageparam, 2, 0)

        imageparam.setFixedSize(imageparam.minimumSizeHint())
        analysisparam.setFixedSize(analysisparam.minimumSizeHint())
        analysisparam.setFixedWidth(imageparam.minimumWidth())

        # Phind button
        layout.addWidget(phind, 3, 0, Qt.AlignCenter)

        # Box for image (?)
        imgwindow = QGroupBox()
        imgwindow.setFlat(True)

        '''
        img = QLabel()
        # Set image to whatever needs to be displayed (temporarily set as icon for testing purposes)
        pixmap = QPixmap('C:\Program Files\Git\Phindr3D\phindr3d_icon.png')
        imgdimension = imageparam.height() + analysisparam.height()
        pixmap = pixmap.scaled(imgdimension, imgdimension)
        img.setPixmap(pixmap)
        '''
        matplotlib.use('Qt5Agg')

        img_plot = MplCanvas(self, width=2160*0.0104166667, height=2160*0.0104166667, dpi=300, projection="2d")
        img_plot.axes.imshow(np.zeros((1000,1000)), cmap = mcolors.ListedColormap("black"))
        img_plot.fig.set_facecolor("black")
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img_plot)
        imgwindow.setLayout(imagelayout)
        imgwindow.setFixedSize(400, 400)
        layout.addWidget(imgwindow, 1, 1, 3, 1)
        self.setLayout(layout)

        #mainGUI buttons clicked
        loadmeta.clicked.connect(lambda: self.file_window_show(sv, mv, adjustbar, slicescrollbar, img_plot))
        #if self.foundMetadata:
        nextimage.clicked.connect(lambda: slicescrollbar.setValue(int(slicescrollbar.value())+1))
        previmage.clicked.connect(lambda: slicescrollbar.setValue(int(slicescrollbar.value())-1) if int(slicescrollbar.value())>0 else None)
        #slicescrollbar.valueChanged.connect(lambda: self.scroll_index(slicescrollbar, img_plot))
        slicescrollbar.valueChanged.connect(lambda: self.img_display(slicescrollbar, img_plot, sv, mv))
        #TEMPORARY PARAMS!!!!!
        class params(object):
                tileX = 10
                tileY = 10
                megaVoxelTileX = 5
                megaVoxelTileY = 5
        param=params()
        sv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.image_grid, param, sv, mv, 'SV'))
        mv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.image_grid, param, mv, sv, 'MV'))

    def overlay_display(self, img_plot, img_grid, params, checkbox_cur, checkbox_prev, type):
        if self.foundMetadata:
            img_plot.axes.clear()
            for i in range(3):
                alpha = 1
                if i > 0:
                    alpha = 0.7
                img_plot.axes.imshow(self.rgb_img[:, :, :, i], alpha=alpha)
            if checkbox_cur.isChecked():
                checkbox_prev.setChecked(False)
                overlay=getImageWithSVMVOverlay(img_grid, params, type)
                img_plot.axes.imshow(overlay, zorder=5, cmap=mcolors.ListedColormap('#FFFFFF'), alpha=0.5)
            img_plot.draw()
    def img_display(self, slicescrollbar, img_plot, sv, mv):

        if self.foundMetadata:
            data = pd.read_csv(self.metadata_file, sep="\t")
            chan_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
            #files = [x for x in os.listdir("/data/home/kjok/phindr/Phindr3D/Phindr3D-Python/src/" + "test_img") if
                     Path("/data/home/kjok/phindr/Phindr3D/Phindr3D-Python/src/" + "test_img", x).is_file()]
            slicescrollbar.setMinimum(0)
            slicescrollbar.setMaximum((data.shape[0]-1)/(chan_len-1))
            rgb_img=[]
            keys, values = zip(*mcolors.CSS4_COLORS.items())
            color=random.sample(range(0,len(keys)-1), 3)
            #for ind, color in zip(range(int(slicescrollbar.value()) * 3, int(slicescrollbar.value()) * 3 + 3),color):
            for ind, color in zip(range(int(slicescrollbar.value())*chan_len, int(slicescrollbar.value())*chan_len + chan_len), color):
                cur_img=np.array(Image.open(
                "/data/home/kjok/phindr/Phindr3D/Phindr3D-Python/src/" + "test_img/" + files[
                    ind]))

                threshold=getImageThreshold(cur_img)
                #print(threshold)
                np.savetxt("/data/home/kjok/t-sample.txt", np.unique(cur_img))
                cur_img[cur_img<threshold]=0
                rgb_color=mcolors.to_rgb(values[color])
                print(keys[color])
                rgb_img.append([[rgb_color if i>0 else (0,0,0) for i in row] for row in cur_img])

            self.rgb_img=np.array(rgb_img).transpose(1,2,3,0)
            #print(np.shape(rgb_img))
            self.image_grid=np.zeros((self.rgb_img.shape[0], self.rgb_img.shape[1], 3))
            img_plot.axes.clear()
            for i in range(3):
                alpha=1
                if i>0:
                    alpha=0.7
                img_plot.axes.imshow(self.rgb_img[:,:,:,i], alpha=alpha)
            img_plot.axes.set_position([0, 0, 1, 1])
            img_plot.draw()
            sv.setChecked(False)
            mv.setChecked(False)

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def aboutAlert(self):
        alert = QMessageBox()
        alert.setText("talk about the program")
        alert.setWindowTitle("About")
        alert.exec()

    def file_window_show(self, sv, mv, adjustbar, slicescrollbar, img_plot):
        self.metadata_file = str(QFileDialog.getOpenFileName(self, 'Select tractography file')[0])
        if self.metadata_file and self.metadata_file.rsplit('.', 1)[-1]=="txt":
            print(self.metadata_file)
            self.foundMetadata=True#temp
            adjustbar.setValue(0)
            slicescrollbar.setValue(0)
            self.img_display(slicescrollbar, img_plot, sv, mv)
        else:
            load_metadata_win=self.buildErrorWindow("Select Valid Metadatafile (.txt)", QMessageBox.Critical)
            load_metadata_win.exec()

    def closeEvent(self, event):
        print("closed all windows")
        for window in QApplication.topLevelWidgets():
            window.close()

def run_mainGUI():
    """Show the window and run the application exec method to start the GUI"""
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    app.exec()

# end class MainGUI