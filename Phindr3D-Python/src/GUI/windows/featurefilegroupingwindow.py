from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class selectWindow(object):
    def __init__(self, chk_lbl, col_lbl, win_title, grp_title, col_title, groupings):
        win = QDialog()
        win.setWindowTitle(win_title)
        win.setLayout(QGridLayout())
        self.x_press=True
        ok_button = QPushButton("OK")
        win.layout().addWidget(ok_button, 1, 1)
        # setup checkbox for groups
        if len(chk_lbl) > 0:
            grp_title = QLabel(grp_title)
            grp_title.setFont(QFont('Arial', 10))
            grp_checkbox = QGroupBox()
            grp_checkbox.setFlat(True)
            grp_list = []
            grp_vbox = QVBoxLayout()
            grp_vbox.addWidget(grp_title)
            #add checkboxes to layout
            for lbl in chk_lbl:
                grp_list.append(QCheckBox(lbl))
                grp_vbox.addWidget(grp_list[-1])
            grp_vbox.addStretch(1)
            grp_checkbox.setLayout(grp_vbox)
            win.layout().addWidget(grp_checkbox, 0, 0)
            ok_button.clicked.connect(lambda: self.selected(grp_checkbox, win, groupings))
        else:
            ok_button.clicked.connect(lambda: win.close())
        # setup Column box
        if len(col_lbl) > 0:
            ch_title = QLabel(col_title)
            ch_title.setFont(QFont('Arial', 10))
            ch_checkbox = QGroupBox()
            ch_checkbox.setFlat(True)
            ch_vbox = QVBoxLayout()
            ch_vbox.addWidget(ch_title)
            # add columns to layout
            for lbl in col_lbl:
                ch_label = QLabel(lbl)
                ch_vbox.addWidget(ch_label)
            ch_vbox.addStretch(1)
            ch_checkbox.setLayout(ch_vbox)
            win.layout().addWidget(ch_checkbox, 0, 1)
        win.show()
        win.setWindowFlags(win.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        win.exec()

    #return selected groups
    def selected(self, grp_checkbox, win, groupings):
        for checkbox in grp_checkbox.findChildren(QCheckBox):
            # print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked():
                groupings.append(checkbox.text())
        self.x_press=False
        win.close()

'''
class featurefilegroupingWindow(object):
    def __init__(self, columns, groupings):
        win = QDialog()
        win.setWindowTitle("Filter Feature File Groups and Channels")
        win.setLayout(QFormLayout())
        #setup checkbox for groups
        grp_title = QLabel("Grouping")
        grp_title.setFont(QFont('Arial', 10))
        grp_checkbox=QGroupBox()
        grp_checkbox.setFlat(True)
        grp_list=[]
        grp_vbox = QVBoxLayout()
        grp_vbox.addWidget(grp_title)
        #setup Channels Column
        ch_title = QLabel("Channels")
        ch_title.setFont(QFont('Arial', 10))
        ch_checkbox=QGroupBox()
        ch_checkbox.setFlat(True)
        ch_vbox = QVBoxLayout()
        ch_vbox.addWidget(ch_title)
        #add channel columns and checkboxes to layout
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
        win.setWindowFlags(win.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        win.exec()
    #change ResultsWindow GUI dropdown to contain groupings
    def selected(self, grp_checkbox, win, groupings):
        for checkbox in grp_checkbox.findChildren(QCheckBox):
            #print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked():
                groupings.append(checkbox.text())
        win.close()
'''