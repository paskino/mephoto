import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QAction, \
    QFrame, QVBoxLayout, QMainWindow, QStyle, QFileDialog, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtGui, QtCore
import imghdr
from PIL import Image

#from PyQt5.QtWidgets import *

class ErrorObserver:

   def __init__(self):
       self.__ErrorOccurred = False
       self.__ErrorMessage = None
       self.CallDataType = 'string0'

   def __call__(self, obj, event, message):
       self.__ErrorOccurred = True
       self.__ErrorMessage = message

   def ErrorOccurred(self):
       occ = self.__ErrorOccurred
       self.__ErrorOccurred = False
       return occ

   def ErrorMessage(self):
       return self.__ErrorMessage


class App(QMainWindow):

    def __init__(self, **kwargs):
        super().__init__()
        self.title = 'PyQt5 image - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
        self.e = ErrorObserver()

    def resizeEvent(self, event):
        #self.resized.emit()
        #return super(Window, self).resizeEvent(event)    
        #print (event)
        rect = self.geometry()
        self.left = rect.left()
        self.top = rect.top()
        self.width = rect.width() - self.left
        self.height = rect.height() - self.top
        #print (self.left, self.top, self.width, self.height)
        self.rescale_pixmap()
    
    def rescale_pixmap(self):
        size = QtCore.QSize(self.width, self.height)
        scaled_pixmap = self.pixmap.scaled(size, 
            aspectRatioMode=QtCore.Qt.KeepAspectRatio,
            transformMode = QtCore.Qt.SmoothTransformation) #QtCore.Qt.KeepAspectRatioByExpanding)
        self.label.setPixmap(scaled_pixmap)
        
    def toolbar(self):
        # Initialise the toolbar
        self.toolbar = self.addToolBar('Viewer tools')

        # define actions
        openAction = QAction(self.style().standardIcon(QStyle.SP_DirOpenIcon), 'Open file', self)
        openAction.triggered.connect(self.openFile)

        saveAction = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save current render as PNG', self)
        # saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.saveFile)

        # Add actions to toolbar
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)

    def keyPressEvent(self, e):
        '''Advances forward or backward with arrow keys'''
        if e.key() == QtCore.Qt.Key_Right:
            print ("Right")
            if self.index < len(self.filenames)-1 and not self.index == -1:
                self.index += 1
                self.statusBar().showMessage('{}/{} {}'.format(self.index, 
                len(self.filenames)-1,
                  self.filenames[self.index]))
                self.loadFile(self.filenames[self.index])

        if e.key() == QtCore.Qt.Key_Left:
            print ("Left")
            if self.index > 0:
                self.index -= 1
                self.loadFile(self.filenames[self.index])
                self.statusBar().showMessage('{}/{} {}'.format(self.index, 
                len(self.filenames)-1,
                  self.filenames[self.index]))


    def openFile(self):
        '''Opens a file or a list of files'''
        fn = QFileDialog.getOpenFileNames(self, 'Open File')
        # If the user has pressed cancel, the first element of the tuple will be empty.
        # Quit the method cleanly
        if not fn[0]:
            return

        # Single file selection
        if len(fn[0]) == 1:
            self.index = -1
            fname = fn[0][0]
            self.filenames = fname
            self.loadFile(fname)
        # Multiple TIFF files selected
        else:
            # Make sure that the files are sorted 0 - end
            #filenames = natsorted(fn[0])
            filenames = fn[0]
            self.filenames = filenames
            self.index = 0
            self.loadFile(filenames[0])
        self.show()

    def loadFile(self, fname):
        what = imghdr.what(fname)
        if what in ['jpeg', 'png']:
            # can be read
            if what == 'jpeg':
                # read the exif orientation
                # Orientation -> 274
                # 1 0 degrees – the correct orientation, no adjustment is required.
                # 2 0 degrees, mirrored – image has been flipped back-to-front.
                # 3 80 degrees – image is upside down.
                # 4 180 degrees, mirrored – image is upside down and flipped back-to-front.
                # 5 90 degrees – image is on its side.
                # 6 90 degrees, mirrored – image is on its side and flipped back-to-front.
                # 7 270 degrees – image is on its far side.
                # 8 270 degrees, mirrored – image is on its far side and flipped back-to-front.
                try:
                    orientation = Image.open(fname)._getexif()[274]
                    print ("orientation ", orientation)
                except KeyError as ke:
                    print (ke)

            self.label.pixmap().load(fname)
            size = QtCore.QSize(self.width, self.height)
            #if orientation =! 0:

            scaled_pixmap = self.label.pixmap().scaled(size, 
                aspectRatioMode=QtCore.Qt.KeepAspectRatio) #QtCore.Qt.KeepAspectRatioByExpanding)
            self.label.setPixmap(scaled_pixmap)
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openFile)

        closeAction = QAction("Close", self)
        closeAction.setShortcut("Ctrl+Q")
        closeAction.triggered.connect(self.close)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(closeAction)

        self.frame = QFrame()
        self.vl = QVBoxLayout()

        # Create widget
        label = QLabel(self)
        #label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label = label
        #self.index = -1
        self.pixmap = QPixmap('image.jpeg')
        
        #self.resize(pixmap.width(),pixmap.height())
        size = QtCore.QSize(self.width, self.height)
        scaled_pixmap = self.pixmap.scaled(size,
          aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding,
          transformMode = QtCore.Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        
        self.vl.addWidget(label)

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.toolbar()

        self.statusBar()
        self.setStatusTip('Open file to begin visualisation...')

        self.show()

    def saveFile(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    
