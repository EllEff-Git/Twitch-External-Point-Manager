import sys, os, threading
# Required system management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



directory = None
"""The base directory of the program, where TEPMpd.exe resides"""
iconPath = None
"""The path of the app icon png"""



if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "tepmpdIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "..", "icons", "tepmpdIcon.png")
    # reassigns the path variables accordingly



class asyncDisplayWindow(QMainWindow):
    """A TEPM helper window to display further prediction details"""

    def __init__(self):
        super().__init__()



    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM (p)rediction (d)isplay"
        # stores the program name



    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(1000, 700))
        # the window size


    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("TEPM (p)rediction (d)isplay")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too big
        self.mainLabel.setMinimumSize(950, 650)
        # tells the label to prefer the main layout's size
        self.mainLayout.addWidget(self.mainLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label to the main layout (should be top, always)


### Queue Poll ###

    def inputPoll(self):
        """The function that keeps polling the input"""
        for item in sys.stdin.read():
        # goes through the standard in and reads the sent dictionary
            print("RECEIVED DATA AT TEPMpd of size:", sys.getsizeof(item))
            print("IS TYPE: ", type(item))





### Starter Startup ###


displayWindowApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
displayWindow = asyncDisplayWindow()
# creates a window reference

inputThread = threading.Thread(target=displayWindow.inputPoll, args=())
# makes a thread for the inputPoll to sit in
inputThread.start()
# starts the thread

displayWindowApp.exec()
# exceutes the app task (runs the QApplication)