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
from PyQt5.QtGui import QPixmap


class load_file(QWidget):                           # <===
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heatmap GUI Help")
        test_label = QLabel("Files")
        self.layout = QFormLayout()
        self.layout.addRow(test_label)
        self.setLayout(self.layout)

class MainGUI():
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        self.app = QApplication([])
        self.mainWindow = self.buildMainWindow()
        self.mainWindow.setWindowTitle('Phindr 3D') #window title

    def buildMainWindow(self):
        """Build the window widget and its components"""
        self.app.main_win = QMainWindow()
        win = QWidget()
        self.app.main_win.setCentralWidget(win)
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignBottom)
        win.setMinimumSize(0, 0)


        # All widgets initialized here, to be placed in their proper section of GUI
        loadmeta = QPushButton("Load MetaData")
        setvoxel = QPushButton("Set Voxel Parameters")
        sv = QCheckBox("SV")
        mv = QCheckBox("MV")
        adjust = QLabel("Adjust Image Threshold") # placeholder for now
        setcolors = QPushButton("Set Channel Colors")
        slicescroll = QLabel("Slice Scroller") # placeholder for now
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here

        # create analysis parameters box (top left box)
        analysisparam = QGroupBox("Analysis Parameters")
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.addWidget(loadmeta, 0, 0, 1, 2)
        grid.addWidget(setvoxel, 1, 0, 1, 2)
        grid.addWidget(sv, 2, 0)
        grid.addWidget(mv, 2, 1)
        grid.addWidget(adjust, 3, 0, 1, 2)
        analysisparam.setLayout(grid)
        analysisparam.setFixedSize(140, 180)
        layout.addWidget(analysisparam, 0, 0)

        # create image viewing parameters box (bottom left box)
        imageparam = QGroupBox("Image Viewing Parameters")
        imageparam.setAlignment(1)
        vertical = QVBoxLayout()
        vertical.addWidget(setcolors)
        vertical.addWidget(slicescroll)
        vertical.addWidget(nextimage)
        imageparam.setLayout(vertical)
        imageparam.setFixedSize(140, 180)
        layout.addWidget(imageparam, 1, 0)

        # Phind button
        layout.addWidget(phind, 2, 0, Qt.AlignCenter)

        # Box for image (?)
        imgwindow = QGroupBox()
        imgwindow.setFlat(True)
        img = QLabel()
        pixmap = QPixmap('C:\Program Files\Git\Phindr3D\phindr3d_icon.png')
        pixmap = pixmap.scaled(400, 400)
        img.setPixmap(pixmap)
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img)
        imgwindow.setLayout(imagelayout)
        imgwindow.setFixedSize(400, 400)
        layout.addWidget(imgwindow, 0, 1, 3, 1)
        win.setLayout(layout)

        loadmeta.clicked.connect(self.file_window_show)
        self.app.aboutToQuit.connect(self.close_windows)
        #win.closeEvent.connect(self.close_windows)
        return win

    def file_window_show(self):
        self.load_file_window = load_file()
        self.load_file_window.show()

    def closeEvent(self):
        print("closevent")
        for window in QApplication.topLevelWidgets():
            window.close()

    def close_windows(self):
        print("closing")
        for window in self.app.topLevelWidgets():
            window.close()

    def run(self):
        """Show the window and run the application exec method to start the GUI"""
        #self.mainWindow.show()
        self.app.main_win.show()
        self.app.exec()

        #self.load_file_window.close()



# end class MainGUI