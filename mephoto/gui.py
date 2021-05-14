from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QThreadPool, QRegExp, QSize, Qt, QSettings, QByteArray
from PySide2.QtWidgets import QMainWindow, QAction, QDockWidget, QFrame, QVBoxLayout, QFileDialog, QStyle, QMessageBox, QApplication, QWidget, QDialog, QDoubleSpinBox
from PySide2.QtWidgets import QLineEdit, QSpinBox, QLabel, QComboBox, QProgressBar, QStatusBar,  QPushButton, QFormLayout, QGroupBox, QCheckBox, QTabWidget, qApp
from PySide2.QtWidgets import QProgressDialog, QDialogButtonBox, QDialog
from PySide2.QtGui import QRegExpValidator, QKeySequence, QCloseEvent

from eqt.threading import Worker
from eqt.threading.QtThreading import ErrorObserver

import sys
import os
from organise import *


class MePhoto(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # 
        self.configured = [False, True]

        # add menu bar
        self.add_menu_bar()

        # add progress bar to statusBar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.statusBar().addPermanentWidget(self.progress_bar)

        # add ThreadPool
        self.threadpool = QThreadPool()


        # central Widget
        btn = QPushButton(self)
        btn.setText("Import")
        btn.setEnabled(False)
        btn.setCheckable(True)
        btn.clicked.connect( lambda: self.startImport() )
        self.import_button = btn

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.import_button)

        widget = QWidget(self)
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        

    def add_menu_bar(self):
        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # QAction
        select_origin_action = QAction("Select Origin Directory", self)
        select_origin_action.triggered.connect(
            lambda: self.selectDirectory('origin', os.path.abspath('/media/edo/LUMIX/DCIM'))
            )
        self.file_menu.addAction(select_origin_action)

        select_destination_action = QAction("Select Destination Directory", self)
        select_destination_action.triggered.connect(
            lambda: self.selectDirectory('destination', os.path.abspath('/mnt/share/Pictures/tutte'))
            )
        

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # add actions to menu
        self.file_menu.addAction(select_origin_action)
        self.file_menu.addAction(select_destination_action)
        self.file_menu.addAction(exit_action)

        
    def selectDirectory(self, which, start_directory=None):
        if which == 'origin':
            dir = QFileDialog.getExistingDirectory(self,"Select {} directory".format(which))
            self.origin_directory = dir
            self.configured[0] = True
        elif which == 'destination':
            dir = QFileDialog.getExistingDirectory(self,"Select {} directory".format(which), dir=start_directory)
        
            self.destination_directory = dir
            self.configured[1] = True
        self.enableImportButton()

    def enableImportButton(self):
        self.import_button.setEnabled( self.configured[0] and self.configured[1] ) 

    def startImport(self):
        import_worker = Worker(self.importer, origin=self.origin_directory, 
                               destination=self.destination_directory, method='stat')
        import_worker.signals.progress.connect(self.progress)
        import_worker.signals.finished.connect(lambda: self.progress_bar.setValue(0))
        self.threadpool.start(import_worker)

    def importer(self, **kwargs):
        origin = kwargs.get('origin')
        destination = kwargs.get('destination')
        method = kwargs.get('method', 'stat')
        progress_callback = kwargs.get('progress_callback')
        #base_directory = os.path.join("/mnt","share","Pictures","tutte")
        base_directory = os.path.abspath(destination)

        print ("base_directory", base_directory)
        print ("origin", origin)
        # iarg = sys.argv[1]
        # if iarg == "":
        #     orig_dir = os.path.abspath("/mnt/share/Pictures/nexus-s/2012-2013/")
        # else:
        #     orig_dir = os.path.abspath(sys.argv[1])
        orig_dir = os.path.abspath(origin)

        all_pics = os.listdir(orig_dir)
        success = []
        fail = []


        mlib = []
        
        for i,el in enumerate(all_pics):
            print ("Progress {0}/{1} {2}".format(i,len(all_pics),el))
            try:
                current_picture = os.path.join(orig_dir, el)
                # print (current_picture, base_directory)
                # tqdm.write ("",current_picture, base_directory)
                if should_organise(current_picture, base_directory, 'stat'):
                    exif, mdir, fname = organise_picture(current_picture, base_directory)
                    success.append(current_picture)
                    exif_filtered = {}
                    for k,v in exif.items():
                        if type(v) != bytes:
                            exif_filtered[k] = v
                    md5sum = md5(current_picture)
                    mlib.append({'filename': fname, 
                                'exif': exif_filtered, 
                                'directory': mdir,
                                'md5' : md5sum })
                else:
                    # print("Skipping ", os.path.basename(current_picture))
                    # tqdm.write("Skipping ", os.path.basename(current_picture))
                    pass
            except OSError as oe:
                fail.append(current_picture)
            progress_callback.emit(i/len(all_pics)*100)

        # if any picture has been copied
        if len(mlib) > 1:
            for k,v in mlib[0]['exif'].items():
                print (k, type(v))


        with open("organise.log","w") as f:
            f.write("Organising pictures \n  from {0}\n  to   {1}\n"
                    .format(orig_dir, base_directory))
            f.write("Success: {}/{}\n".format(len(success),len(all_pics)))
            f.write("Fail   : {}/{}\n".format(len(fail),len(all_pics)))
            f.write("Failed file list:\n")
            for failed in fail:
                f.write("{}\n".format(failed))

        try:
            with open(os.path.join(base_directory, 'library.json'), "r") as f:
                remote_mlib = json.load(f)
        except FileNotFoundError as err:
            mlib = []
            print("Caught error: ", err, mlib)
            with open(os.path.join(base_directory, 'library.json'), "w") as fw:
                json.dump(mlib, fw)
        except json.decoder.JSONDecodeError as jde:
            print ("Some error in library", jde)

        try:
            with open(os.path.join(base_directory, 'library.json'), "w") as fw:
                json.dump(mlib, fw)
        except json.decoder.JSONDecodeError as jde:
            print ("Some error in library", jde)

    def progress(self, value):
        self.progress_bar.setValue(value)

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = MePhoto()
    app.show()
    qapp.exec_()
