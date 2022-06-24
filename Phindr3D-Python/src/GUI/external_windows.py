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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler
from ..Data import *
from ..Clustering import *
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
from matplotlib import rcParams, cycler
import matplotlib.colors as mcolors
import pandas as pd
from .analysis_scripts import *
from PIL import Image
from textwrap import wrap, fill
from math import ceil
from more_itertools import locate
import os

#Matplotlib Figure
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection=="3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111, projection=None)
        super(MplCanvas, self).__init__(self.fig)

#imported matplotlib toolbar. Only use desired functions.
class NavigationToolbar(NavigationToolbar):
    NavigationToolbar.toolitems = (
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Customize', 'Edit axis, curve and image parameters', 'qt4_editor_options', 'edit_parameters'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure')
    )

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe
class interactive_points():
    def __init__(self, main_plot, plots, projection, data, labels, feature_file, color, imageID):
        self.main_plot=main_plot
        self.plots=plots
        self.projection=projection
        self.data=data
        self.labels=labels
        self.feature_file=feature_file
        self.color=color
        self.imageID=imageID

    def buildImageViewer(self, x_data, label, cur_label, index, color, feature_file, imageID):

                win = QDialog()
                win.resize(1000, 1000)
                win.setWindowTitle("ImageViewer")
                grid = QGridLayout()

                #info layout
                info_box = QVBoxLayout()
                file_info=QLabel("FileName:")
                file_info.setAlignment(Qt.AlignTop)
                file_info.setStyleSheet("background-color: white")
                file_info.setWordWrap(True)
                ch_info=QLabel("Channels\n")
                ch_info.setAlignment(Qt.AlignTop)
                ch_info.setStyleSheet("background-color: white")
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
                main_plot = MplCanvas(self, width=12, height=12, dpi=100, projection='2d')
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

                win.setLayout(grid)

                self.channel_display(adjustbar, main_plot, color, x_data, label, cur_label, index, feature_file, file_info, ch_info, imageID)
                win.show()
                win.exec()

    def channel_display(self, slicescrollbar, img_plot, color, x, label, cur_label, index, feature_file, file_info, ch_info, imageID):
            if feature_file:
                # extract image details from feature file
                data = pd.read_csv(feature_file[0], sep="\t", na_values='        NaN')
                ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))

                #update info labels
                ch_names = ['<font color= "#' + str('%02x%02x%02x' % (int(color[i-1][0]*255), int(color[i-1][1]*255), int(color[i-1][2]*255))) + '">' + "Channel_" + str(i) + "</font>" for i in
                            range(1, ch_len + 1, 1)]
                ch_names='<br>'.join(ch_names)
                ch_info.setText("Channels<br>"+ch_names)
                slicescrollbar.setMaximum((data.shape[0] - 1))
                if len(self.labels)>1:
                    cur_ind=list(locate(label, lambda x: x==cur_label))[index]
                    cur_ind=imageID[cur_ind]-1
                    slicescrollbar.setValue(cur_ind)
                    file_info.setText("Filename: " + data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[cur_ind])
                else:
                    slicescrollbar.setValue(imageID[index]-1)
                    file_info.setText("Filename: " + data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[index])

                # initialize array as image size with # channels
                rgb_img = Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[slicescrollbar.value()]).size
                rgb_img = np.empty((rgb_img[1], rgb_img[0], 3, ch_len))

                # threshold/colour each image channel
                for ind, rgb_color in zip(range(slicescrollbar.value(), slicescrollbar.value() + ch_len),color):
                    ch_num = str(ind - slicescrollbar.value() + 1)
                    data['Channel_' + ch_num] = data['Channel_' + ch_num].str.replace(r'\\', '/', regex=True)
                    cur_img = np.array(Image.open(data['Channel_' + ch_num].iloc[slicescrollbar.value()]))
                    threshold = getImageThreshold(cur_img)
                    cur_img[cur_img <= threshold] = 0
                    cur_img = np.dstack((cur_img, cur_img, cur_img))
                    rgb_img[:, :, :, int(ch_num) - 1] = cur_img * rgb_color

                # compute average and norm to mix colours
                divisor = np.sum(rgb_img != 0, axis=-1)
                tot = np.sum(rgb_img, axis=-1)
                rgb_img = np.divide(tot, divisor, out=np.zeros_like(tot), where=divisor != 0)
                max_rng = [np.max(rgb_img[:, :, i]) if np.max(rgb_img[:, :, i]) > 0 else 1 for i in range(ch_len)]
                rgb_img = np.divide(rgb_img, max_rng)

                # plot combined channels
                img_plot.axes.clear()
                img_plot.axes.imshow(rgb_img)
                img_plot.draw()

    def __call__ (self, event): #picker is mouse scroll down trigger
        if event.mouseevent.inaxes is not None and event.mouseevent.button=="down":

            #https://github.com/matplotlib/matplotlib/issues/ 19735   ---- code below from github open issue. wrong event.ind coordinate not fixed in current version matplotlib...
            xx = event.mouseevent.x
            yy = event.mouseevent.y
            label = event.artist.get_label()
            label_ind=np.where(np.array(self.labels)==label)
            # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind][0], self.data[1][label_ind][0], self.data[2][label_ind][0], self.main_plot.axes.get_proj())
            x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
            # the distance
            d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)

            # find the closest by searching for min distance.
            # from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            imin = 0
            dmin = 10000000
            for i in range(len(self.data[0][label_ind])):
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind][i], self.data[1][label_ind][i], self.data[2][label_ind][i], self.main_plot.axes.get_proj())
                x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)
                # We find the distance and also the index for the closest datapoint
                if d < dmin:
                    dmin = d
                    imin = i
            self.main_plot.axes.scatter3D(self.data[0][label_ind][imin],
                                        self.data[1][label_ind][imin],
                                        self.data[2][label_ind][imin], s=35, facecolor="none",
                                        edgecolor='gray', alpha=1)

            self.main_plot.draw()
            self.main_plot.figure.canvas.draw_idle()
            self.buildImageViewer(self.data[0],self.labels,label, imin,self.color,self.feature_file, self.imageID)

class featurefilegroupingWindow(object):
    def __init__(self, columns, groupings):
        win = QDialog()
        win.setWindowTitle("Filter Feature File Groups and Channels")
        win.setLayout(QFormLayout())

        grp_title = QLabel("Grouping")
        grp_title.setFont(QFont('Arial', 10))
        grp_checkbox=QGroupBox()
        grp_checkbox.setFlat(True)
        grp_list=[]
        grp_vbox = QVBoxLayout()
        grp_vbox.addWidget(grp_title)

        ch_title = QLabel("Channels")
        ch_title.setFont(QFont('Arial', 10))
        ch_checkbox=QGroupBox()
        ch_checkbox.setFlat(True)
        ch_vbox = QVBoxLayout()
        ch_vbox.addWidget(ch_title)

        for i in range (len(columns)):
            if columns[i].find("Channel_")== 0:
                ch_label=QLabel(columns[i])
                ch_vbox.addWidget((ch_label))
            elif columns[i][:2].find("MV")== -1:
                grp_list.append(QCheckBox(columns[i]))
                grp_vbox.addWidget(grp_list[-1])

        grp_vbox.addStretch(1)
        grp_checkbox.setLayout(grp_vbox)

        ch_vbox.addStretch(1)
        ch_checkbox.setLayout(ch_vbox)

        win.layout().addRow(grp_checkbox, ch_checkbox)

        ok_button=QPushButton("OK")
        win.layout().addRow(ok_button)
        ok_button.clicked.connect(lambda :self.selected(grp_checkbox, win, groupings))

        win.show()
        win.exec()

    def selected(self, grp_checkbox, win, groupings):
        for checkbox in grp_checkbox.findChildren(QCheckBox):
            #print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked():
                groupings.append(checkbox.text())
        win.close()

class extractWindow(QDialog):
    def __init__(self):
        super(extractWindow, self).__init__()
        largetext = QFont("Arial", 12, 1)
        self.setWindowTitle("Extract Metadata")
        directory = "Image Root Directory"
        self.samplefilename = "Sample File Name"
        layout = QGridLayout()
        imagerootbox = QTextEdit()
        imagerootbox.setReadOnly(True)
        imagerootbox.setPlaceholderText(directory)
        imagerootbox.setFixedSize(300, 60)
        imagerootbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        imagerootbox.setFont(largetext)

        selectimage = QPushButton("Select Image Directory")
        selectimage.setFixedSize(selectimage.minimumSizeHint())
        selectimage.setFixedHeight(40)

        samplefilebox = QTextEdit()
        samplefilebox.setReadOnly(True)
        samplefilebox.setPlaceholderText(self.samplefilename)
        samplefilebox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        samplefilebox.setFont(largetext)
        samplefilebox.setFixedSize(450, 30)

        expressionbox = QLineEdit()
        expressionbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        expressionbox.setFont(largetext)
        expressionbox.setFixedSize(450, 30)
        expressionbox.setPlaceholderText("Type Regular Expression Here")

        evaluateexpression = QPushButton("Evaluate Regular Expression")
        evaluateexpression.setFixedSize(evaluateexpression.minimumSizeHint())
        evaluateexpression.setFixedHeight(30)

        outputfilebox = QLineEdit()
        outputfilebox.setAlignment(Qt.AlignCenter)
        outputfilebox.setFont(largetext)
        outputfilebox.setPlaceholderText("Output Metadata File Name")
        outputfilebox.setFixedSize(200, 30)

        createfile = QPushButton("Create File")
        createfile.setFixedSize(createfile.minimumSizeHint())
        createfile.setFixedHeight(30)

        cancel = QPushButton("Cancel")
        cancel.setFixedSize(cancel.minimumSizeHint())
        cancel.setFixedHeight(30)

        # button functions
        def selectImageDir():
            imagedir = QFileDialog.getExistingDirectory()
            if not os.path.exists(imagedir):
                return
            imagerootbox.setText(imagedir)
            # select first '.tif' or '.tiff' file to be sample file
            for file in os.listdir(imagedir):
                if file.endswith('.tiff') or file.endswith('.tif'):
                    samplefilebox.setText(file)
                    break
        def createFile():
            imagedir = imagerootbox.toPlainText()
            regex = expressionbox.text()
            outputname = outputfilebox.text()
            # replace '?<' patterns with '?P<' to make compatible with re.fullmatch function
            # first checks if '?<' corresponds to a '?<=' or '?<!' pattern first before replacing
            # part of Python specific regular expression syntax
            regex = DataFunctions.regexPatternCompatibility(regex)
            try:
                alert = QMessageBox()
                try:
                    if outputname != "":
                        created = DataFunctions.createMetadata(imagedir, regex, outputname)
                    else:
                        created = DataFunctions.createMetadata(imagedir, regex)
                    if created:
                        alert.setText("Metadata creation success.")
                        alert.setIcon(QMessageBox.Information)
                        alert.setWindowTitle("Notice")
                        self.close()
                    else:
                        alert.setText("Error: No Regex matches found in selected folder.")
                        alert.setIcon(QMessageBox.Critical)
                except MissingChannelStackError:
                    alert.setText("Error: No Channel and/or Stack groups found in regex.")
                    alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()
            except WindowsError:
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText("No such image directory exists.")
                alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()

        def evalRegex():
            regex = expressionbox.text()
            samplefile = samplefilebox.toPlainText()
            if regex == "":
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText("Please enter a regular expression to evaluate")
                alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()
                return
            if samplefile == "":
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText("No sample file was found. Please check the selected image directory.")
                alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()
                return
            # replace '?<' patterns with '?P<' to make compatible with re.fullmatch function
            # first checks if '?<' corresponds to a '?<=' or '?<!' pattern first before replacing
            # part of Python specific regular expression syntax
            regex = DataFunctions.regexPatternCompatibility(regex)
            # parse the sample file with the regular expression to find field values
            reout = DataFunctions.parseAndCompareRegex(samplefile, regex)
            # Create the GUI that displays the output
            winex = QDialog()
            winex.setWindowTitle("Evaluate Regular Expression")
            winlayout = QGridLayout()
            labelText = "Regular Expression Match"
            # List of regex keys and values
            relist = QListWidget()
            if len(reout) == 0:
                relist.addItem("No results")
            else:
                for rekey in reout.keys():
                    nextline = str(rekey)+" ::: "+str(reout[rekey])
                    relist.addItem(nextline)
            # Ok button closes the window
            reok = QPushButton("Ok")
            # button behaviour
            def okPressed():
                winex.close()
            reok.clicked.connect(okPressed)

            # add the widgets to the layout
            winlayout.addWidget(QLabel(labelText))
            winlayout.addWidget(relist)
            winlayout.addWidget(reok)
            # add the layout and show the window
            winex.setLayout(winlayout)
            winex.show()
            winex.exec()
        #end evalRegex

        cancel.clicked.connect(self.close)
        selectimage.clicked.connect(selectImageDir)
        createfile.clicked.connect(createFile)
        evaluateexpression.clicked.connect(evalRegex)

        layout.addWidget(imagerootbox, 0, 0, 1, 2)
        layout.addWidget(selectimage, 0, 2, 1, 1)
        layout.addWidget(samplefilebox, 1, 0, 1, 3)
        layout.addWidget(expressionbox, 2, 0, 1, 3)
        layout.addWidget(evaluateexpression, 3, 0, 1, 1)
        layout.addWidget(outputfilebox, 4, 0, 1, 1)
        layout.addWidget(createfile, 4, 1, 1, 1)
        layout.addWidget(cancel, 4, 2, 1, 1)
        layout.setSpacing(10)
        self.setLayout(layout)
        self.setFixedSize(self.minimumSizeHint())

class resultsWindow(QDialog):
    def __init__(self, color):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
        self.imageIDs=[]
        menubar = QMenuBar()
        file = menubar.addMenu("File")
        inputfile = file.addAction("Input Feature File")
        data = menubar.addMenu("Data Analysis")
        classification = data.addMenu("Classification")
        selectclasses = classification.addAction("Select Classes")
        clustering = data.addMenu("Clustering")
        estimate = clustering.addAction("Estimate Clusters")
        setnumber = clustering.addAction("Set Number of Clusters")
        piemaps = clustering.addAction("Pie Maps")
        export = clustering.addAction("Export Cluster Results")
        plotproperties = menubar.addMenu("Plot Properties")
        rotation = plotproperties.addAction("3D Rotation")
        reset_action = QAction("Reset Plot View", self)
        reset_action.triggered.connect(lambda: self.reset_view())
        resetview = plotproperties.addAction(reset_action)

        # menu features go here

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        map_type = QComboBox()
        map_type.addItem("PCA")
        map_type.addItem("t-SNE")
        map_type.addItem("Sammon")
        twod = QCheckBox("2D")
        threed = QCheckBox("3D")
        dimensionbox = QGroupBox()
        dimensionboxlayout = QHBoxLayout()
        dimensionboxlayout.addWidget(twod)
        dimensionboxlayout.addWidget(threed)
        dimensionbox.setLayout(dimensionboxlayout)
        colordropdown = QComboBox()
        boxlayout.addWidget(selectfile, 0, 0, 3, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(map_type, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        self.plot_data=[]
        self.labels=[]
        self.plots=[]
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)#, picker=True)
        self.main_plot.axes.set_position([-0.25, 0.1, 1, 1])
        if not self.plot_data:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim=[0,0]
        self.original_ylim=[0,0]
        self.original_zlim=sc_plot.axes.get_zlim3d()

        self.projection = "2d"  # update from radiobutton
        def axis_limit(sc_plot):
            xlim = sc_plot.axes.get_xlim3d()
            ylim = sc_plot.axes.get_ylim3d()
            lower_lim=min(xlim[0], ylim[0])
            upper_lim=max(xlim[1], ylim[1])
            return(lower_lim, upper_lim)
        def toggle_2d_3d(data, sc_plot, checkbox_cur, checkbox_prev, dim, plot):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(data, sc_plot, dim, plot)
        def check_projection(data, sc_plot, dim, plot):
            if dim == "2d":
                self.projection=dim
                low, high= axis_limit(sc_plot)
                #for debugging
                #print(low, high)
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=-90)
                if self.feature_file!=[]:
                    self.original_xlim=[low-1, high+1]
                    self.original_ylim=[low - 1, high + 1]
                    self.main_plot.axes.set_xlim(low-1, high+1)
                    self.main_plot.axes.set_ylim(low-1, high+1)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                self.projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.fig.canvas.draw()
                self.main_plot.axes.mouse_init()
            if self.feature_file and colordropdown.count()>0:
                self.data_filt(colordropdown, "False", self.projection, plot, True)

        # button features go here
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText()))
        twod.toggled.connect(lambda: toggle_2d_3d(self.plot_data, sc_plot, twod, threed, "2d", map_type.currentText()))
        threed.toggled.connect(lambda: toggle_2d_3d(self.plot_data, sc_plot, threed, twod, "3d", map_type.currentText()))
        twod.setChecked(True)
        picked_pt=interactive_points(self.main_plot, self.plots, self.projection, self.plot_data, self.labels, self.feature_file, color, self.imageIDs)
        # matplotlib callback mouse/scroller actions
        cid=self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(), False) if self.feature_file and colordropdown.count()>0 else None)
        map_type.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(), True) if self.feature_file and colordropdown.count() > 0 else None)
        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)

        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 600)
        minsize.setWidth(self.minimumSizeHint().width() + 600)
        self.setFixedSize(minsize)
    def reset_view(self):
        self.main_plot.axes.set_xlim3d(self.original_xlim)
        self.main_plot.axes.set_ylim3d(self.original_ylim)
        self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=-90, elev=-90)
        self.main_plot.draw()

    def loadFeaturefile(self, grouping, plot):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file.clear()
            self.feature_file.append(filename)
            print(self.feature_file)

            self.data_filt(grouping, True, "2d", plot, True)
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def data_filt(self, grouping, load, projection, plot, new_plot): #modified from Phindr... implemented PCA ...
        image_feature_data_raw = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        if load==True:
            grouping.blockSignals(True)
            if grouping.count()>1:
                grouping.clear()
            grps=[]
            featurefilegroupingWindow(image_feature_data_raw.columns, grps)
            grouping.addItem("No Grouping")
            #grouping.setCurrentIndex(0)
            for col in grps:
                grouping.addItem(col)
            grouping.blockSignals(False)
        filter_data= grouping.currentText()

        # rescale texture features to the range [0, 1]
        rescale_texture_features = False

        # choose dataset to use for clustering: EDIT HERE
        # Choices:
        # 'MV' -> megavoxel frequencies,
        # 'text' -> 4 haralick texture features,
        # 'combined' -> both together
        datachoice = 'MV'
        image_feature_data = image_feature_data_raw

        # Identify columns
        columns = image_feature_data.columns
        mv_cols = columns[columns.map(lambda col: col.startswith('MV'))]
        # all columns corresponding to megavoxel categories #should usually be -4 since contrast is still included here.
        texture_cols = columns[columns.map(lambda col: col.startswith('text_'))]
        featurecols = columns[columns.map(lambda col: col.startswith('MV') or col.startswith('text_'))]
        mdatacols = columns.drop(featurecols)

        # drop  duplicate data rows:
        image_feature_data.drop_duplicates(subset=featurecols, inplace=True)

        # remove non-finite/ non-scalar valued rows in both
        image_feature_data = image_feature_data[np.isfinite(image_feature_data[featurecols]).all(1)]
        image_feature_data.sort_values(list(featurecols), axis=0, inplace=True)

        # min-max scale all data and split to feature and metadata
        mind = np.min(image_feature_data[featurecols], axis=0)
        maxd = np.max(image_feature_data[featurecols], axis=0)
        featuredf = (image_feature_data[featurecols] - mind) / (maxd - mind)
        mdatadf = image_feature_data[mdatacols]

        # select data
        if datachoice.lower() == 'mv':
            X = featuredf[mv_cols].to_numpy().astype(np.float64)
        elif datachoice.lower() == 'text':
            X = featuredf[texture_cols].to_numpy().astype(np.float64)
        elif datachoice.lower() == 'combined':
            X = featuredf.to_numpy().astype(np.float64)
        else:
            X = featuredf[mv_cols].to_numpy().astype(np.float64)
            print('Invalid data set choice. Using Megavoxel frequencies.')
        print('Dataset shape:', X.shape)
        self.imageIDs.clear()
        self.imageIDs.extend(np.array(mdatadf['ImageID'], dtype='object').astype(int))
        z=np.ones(X.shape[0]).astype(int)
        cat=[1]
        if filter_data!="No Grouping":
            z=np.array(mdatadf[filter_data], dtype='object')
        numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
        # misc info
        num_images_kept = X.shape[0]
        print(f'\nNumber of images: {num_images_kept}\n')

        if new_plot:
            self.main_plot.axes.clear()
            dim=int(projection[0])
            title, xlabel, ylabel, P=plot_type(X, dim, plot)
            self.plot_data.clear()

            #save x, y, z data and plot
            self.plot_data.append(P[:,0])
            self.plot_data.append(P[:,1])
            if dim==3:
                self.plot_data.append(P[:, 2])
            else:
                self.plot_data.append(np.zeros(len(self.plot_data[-1])))
        else:
            for artist in self.main_plot.axes.collections:
                artist.remove()
        self.labels.clear()
        self.labels.extend(list(map(str, z)))
        self.plots.clear()
        colors= plt.cm.get_cmap('gist_rainbow')(range(0, 255, int(255/len(np.unique(self.labels)))))

        if len(np.unique(self.labels))>1:
            for label, i in zip(np.unique(self.labels), range(len(np.unique(self.labels)))):
                self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0][np.array(self.labels)==label], self.plot_data[1][np.array(self.labels)==label], self.plot_data[2][np.array(self.labels)==label], label=label,
                             s=10, alpha=1, color=[colors[i]], depthshade=False, picker=0.1, cmap=colors))
                print("not unique")
        else:
            self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels[0],
                                              s=10, alpha=1, color=[colors[0]], depthshade=False, picker=0.1, cmap=colors))
        #legend formating
        cols=2
        bbox=(1.3, 0.75)
        text=""
        handle=[matplotlib.patches.Patch(color=colour, label=label) for label, colour in zip(self.labels, colors)]
        #increase legend columns if too many labels
        if len(self.labels)>1:
            text=max(self.labels, key = len)
        if len(np.unique(self.labels))>40:
            cols=cols + ceil(len(np.unique(self.labels))/40)
            bbox=(1.6, 0.5)
        #wrap_text if longer than 10 characters
        if len(text)>10:
            labels = [fill(l, 20) for l in np.unique(self.labels)]
            self.main_plot.axes.legend(handle, labels, bbox_to_anchor=bbox, ncol=cols,loc='center right')
        else:
            self.main_plot.axes.legend(handle, np.unique(self.labels),bbox_to_anchor=bbox, ncol=cols,loc='center right')
        if new_plot:
            self.main_plot.axes.set_title(title)
            self.main_plot.axes.set_xlabel(xlabel)
            self.main_plot.axes.set_ylabel(ylabel)
            for plot in self.plots:
                self.original_xlim=[min(plot.axes.get_xlim3d()[0], self.original_xlim[0]), max(plot.axes.get_xlim3d()[1], self.original_xlim[1])]
                self.original_ylim=[min(plot.axes.get_ylim3d()[0], self.original_ylim[0]), max(plot.axes.get_ylim3d()[1], self.original_ylim[1])]
                self.original_zlim=[min(plot.axes.get_zlim3d()[0], self.original_zlim[0]), max(plot.axes.get_zlim3d()[1], self.original_zlim[1])]
        self.main_plot.draw()

class paramWindow(QDialog):
    def __init__(self):
        super(paramWindow, self).__init__()
        self.setWindowTitle("Set Parameters")
        winlayout = QGridLayout()

        # super voxel box
        superbox = QGroupBox()
        superbox.setLayout(QGridLayout())
        supersizebox = QGroupBox()
        supersizebox.setLayout(QGridLayout())
        superxin = QLineEdit()
        superyin = QLineEdit()
        superzin = QLineEdit()
        superxin.setFixedWidth(30)
        superyin.setFixedWidth(30)
        superzin.setFixedWidth(30)
        supersizebox.layout().addWidget(superxin, 0, 1, 1, 1)
        supersizebox.layout().addWidget(superyin, 1, 1, 1, 1)
        supersizebox.layout().addWidget(superzin, 2, 1, 1, 1)
        supersizebox.layout().addWidget(QLabel("X"), 0, 0, 1, 1)
        supersizebox.layout().addWidget(QLabel("Y"), 1, 0, 1, 1)
        supersizebox.layout().addWidget(QLabel("Z"), 2, 0, 1, 1)
        supersizebox.setTitle("Size")
        supersizebox.layout().setContentsMargins(20, 10, 20, 20)
        superbox.setTitle("Super Voxel")
        svnum = QLineEdit()
        svnum.setFixedWidth(30)
        superbox.layout().addWidget(svnum, 1, 1, 1, 1)
        superbox.layout().addWidget(QLabel("#SV\n Categories"), 1, 0, 1, 1)
        superbox.layout().addWidget(supersizebox, 0, 0, 1, 2)
        superbox.setFixedWidth(superbox.minimumSizeHint().width() + 20)
        superbox.setFixedHeight(superbox.minimumSizeHint().height() + 20)

        # mega voxel box
        megabox = QGroupBox()
        megabox.setLayout(QGridLayout())
        megasizebox = QGroupBox()
        megasizebox.setLayout(QGridLayout())
        megaxin = QLineEdit()
        megayin = QLineEdit()
        megazin = QLineEdit()
        megaxin.setFixedWidth(30)
        megayin.setFixedWidth(30)
        megazin.setFixedWidth(30)
        megasizebox.layout().addWidget(megaxin, 0, 1, 1, 1)
        megasizebox.layout().addWidget(megayin, 1, 1, 1, 1)
        megasizebox.layout().addWidget(megazin, 2, 1, 1, 1)
        megasizebox.layout().addWidget(QLabel("X"), 0, 0, 1, 1)
        megasizebox.layout().addWidget(QLabel("Y"), 1, 0, 1, 1)
        megasizebox.layout().addWidget(QLabel("Z"), 2, 0, 1, 1)
        megasizebox.setTitle("Size")
        megasizebox.layout().setContentsMargins(20, 10, 20, 20)
        megabox.setTitle("Mega Voxel")
        mvnum = QLineEdit()
        mvnum.setFixedWidth(30)
        megabox.layout().addWidget(mvnum, 1, 1, 1, 1)
        megabox.layout().addWidget(QLabel("#MV\n Categories"), 1, 0, 1, 1)
        megabox.layout().addWidget(megasizebox, 0, 0, 1, 2)
        megabox.setFixedSize(superbox.size())

        # main box
        mainbox = QGroupBox()
        mainbox.setLayout(QGridLayout())
        voxelcategories = QLineEdit()
        voxelcategories.setFixedWidth(30)
        trainingimages = QLineEdit()
        trainingimages.setFixedWidth(30)
        usebackground = QCheckBox("Use Background Voxels for comparing") # text is cutoff, don't know actual line?
        normalise = QCheckBox("Normalise Intensity\n Per Condition")
        trainbycondition = QCheckBox("Train by condition")
        leftdropdown = QComboBox()
        leftdropdown.setEnabled(False)
        rightdropdown = QComboBox()
        rightdropdown.setEnabled(False)
        normalise.clicked.connect(lambda: leftdropdown.setEnabled(not leftdropdown.isEnabled()))
        trainbycondition.clicked.connect(lambda: rightdropdown.setEnabled(not rightdropdown.isEnabled()))

        mainbox.layout().addWidget(QLabel("#Voxel\nCategories"), 0, 0, 1, 1)
        mainbox.layout().addWidget(voxelcategories, 0, 1, 1, 1)
        mainbox.layout().addWidget(QLabel("#Training\nImages"), 0, 3, 1, 1)
        mainbox.layout().addWidget(trainingimages, 0, 4, 1, 1)
        mainbox.layout().addWidget(usebackground, 1, 0, 1, 6)
        mainbox.layout().addWidget(normalise, 2, 0, 1, 3)
        mainbox.layout().addWidget(trainbycondition, 2, 3, 1, 3)
        mainbox.layout().addWidget(leftdropdown, 3, 0, 1, 3)
        mainbox.layout().addWidget(rightdropdown, 3, 3, 1, 3)
        mainbox.setFixedWidth(mainbox.minimumSizeHint().width() + 50)
        mainbox.setFixedHeight(mainbox.minimumSizeHint().height() + 20)

        # reset and done buttons
        reset = QPushButton("Reset")
        done = QPushButton("Done")

        # button behaviours
        def donePressed():
            # When done is pressed, all the inputted values are returned, stored in their place
            # and the window closes
            # Theoretically stored where overall parameters are stored (externally)
            superx = superxin.text()
            supery = superyin.text()
            superz = superzin.text()
            svcategories = svnum.text()
            megax = megaxin.text()
            megay = megayin.text()
            megaz = megazin.text()
            mvcategories = mvnum.text()
            voxelnum = voxelcategories.text()
            trainingnum = trainingimages.text()
            bg = usebackground.isChecked() # For checkboxes, return boolean for if checked or not
            norm = normalise.isChecked()
            conditiontrain = trainbycondition.isChecked()
            # dropdown behaviour goes here <--

            # print statements for testing purposes
            print(superx, supery, superz, svcategories, megax, megay, megaz,
                  mvcategories, voxelnum, trainingnum)
            if bg:
                print("bg")
            if norm:
                print("norm")
            if conditiontrain:
                print("conditiontrain")

            self.close()

        done.clicked.connect(donePressed)
        winlayout.addWidget(superbox, 0, 0, 1, 1)
        winlayout.addWidget(megabox, 0, 1, 1, 1)
        winlayout.addWidget(mainbox, 1, 0, 1, 2)
        winlayout.addWidget(reset, 2, 0, 1, 1)
        winlayout.addWidget(done, 2, 1, 1, 1)
        winlayout.setAlignment(Qt.AlignLeft)
        self.setLayout(winlayout)

class segmentationWindow(QDialog):
    def __init__(self):
        super(segmentationWindow, self).__init__()
        self.setWindowTitle("Organoid Segmentation")
        self.setLayout(QGridLayout())

        # buttons
        selectmetadata = QPushButton("Select Metadata File")
        segmentationsettings = QPushButton("Segmentation Settings")
        outputpath = QPushButton("Preview/edit output path")
        segment = QPushButton("Segment")
        nextimage = QPushButton("Next Image")
        previmage = QPushButton("Previous Image")

        # button functions
        def setSegmentationSettings():
            newdialog = QDialog()
            newdialog.setWindowTitle("Set Segmentation Settings")
            newdialog.setLayout(QGridLayout())
            minarea = QLineEdit()
            intensity = QLineEdit()
            radius = QLineEdit()
            smoothing = QLineEdit()
            scale = QLineEdit()
            entropy = QLineEdit()
            maximage = QLineEdit()
            confirm = QPushButton("Confirm")
            cancel = QPushButton("Cancel")

            def confirmClicked():
                # do stuff with the values in the line edits
                newdialog.close()
            def cancelClicked():
                newdialog.close()

            confirm.clicked.connect(confirmClicked)
            cancel.clicked.connect(cancelClicked)

            newdialog.layout().addWidget(QLabel("Min Area Spheroid"), 0, 0, 1, 1)
            newdialog.layout().addWidget(minarea, 0, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Intensity Threshold"), 1, 0, 1, 1)
            newdialog.layout().addWidget(intensity, 1, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Radius Spheroid"), 2, 0, 1, 1)
            newdialog.layout().addWidget(radius, 2, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Smoothing Parameter"), 3, 0, 1, 1)
            newdialog.layout().addWidget(smoothing, 3, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Scale Spheroid"), 4, 0, 1, 1)
            newdialog.layout().addWidget(scale, 4, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Entropy Threshold"), 5, 0, 1, 1)
            newdialog.layout().addWidget(entropy, 5, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Max Image Fraction"), 6, 0, 1, 1)
            newdialog.layout().addWidget(maximage, 6, 1, 1, 1)
            newdialog.layout().addWidget(confirm, 7, 0, 1, 1)
            newdialog.layout().addWidget(cancel, 7, 1, 1, 1)
            newdialog.setFixedSize(newdialog.minimumSizeHint())
            newdialog.show()
            newdialog.exec()


        segmentationsettings.clicked.connect(setSegmentationSettings)

        # image boxes
        focusimage = QGroupBox("Focus Image")
        segmentmap = QGroupBox("Segmentation Map")
        # put images here

        # add everything to layout
        self.layout().addWidget(selectmetadata, 0, 0)
        self.layout().addWidget(segmentationsettings, 1, 0)
        self.layout().addWidget(outputpath, 2, 0)
        self.layout().addWidget(segment, 3, 0)
        self.layout().addWidget(focusimage, 0, 1, 3, 1)
        self.layout().addWidget(segmentmap, 0, 2, 3, 1)
        self.layout().addWidget(previmage, 3, 1)
        self.layout().addWidget(nextimage, 3, 2)


class colorchannelWindow(object):
    def __init__(self, ch, color):
        win = QDialog()
        win.setWindowTitle("Color Channel Picker")
        title = QLabel("Channels")
        title.setFont(QFont('Arial', 25))
        title.setAlignment(Qt.AlignCenter)
        win.setLayout(QFormLayout())
        win.layout().addRow(title)
        self.btn=[]
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        btn_ok= QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        self.color=color
        self.tmp_color=color[:]

        for i in range(ch):
            self.btn.append(QPushButton('Channel_' + str(i+1)))
            #channel button colour is colour of respective channel
            self.btn[i].setStyleSheet('background-color: rgb' +str(tuple((np.array(self.color[i])*255).astype(int))) +';')
            win.layout().addRow(self.btn[i])
            btn_grp.addButton(self.btn[i], i+1)
        win.layout().addRow(btn_ok, btn_cancel)
        btn_grp.buttonPressed.connect(self.colorpicker_window)
        btn_ok.clicked.connect(lambda: self.confirmed_colors(win, color))
        btn_cancel.clicked.connect(lambda: win.close())
        win.show()
        win.exec()

    def colorpicker_window(self, button):
            #Qt custom Colorpicker. Update channel button and current colour to selected colour. Update channel color list.
            wincolor=QColorDialog()
            curcolor = (np.array(self.tmp_color[int(button.text()[-1]) - 1]) * 255).astype(int)
            wincolor.setCurrentColor(QColor.fromRgb(curcolor[0], curcolor[1], curcolor[2]))
            wincolor.exec_()
            rgb_color = wincolor.selectedColor()
            if rgb_color.isValid():
                self.btn[int(button.text()[-1])-1].setStyleSheet('background-color: rgb' +str(rgb_color.getRgb()[:-1]) +';')
                self.tmp_color[int(button.text()[-1]) - 1] = np.array(rgb_color.getRgb()[:-1]) / 255
    def confirmed_colors(self, win, color):
        self.color=self.tmp_color[:]
        win.close()

class external_windows():
    def buildExtractWindow(self):
        return extractWindow()

    def buildResultsWindow(self, color):
        return resultsWindow(color)

    def buildParamWindow(self):
        return paramWindow()

    def buildSegmentationWindow(self):
        return segmentationWindow()

    def buildColorchannelWindow(self):
        return colorchannelWindow()
