from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
import matplotlib.colors as mcolors
import pandas as pd
from mpldatacursor import datacursor
from mpl_toolkits import mplot3d


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

#Callback will open image associated with data point
class left_click():
    def __init__(self, main_plot, plots, projection, x, y, z, labels):
        self.main_plot=main_plot
        self.plots=plots
        self.projection=projection
        self.x=x
        self.y=y
        self.z=z
        self.labels=labels
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

                self.setLayout(grid)

        self.winc = buildImageViewer()
    def __call__ (self, event):
        if event:
            #https://github.com/matplotlib/matplotlib/issues/ 19735   ---- code below from github open issue. wrong event.ind coordinate not fixed in current version matplotlib...
            xx = event.mouseevent.x
            yy = event.mouseevent.y
            label = event.artist.get_label()
            label_ind=self.labels.index(label)

            # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            x2, y2, z2 = proj3d.proj_transform(self.x[label_ind][0], self.y[label_ind][0], self.z[label_ind][0], self.main_plot.axes.get_proj())
            x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
            # the distance
            d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)

            # find the closest by searching for min distance.
            # from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            imin = 0
            dmin = 10000000
            for i in range(len(self.x[label_ind])):
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                x2, y2, z2 = proj3d.proj_transform(self.x[label_ind][i], self.y[label_ind][i], self.z[label_ind][i], self.main_plot.axes.get_proj())
                x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)
                # We find the distance and also the index for the closest datapoint
                if d < dmin:
                    dmin = d
                    imin = i

            #print("Xfixed=", self.x[0][imin], " Yfixed=", self.y[0][imin], " Zfixed=", self.z[0][imin], " PointIdxFixed=", imin)
            self.main_plot.axes.scatter3D(self.x[self.labels.index(label)][imin],
                                        self.y[self.labels.index(label)][imin],
                                        self.z[self.labels.index(label)][imin], s=20, facecolor="none",
                                        edgecolor='red', alpha=1)

            self.main_plot.draw()

#zoom in/out fixed xy plane
class fixed_2d():
    def __init__(self, main_plot, sc_plot, projection):
        self.main_plot =main_plot
        self.sc_plot =sc_plot
        self.projection = projection

    def __call__(self, event):

        if event.inaxes is not None:
            if self.projection=="2d":
                if event.button == 'up':
                    self.main_plot.axes.mouse_init()
                    self.main_plot.axes.xaxis.zoom(-1)
                    self.main_plot.axes.yaxis.zoom(-1)
                    self.main_plot.axes.zaxis.zoom(-1)
                if event.button =='down':
                    self.main_plot.axes.xaxis.zoom(1)
                    self.main_plot.axes.yaxis.zoom(1)
                    self.main_plot.axes.zaxis.zoom(-1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()

class extractWindow(QDialog):
    def __init__(self):
        super(extractWindow, self).__init__()
        largetext = QFont("Arial", 12, 1)
        self.setWindowTitle("Extract Metadata")
        directory = "Image Root Directory"
        samplefilename = "Sample File Name"
        layout = QGridLayout()
        imagerootbox = QTextEdit()
        imagerootbox.setReadOnly(True)
        imagerootbox.setText(directory)
        imagerootbox.setFixedSize(300, 60)
        imagerootbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        imagerootbox.setFont(largetext)

        selectimage = QPushButton("Select Image Directory")
        selectimage.setFixedSize(selectimage.minimumSizeHint())
        selectimage.setFixedHeight(40)

        samplefilebox = QTextEdit()
        samplefilebox.setReadOnly(True)
        samplefilebox.setText(samplefilename)
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

        cancel.clicked.connect(self.close)

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
    def __init__(self):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=False
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
        typedropdown = QComboBox()
        typedropdown.addItem("PCA")
        typedropdown.addItem("t-SNE")
        typedropdown.addItem("Sammon")
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
        boxlayout.addWidget(typedropdown, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        # test points. normally empty list x=[], y=[], z=[] #temporary until read in formated super/megavoxel data
        #x = [1, 5]
        #y = [7, 2]
        #z = [0,0]
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        self.x=[]
        self.y=[]
        self.z=[]
        self.labels=[]
        self.plots=[0,0,0]
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D(self.x, self.y, self.z, s=10, alpha=1, depthshade=False, picker=True)
        #sc_plot = self.main_plot.axes.scatter(self.x, self.y, self.z, s=10, alpha=1, depthshade=False, picker=True)
        self.main_plot.axes.set_position([0, 0, 1, 1])
        if not self.x and not self.y:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim=0
        self.original_ylim=0
        if all(np.array(self.z)==0):
            self.original_zlim=[0, 0.1]
        else:
            self.original_zlim=sc_plot.axes.get_zlim3d()

        projection = "2d"  # update from radiobutton
        def axis_limit(sc_plot):
            xlim = sc_plot.axes.get_xlim3d()
            ylim = sc_plot.axes.get_ylim3d()
            lower_lim=min(xlim[0], ylim[0])
            upper_lim=max(xlim[1], ylim[1])
            return(lower_lim, upper_lim)
        def toggle_2d_3d(x, y, z, projection, sc_plot, checkbox_cur, checkbox_prev, dim):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(x, y, z, projection, sc_plot, dim)
        def check_projection(x, y, z, projection, sc_plot, dim):
            if dim == "2d":
                projection=dim
                low, high= axis_limit(sc_plot)
                #for debugging
                #print(low, high)
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=0, elev=90)
                if self.original_xlim==0 and self.original_ylim==0 and self.original_zlim==0:
                    self.original_xlim=[low-1, high+1]
                    self.original_ylim=[low - 1, high + 1]
                self.main_plot.axes.set_xlim(low-1, high+1)
                self.main_plot.axes.set_ylim(low-1, high+1)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                #self.main_plot.axes.set_zlim3d(0,0.1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                if self.z:
                    self.main_plot.axes.set_zlim3d(np.amin(self.z)-1, np.amax(self.z)+1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.fig.canvas.draw()
                self.main_plot.axes.mouse_init()

        # button features go here
        selectfile.clicked.connect(lambda: self.loadFeaturefile())
        twod.toggled.connect(lambda: toggle_2d_3d(self.x, self.y, self.z, projection, sc_plot, twod, threed, "2d"))
        threed.toggled.connect(lambda: toggle_2d_3d(self.x, self.y, self.z, projection, sc_plot, threed, twod, "3d"))
        twod.setChecked(True)
        fixed_camera = fixed_2d(self.main_plot, sc_plot, projection)
        magic=left_click(self.main_plot, self.plots, projection, self.x, self.y, self.z, self.labels)
        #picked=pick_onclick(self.main_plot, self.plots, projection, self.x, self.y, self.z, self.labels)
        # matplotlib callback mouse/scroller actions
        rot =self.main_plot.fig.canvas.mpl_connect('scroll_event', fixed_camera)
        magic=self.main_plot.fig.canvas.mpl_connect('pick_event', magic)
        #self.main_plot.fig.canvas.mpl_connect('pick_event', picked)

        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)

        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 400)
        minsize.setWidth(self.minimumSizeHint().width() + 300)
        self.setFixedSize(minsize)
    def reset_view(self):
        print(self.original_xlim, self.original_ylim, self.original_zlim)
        self.main_plot.axes.set_xlim(self.original_xlim)
        self.main_plot.axes.set_ylim(self.original_ylim)
        if self.z:
            self.main_plot.axes.set_zlim3d(np.amin(self.z) - 1, np.amax(self.z) + 1)
        #self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=90, elev=90)
        self.main_plot.draw()

    def loadFeaturefile(self):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file = filename
            print(self.feature_file)
            self.data_filt()
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def data_filt(self):
        image_feature_data_raw = pd.read_csv(self.feature_file, sep='\t', na_values='        NaN')
        from IPython.display import display
        display(image_feature_data_raw)

        # Filter dataframe as needed:
        #   to filter the dataframe (e.g. to only select orws with specific range of values):
        #   set filter_data to True below, change FILTER COLUMN to the desired column,
        #   change FILTER VALUE to the desired value, and check that the operation (==, >, <, <=, >=) is correct.
        #   copy and paste the indented filter control lines below to add aditional filtering as needed.
        filter_data = True

        # rescale texture features to the range [0, 1]
        rescale_texture_features = False

        # choose dataset to use for clustering: EDIT HERE
        # Choices:
        # 'MV' -> megavoxel frequencies,
        # 'text' -> 4 haralick texture features,
        # 'combined' -> both together
        datachoice = 'MV'

        if filter_data:
            df = image_feature_data_raw
            df.loc[df['Well'].str.contains('c02'), 'Treatment'] = 'DMSO'
            df.loc[df['Well'].str.contains('c03'), 'Treatment'] = 'MEDIA'
            df.loc[df['Well'].str.contains('c04'), 'Treatment'] = 'STS'
            df.loc[df['Well'].str.contains('c05'), 'Treatment'] = 'ABT-263'
            df.loc[df['Well'].str.contains('c06'), 'Treatment'] = 'A-1331852'
            df.loc[df['Well'].str.contains('c07'), 'Treatment'] = 'AZD-4320'
            df.loc[df['Well'].str.contains('c08'), 'Treatment'] = 'ABT-199'
            df.loc[df['Well'].str.contains('c09'), 'Treatment'] = 'S63415'
            df.loc[df['Well'].str.contains('c10'), 'Treatment'] = 'S+ABT-263'
            df.loc[df['Well'].str.contains('c11'), 'Treatment'] = 'S+A-1331852'
            df.loc[df['Well'].str.contains('c12'), 'Treatment'] = 'S+AZD-4320'
            df.loc[df['Well'].str.contains('c13'), 'Treatment'] = 'S+ABT-199'
            #Made up
            df.loc[df['Well'].str.contains('c19'), 'Treatment'] = 'unknown19'
            df.loc[df['Well'].str.contains('c20'), 'Treatment'] = 'unknown20'
            df.loc[df['Well'].str.contains('c21'), 'Treatment'] = 'unknown21'
            df.loc[df['Well'].str.contains('c22'), 'Treatment'] = 'unknown22'

            wt = df.loc[df['Well'].str.contains('r05')]
            oneH6 = df.loc[df['Well'].str.contains('r06')]
            sixG10 = df.loc[df['Well'].str.contains('r07')]
            #made up
            sixG10 = df.loc[df['Well'].str.contains('r03')]

            # filter here
            # documentation on how to filter Pandas dataframes can be found at: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas.DataFrame.loc

            image_feature_data = sixG10
        else:
            image_feature_data = image_feature_data_raw

        display(image_feature_data)

        # Identify columns
        columns = image_feature_data.columns
        mv_cols = columns[columns.map(lambda col: col.startswith(
            'MV'))]  # all columns corresponding to megavoxel categories #should usually be -4 since contrast is still included here.
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

        imageIDs = np.array(mdatadf['ImageID'], dtype='object')
        treatments = np.array(mdatadf['Treatment'], dtype='object')
        Utreatments = np.unique(treatments)
        numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
        y = imageIDs
        z = treatments

        # misc info
        num_images_kept = X.shape[0]
        print(f'\nNumber of images: {num_images_kept}\n')

        print('Treatments found:')
        print(Utreatments)

        # set colors if needed.
        if len(Utreatments) > 10:
            import matplotlib as mpl
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, 20))
            mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)

        from IPython.display import display
        display(featuredf)
        # display(image_feature_data.describe())

        # PCA kernel function: EDIT HERE
        # set as 'linear' for linear PCA, 'rbf' for gaussian kernel,
        # 'sigmoid' for sigmoid kernel,
        # 'cosine' for cosine kernel
        func = 'rbf'

        # plot parameters: EDIT HERE
        title = 'PCA plot'
        xlabel = 'PCA 1'
        ylabel = 'PCA 2'

        # makes plot
        from sklearn.decomposition import PCA, KernelPCA
        from sklearn.preprocessing import StandardScaler

        sc = StandardScaler()
        X_show = sc.fit_transform(X)
        pca = KernelPCA(n_components=3, kernel=func)
        P = pca.fit(X_show).transform(X_show)

        #self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        #sc_plot = self.main_plot.axes.scatter(x, y, z, s=10, alpha=1, depthshade=False, picker=True)
        self.main_plot.axes.clear()
        print(np.zeros(len(P)))
        self.labels.extend(Utreatments)
        for treat, i in zip(Utreatments,[0,1,2]) :
            self.x.append(P[z == treat, 0])
            self.y.append(P[z == treat, 1])
            self.z.append(P[z == treat, 2])

            #np.zeros(len(P[z == treat, 0]))
            #self.plots[i]=self.main_plot.axes.scatter(P[z == treat, 0], P[z == treat, 1], P[z == treat, 2] ,label=treat, marker='x', s=10, alpha=0.7, depthshade=False, picker=len(P[z== treat,0])) #picker=True)#, pickradius=0.01)
            self.plots[i] = self.main_plot.axes.scatter3D(P[z == treat, 0], P[z == treat, 1], P[z == treat, 2], label=treat,
                                                    s=10, alpha=0.7, depthshade=False,
                                                    picker=1)  # picker=True)#, pickradius=0.01)


        #self.plots[0] = self.main_plot.axes.scatter(self.x, self.y, self.z, label=self.labels,
        #                                            marker='o', s=10, alpha=1, depthshade=False, picker=True)
        self.main_plot.axes.legend()
        self.main_plot.axes.set_title(title)
        self.main_plot.axes.set_xlabel(xlabel)
        self.main_plot.axes.set_ylabel(ylabel)
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
        normalise = QCheckBox("Normalise Intesity\n Per Condition")
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
        title = QLabel("Organoid Segmentation")
        title.setFont(QFont('Arial', 25))
        self.layout().addWidget(title)
        choosemdata = QPushButton("Select Metadata File")

        # Define function for button behaviour (choose metadata file, select channels, choose output
        # directory, select segmentation channel, loading windows, create directories, TBA)
        def segment():
            filename, dump = QFileDialog.getOpenFileName(self, 'Select Metadata File', '', 'Text file (*.txt)')
            if filename != '':
                win = QDialog()
                selectall = QPushButton("Select All")
                ok = QPushButton("OK")
                cancel = QPushButton("Cancel")
                items = ["Channel 1", "Channel 2", "Channel 3", "Well", "Field", "Stack", "Metadata File", "ImageID"]
                list = QListWidget()
                for item in items:
                    list.addItem(item)
                list.setSelectionMode(QAbstractItemView.MultiSelection)

                selectall.clicked.connect(lambda: list.selectAll())
                cancel.clicked.connect(lambda: win.close())

                # OK button behaviour: User has made their selection, and thus moves on to next step
                def okClicked():
                    win.close()
                    selected = list.selectedItems()
                    if selected == []:
                        print("nothing selected")
                    else:
                        outputdirectory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
                        if outputdirectory != '':
                            newlist = QListWidget()
                            for item in items:
                                newlist.addItem(item)
                            newlist.setSelectionMode(QAbstractItemView.SingleSelection)
                            wina = QDialog()
                            wina.setLayout(QGridLayout())
                            wina.layout().addWidget(newlist, 0, 0, 2, 2)
                            secondok = QPushButton("OK")
                            secondcancel = QPushButton("Cancel")
                            secondcancel.clicked.connect(lambda: wina.close())
                            progress = QProgressBar()
                            # Again, new OK button behaviour: write images, with progress bar to track status
                            def secondOkClicked():
                                wina.close()
                                selecteditem = newlist.selectedItems()
                                if selecteditem == []:
                                    print("nothing selected")
                                else:
                                    completed = 0
                                    winb = QDialog()
                                    winb.setLayout(QGridLayout())
                                    progress.setFixedSize(500, 20)
                                    dl = QPushButton("Download")
                                    winb.layout().addWidget(progress, 0, 0, 2, 2)
                                    winb.layout().addWidget(dl, 2, 1, 1, 1)
                                    winb.show()
                                    while completed < 100:
                                        completed += 0.0001
                                        progress.setValue(int(completed))
                                    winb.exec()

                            secondok.clicked.connect(lambda: secondOkClicked())
                            wina.layout().addWidget(secondok, 2, 0, 1, 1)
                            wina.layout().addWidget(secondcancel, 2, 1, 1, 1)
                            wina.show()
                            wina.exec()

                ok.clicked.connect(lambda: okClicked())

                win.setLayout(QGridLayout())
                win.layout().addWidget(list, 0, 0, 2, 2)
                win.layout().addWidget(selectall, 2, 0, 1, 2)
                win.layout().addWidget(ok, 3, 0, 1, 1)
                win.layout().addWidget(cancel, 3, 1, 1, 1)
                win.show()
                win.exec()

        choosemdata.clicked.connect(segment)
        self.layout().addWidget(choosemdata)

class colorchannelWindow(object):
    def __init__(self, ch, color):
        win = QDialog()
        win.setWindowTitle("Color Channel Picker")
        title = QLabel("Channels")
        title.setFont(QFont('Arial', 25))
        win.setLayout(QFormLayout())
        win.layout().addWidget(title)
        self.btn=[]
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        self.color=color

        for i in range(ch):
            self.btn.append(QPushButton('Channel_' + str(i+1)))
            #channel button colour is colour of respective channel
            self.btn[i].setStyleSheet('background-color: rgb' +str(tuple((np.array(self.color[i])*255).astype(int))) +';')
            win.layout().addRow(self.btn[i])
            btn_grp.addButton(self.btn[i], i+1)
        print(btn_grp.buttons())

        btn_grp.buttonPressed.connect(self.colorpicker_window)
        win.show()
        win.exec()

    def colorpicker_window(self, button):
            #Qt custom Colorpicker. Update channel button and current colour to selected colour. Update channel color list.
            wincolor=QColorDialog()
            curcolor=(np.array(self.color[int(button.text()[-1])-1])*255).astype(int)
            wincolor.setCurrentColor(QColor.fromRgb(curcolor[0], curcolor[1], curcolor[2]))
            wincolor.exec_()
            rgb_color = wincolor.selectedColor()
            if rgb_color.isValid():
                self.btn[int(button.text()[-1])-1].setStyleSheet('background-color: rgb' +str(rgb_color.getRgb()[:-1]) +';')
                self.color[int(button.text()[-1])-1] = np.array(rgb_color.getRgb()[:-1])/255


class external_windows():
    def buildExtractWindow(self):
        return extractWindow()

    def buildResultsWindow(self):
        return resultsWindow()

    def buildParamWindow(self):
        return paramWindow()

    def buildSegmentationWindow(self):
        return segmentationWindow()

    def buildColorchannelWindow(self):
        return colorchannelWindow()
