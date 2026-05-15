import sys, os
# Required system management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



directory = None
"""The base directory of the program, where TEPMhelp.exe resides"""
iconPath = None
"""The path of the app icon png"""



if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "tepmhelpIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "icons", "tepmhelpIcon.png")
    # reassigns the path variables accordingly



class asyncHelpWindow(QMainWindow):
    """A TEPM helper window to display a help page"""

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM Help"
        # stores the program name

        self.running = True
        # runs

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(900, 500))
        # the window size

    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.setCentralWidget(self.container)
        # sets the main widget to display

    ### Text ###

        self.helpLabel = QLabel()
        # the help text
        self.helpLabel.setText("TEPM\n\n"
                            "To vote (bet) on predictions, enter a sum of points to gamble\n"
                            "You can enter a sum by either manually entering one in the Bet Amount field\n"
                            "or by clicking the Max or Default buttons, which will enter a value based on your current balance and/or the config\n"
                            "To confirm your bet, click the Bet button\n\n"
                            "You can change the stream by entering a different stream in the Change Channel field\n"
                            "To confirm the swap, press the Enter key or click the Change button\n\n"
                            "Keybinds:\n\n"
                            "Confirm bet: Ctrl+B\n"
                            "Set max bet: Ctrl+M\n"
                            "Set default bet: Ctrl+D\n"
                            "Halve current bet: Ctrl+H\n"
                            "Clear bet field: Ctrl+Y\n"
                            "Save own predictions: Ctrl+S\n\n"
                            "Please use the exit button to close, in order to save prediction details!\n"
                            "Exiting the program via Alt+F4 or other means will NOT SAVE your prediction history\n\n"
                            "Currently, re-opening any external window requires 2x clicks - it'll prompt once about already being open\n"
                            "This compromise was made to not have to poll the status, which would increase resource use for a small QoL thing"
                            )
        # the text to display
        self.helpLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to center

        self.mainLayout.addWidget(self.helpLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

 

### Quit ###

    def closeEvent(self, event):
        """pyQt method to trigger a stop when exiting"""
        self.running = False
        # stops run

        helpWindowApp.quit()
        # quits the app

        event.accept()
        # accepts the exit event from Windows



### Starter Startup ###


helpWindowApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
displayWindow = asyncHelpWindow()
# creates a window reference

helpWindowApp.exec()
# exceutes the app task (runs the QApplication)