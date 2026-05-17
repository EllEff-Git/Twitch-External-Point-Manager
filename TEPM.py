import os, sys, requests, datetime, json, subprocess, uuid, threading, queue
# Required program management
import pandas as pnd
# Soft required for CSV management (not required, but improves formatting)
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



tepmVer = "0.5.17.0757"
"""TEPM program version (Y.MM.DD.HHMM)"""



directory = None
"""The base directory of the program, where TEPM.exe resides"""
iconPath = None
"""The path of the app icon png"""



if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "tepmIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "icons", "tepmIcon.png")
    # reassigns the path variables accordingly



dataDir = os.path.join(directory, "Data")
"""The /Data/ directory"""
profilePath = os.path.join(dataDir, "Profile")
"""The user profile path"""
textPath = os.path.join(directory, "Channel List.txt")
"""The list of channels, txt"""
csvPath = os.path.join(directory, "Channel Points.csv")
"""The CSV file path"""
streakMapPath = os.path.join(directory, "Streak List.json")
"""The streak map json file path"""
hashFilePath = os.path.join(dataDir, "hashes.json")
"""The hash container file"""
detailWindowPath = os.path.join(dataDir, "TEPMpd.exe")
"""The prediction detail window executable path"""
modWindowPath = os.path.join(dataDir, "TEPMmv.exe")
"""The prediction mod view window executable path"""
helpWindowPath = os.path.join(dataDir, "TEPMhelp.exe")
"""The help window executable path"""
historyWindowPath = os.path.join(dataDir, "TEPMhist.exe")
"""The history window executable path"""
predictHistoryPath = os.path.join(directory, "Prediction History.json")
"""The prediction history json file path"""
cssPath = os.path.join(dataDir, "cssStylesheet.qss")
"""cssStylesheet.qss path"""



profileName = None
"""The user profile (folder) name"""
enableStreaks = False
"""The boolean for streak checking"""
autoAddStreaks = False
"""The boolean for adding streaks automatically"""
autoRemoveStreaks = False
"""The boolean for removing stale streaks automaticall"""
enablePoints = False
"""The boolean for point checking"""
enableErrorLog = False
"""The boolean for error storing in CSV"""
defaultBet = 0
"""The default points to set with default button"""
roundBalanceBet = False
"""The boolean for using default bet as a rounding guide"""
streakMap = {}
"""The map that holds all the streak list information"""
hashMap = {}
"""The map that holds all the hashes and related information"""
excludedEntries = ["enableErrorsInCSV", "autoAddStreaks", "autoRemoveStreaks", "defaultBet", "roundBalanceBet" "exampleChannel"]
"""A list of streakMap entries that shouldn't count for the streak list"""



overrideChannel = None
"""The single channel name, if using single channel"""
predictChannel = None
"""The channel to predict on, if using"""
canRun = False
"""Boolean that determines if the main window can start (True after first window completes)"""
activeOnly = False
"""Boolean that determines if the grabbed streaks should be previously active"""
modWindowBool = False
"""Boolean that determines if the mod view window is open or not"""
displayWindowBool = False
"""Boolean that determines if the details view window is open or not"""



reqSession = requests.Session()
"""A request session that stores cached request information"""
rURL = "https://gql.twitch.tv/gql"
"""The Twitch endpoint to make requests to"""
gURL = "https://api.github.com/repos/EllEff-Git/Twitch-External-Point-Manager/tags"
"""The GitHub URL to make an update check request to"""



os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = f"--user-data-dir={profilePath} --profile-directory={profileName} --enable-gpu --disable-webgpu --disable-logging --log-level=3"
# environment flags for the chromium webengine



def folders(path):
    """Function to check subfolder existence"""
    for folder in os.listdir(path):
        # goes through each folder in the given path
        if os.path.isdir(os.path.join(path, folder)):
            # if the directory is real
            yield os.path.join(path, folder)
            # joins and goes to next



### Starter Window UI ###

class StarterWindow(QWidget):
    """A class for the first window that pops up"""

    labelSwap = pyqtSignal(str)
    """A pyQt signal to swap the starter window user inform label"""
    configLoaded = pyqtSignal()
    """A pyQt signal to indicate the config has been loaded successfully"""
    starterDone = pyqtSignal(str)
    """A pyQt signal to indicate the starter window is done, passes the main window task string"""

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.version = tepmVer
        """Program version"""
        self.mainIcon = iconPath
        """Program icon"""
        self.programName = f"TEPM Starter"
        """Program name"""

        self.optionReturn = False
        # boolean to store whether user has visited options or not (changes visuals)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(1000, 650)
        # the window size

    ### UI Elements ###

        self.mainStack = QStackedWidget()
        """A stacked widget to show/hide individual pages"""
        self.mainLayout = QGridLayout()
        """The main layout that contains the main elements"""
        self.mainLayout.setSpacing(0)
        # removes spacing
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        # sets content margins
        self.mainLayout.addWidget(self.mainStack)
        # adds the stack to the main layout
        self.setLayout(self.mainLayout)
        # sets the container to fill the window

    ### Main Page ###

        self.mainPage = QWidget()
        # widget to hold the main page elements
        self.mainPage.setObjectName("Starter Main Page")
        # object name
        self.mainStack.addWidget(self.mainPage)
        # adds page to stack
        self.mainPageLayout = QGridLayout(self.mainPage)
        # layout to hold the main page elements

    ### Main Label ### 

        self.mainLabel = QLabel()
        """A label to hold the main information about current process"""
        self.mainLabel.setText("TEPM starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(False)
        # makes the text wrap if it's too big
        self.mainLabel.setMaximumSize(400, 150)
        # tells the label to prefer the main layout's size
        self.mainPageLayout.addWidget(self.mainLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label to the main layout (should be top, always)

    ### Version ###

        self.versionTag = QLabel(f"TEPM v{self.version}\n ")
        """A version tag label"""
        self.versionTag.setToolTip("Current TEPM version")
        # tooltip
        self.versionTag.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        # aligns the text itself to the left
        self.versionTag.setOpenExternalLinks(True)
        # allows opening links (in case of new update)
        self.mainPageLayout.addWidget(self.versionTag, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds to the bottom left corner

    ### Exit ###

        self.exitButton = QPushButton("Exit")
        """Button to exit the starter window"""
        self.exitButton.setToolTip("Quit the application")
        # tooltip
        self.exitButton.setMinimumSize(150, 50)
        # size
        self.exitButton.clicked.connect(lambda: app.exit())
        # connects to exit
        self.mainPageLayout.addWidget(self.exitButton, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        # adds to layout (bottom middle)

    ### Options Button ###

        self.optionsButton = QPushButton("Options")
        # adds options button
        self.optionsButton.setToolTip("Open the options/config view")
        # tooltip
        self.optionsButton.setMinimumSize(100, 50)
        # sets size
        self.optionsButton.clicked.connect(lambda: self.mainStack.setCurrentWidget(self.configPage))
        # connects the options button to display the options page
        self.optionsButton.setEnabled(False)
        # disabled by default

        self.mainPageLayout.addWidget(self.optionsButton, 2, 2, alignment=Qt.AlignmentFlag.AlignRight)
        # adds the button to the right bottom corner

    ### Profile Name Picking ###

        self.profilePickPage = QWidget()
        # widget to hold the profile name picking layout
        self.profilePickPage.setObjectName("Profile Name Page")
        # object name
        self.mainStack.addWidget(self.profilePickPage)
        # adds page to stack
        self.profilePickLayout = QGridLayout(self.profilePickPage)
        # layout to hold the profile picking

        self.labelSwap.emit("No profile configured, please enter a new profile name:\nThis is purely cosmetic")
        # swaps the label

        self.profileNameField = QLineEdit()
        # entry for profile name
        self.profileNameField.setPlaceholderText("Default")
        # sets the default text

        self.usernameButton = QPushButton("Submit")
        # makes a new button to save the name
        self.usernameButton.setFixedSize(100, 50)
        # sets size

        self.profilePickLayout.addWidget(self.profileNameField, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.profilePickLayout.addWidget(self.usernameButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the button and profile name field to layout

        self.usernameButton.clicked.connect(self.userNameGrab)
        # on click, calls the next part



    ### Configuration Page ###

        self.configPage = QWidget()
        # config page widget
        self.configPage.setObjectName("Configuration Page")
        # object name
        self.mainStack.addWidget(self.configPage)
        # adds page to stack
        self.configLayout = QGridLayout(self.configPage)
        # creates a layout just for the config file

        self.configTaskText = QLabel("Configure TEPM\nHover over any text field to see more details")
        # the config page prompt
        self.configTaskText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to center
        self.configLayout.addWidget(self.configTaskText, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to top of config page

        self.defaultBetMask = QIntValidator(0, 250000)
        """A validator for the default bet"""
        
        self.autoAddStreaksCheckbox = QCheckBox("Auto-add streaks")
        """Checkbox for automatically adding streaks"""
        self.autoAddStreakText = QLabel("Automatically add active streaks to list")
        """Text helper for streak addition"""
        self.autoAddStreakText.setToolTip("When checking points and streaks, adds active streaks to the streak list file\n"
                                        "Active streak = longer than 1")
        # tooltip

        self.autoRemoveStreaksCheckbox = QCheckBox("Auto-remove streaks")
        """Checkbox for automatically removing inactive streaks"""
        self.autoRemoveStreaksText = QLabel("Automatically remove stale streaks")
        """Text helper for streak removal"""
        self.autoRemoveStreaksText.setToolTip("Removes streaks that have been broken (0 streak)")
        # tooltip

        self.enableCSVErrorsCheckbox = QCheckBox("Store errors")
        """Checkbox for enabling errors in CSV"""
        self.enableCSVErrorsText = QLabel("Whether to add any point grab errors into CSV")
        """Text helper for CSV errors"""
        self.enableCSVErrorsText.setToolTip("Save any error reasons into the CSV with point/streak data\n"
                                            "Error booleans are saved regardless of this option")
        # tooltip

        self.defaultBetLine = QLineEdit()
        """Line to edit the default bet value"""
        self.defaultBetLine.setValidator(self.defaultBetMask)
        # sets a validator to only accept digits with a max bet of 250000
        self.defaultBetLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.defaultBetLine.setPlaceholderText("5,000")
        # background text
        self.defaultBetText = QLabel("Default bet size")
        """Text helper for default bet"""
        self.defaultBetText.setToolTip("Bet to set automatically with the default button\n"
                                    "If the balance rounding is enabled, rounds the balance to the nearest set value instead\n"
                                    "Eg. 10,000 means a balance of 15,202 would round to a bet of 5,202 (leaving 10,000 as the balance)\n"
                                    "A balance of 31,863 would round to a bet of 1,863 (leaving 30,000 as the balance)")
        # tooltip
        
        self.roundBalanceBetCheckbox = QCheckBox("Round balance to bet")
        """Checkbox to enable balance rounding"""
        self.roundBalanceBetText = QLabel("Whether to round the balance to form bets")
        """Text helper for balance rounding"""
        self.roundBalanceBetText.setToolTip("Uses the default bet as a 'rounding guide' instead")
        # tooltip

        self.autoAddStreakText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.autoRemoveStreaksText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.enableCSVErrorsText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.defaultBetText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.roundBalanceBetText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        # centers all text fields to the top of their slots

        self.configLayout.addWidget(self.autoAddStreaksCheckbox, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.autoRemoveStreaksCheckbox, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.enableCSVErrorsCheckbox, 6, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.defaultBetLine, 8, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.roundBalanceBetCheckbox, 10, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the selector fields to layout

        self.configLayout.addWidget(self.autoAddStreakText, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.autoRemoveStreaksText, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.enableCSVErrorsText, 7, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.defaultBetText, 9, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.roundBalanceBetText, 11, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the text widgets to layout

        self.configPageTopSpacer = QSpacerItem(50, 25)
        # a spacer between the top text and the options
        self.configPageBottomSpacer = QSpacerItem(50, 25)
        # adds a layout spacer below the "save" button

        self.configLayout.addItem(self.configPageTopSpacer, 1, 0)
        self.configLayout.addItem(self.configPageBottomSpacer, 12, 0)
        # adds the spacers to layout

        self.configPrepSaveButton = QPushButton("Save")
        # adds a button to save the config
        self.configPrepSaveButton.setFixedSize(100, 50)
        # sets size
        self.configLayout.addWidget(self.configPrepSaveButton, 13, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

        self.configPrepSaveButton.clicked.connect(self.modifyConfigText)
        # done -> modify config



    ### Task Page ###

        self.taskPage = QWidget()
        # task widget
        self.taskPage.setObjectName("Task Chooser Page")
        # object name

        self.taskLayout = QGridLayout(self.taskPage)
        # creates a new layout for the tasks to use
        self.taskLayout.setColumnMinimumWidth(0, 300)
        # forces the column 0 to stay at 300px (no movement)
        self.taskLayout.setVerticalSpacing(20)
        # sets spacing between buttons

        self.mainStack.addWidget(self.taskPage)
        # adds the config layout to the center of the doc

        self.pointGrabTask = QPushButton("Channel Points")
        self.streakGrabTask = QPushButton("Channel Streaks")
        self.singleGrabTask = QPushButton("Single Channel")
        self.predictionTask = QPushButton("Prediction Screen")
        self.skipToBrowser = QPushButton("Skip to browser view")
        # adds the buttons to determine task

        self.pointGrabTask.setToolTip("Tasks related to channel points")
        self.streakGrabTask.setToolTip("Tasks related to view streaks")
        self.singleGrabTask.setToolTip("Single channel's points and streak")
        self.predictionTask.setToolTip("Opens the prediction view")
        self.skipToBrowser.setToolTip("Bypass processing and enter the browser\nUse this to change the logged in Twitch account")
        # tooltips

        self.pointGrabTask.setMinimumSize(250, 40)
        self.streakGrabTask.setMinimumSize(250, 40)
        self.singleGrabTask.setMinimumSize(250, 40)
        self.predictionTask.setMinimumSize(250, 40)
        self.skipToBrowser.setMinimumSize(250, 40)
        # sets the sizes of the buttons

        self.optionsButtonTask = self.optionsButton
        self.versionTagTask = self.versionTag
        self.exitButtonTask = self.exitButton
        # creates a clone of the options and exit buttons and the version tag

        self.taskLayout.addWidget(self.pointGrabTask, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.streakGrabTask, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.singleGrabTask, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.predictionTask, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.skipToBrowser, 5, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.versionTagTask, 7, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.taskLayout.addWidget(self.exitButtonTask, 7, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.optionsButtonTask, 7, 2, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all the buttons to layout

        self.taskLayoutTopSpacer = QSpacerItem(50, 50)
        self.taskLayoutBotSpacer = QSpacerItem(50, 50)
        # adds a top and bottom spacer

        self.taskLayout.addItem(self.taskLayoutTopSpacer, 0, 1)
        self.taskLayout.addItem(self.taskLayoutBotSpacer, 6, 1)
        # adds the spacers to layout (above and below selections, to squish them a bit

        self.pointGrabTask.clicked.connect(lambda: self.taskChooser("Channel Points", 1))
        self.streakGrabTask.clicked.connect(lambda: self.taskChooser("Channel Streaks", 2))
        self.singleGrabTask.clicked.connect(lambda: self.taskChooser("Single Channel", 3))
        self.predictionTask.clicked.connect(lambda: self.taskChooser("Prediction", 4))
        self.skipToBrowser.clicked.connect(lambda: self.taskChooser("Skip to Browser", 5))
        # calls the task chooser to further check the task(s)

        self.escShortcut = QShortcut(QKeySequence("Escape"), self)
        # forms a keybind to Escape
        self.escShortcut.activated.connect(lambda: self.mainStack.setCurrentWidget(self.taskPage))
        # sets the task page as active when activated (can be used to go back from config or subtask views)



    ### Subtask Page 1 (Points-Related) ###
        
        self.subtaskPage1 = QWidget()
        # subtask page 1
        self.subtaskPage1.setObjectName("Subtask Page 1")
        # object name
        self.mainStack.addWidget(self.subtaskPage1)
        # adds to stack
        self.subtaskPage1Layout = QGridLayout(self.subtaskPage1)
        # layout for subtask 1

        self.taskChooseTopSpacerST1 = QSpacerItem(250, 150)
        # adds a spacer between the top and the first option     

        self.allPointsButton = QPushButton("All Points")
        # all points button
        self.allPointsButton.setToolTip("Get all channel points for channels in the channel list file")
        # tooltip
        self.allPointsButton.setMinimumSize(250, 50)
        # sets minimum size

        self.taskPointsAndStreaksButtonST1 = QPushButton("All Points and Streaks")
        # pre-creates a button for both streaks and points
        self.taskPointsAndStreaksButtonST1.setToolTip("Get both channel points and streaks\nof the channels in the channel list file")
        # tooltip
        self.taskPointsAndStreaksButtonST1.setMinimumSize(250, 50)
        # sets minimum size
        self.taskPointsAndStreaksButtonST1.clicked.connect(lambda: self.taskRunner(1, 2, None))
        # if the points + streaks button is pressed, calls taskRunner with task 1 subtask 2

        self.taskChooseBackSpacerST1 = QSpacerItem(250, 100)
        # adds a spacer beween the back button and the last option

        self.taskChooseBackButtonST1 = QPushButton("Back")
        # back button, in case points was not the intended selection
        self.taskChooseBackButtonST1.setToolTip("Go back to selection menu\nEscape works, too")
        # tooltip
        self.taskChooseBackButtonST1.setMinimumSize(250, 50)
        # sets minimum size
        self.taskChooseBackButtonST1.clicked.connect(lambda: self.mainStack.setCurrentWidget(self.taskPage))
        # sends back to task page

        self.subtaskPage1Layout.addItem(self.taskChooseTopSpacerST1, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the top spacer
        self.subtaskPage1Layout.addWidget(self.allPointsButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the all points button to layout
        self.subtaskPage1Layout.addWidget(self.taskPointsAndStreaksButtonST1, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the streaks + points button
        self.subtaskPage1Layout.addItem(self.taskChooseBackSpacerST1, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the spacer
        self.subtaskPage1Layout.addWidget(self.taskChooseBackButtonST1, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the back button

        self.allPointsButton.clicked.connect(lambda: self.taskRunner(1, 1, None))
        # all points calls taskRunner with task 1 subtask 1



    ### Subtask Page 2 (Streaks-Related) ###

        self.subtaskPage2 = QWidget()
        # subtask page 2
        self.subtaskPage2.setObjectName("Subtask Page 2")
        # object name
        self.mainStack.addWidget(self.subtaskPage2)
        # adds to stack
        self.subtaskPage2Layout = QGridLayout(self.subtaskPage2)
        # layout for subtask 2

        self.taskChooseTopSpacerST2 = QSpacerItem(250, 150)
        # adds a spacer between the top and the first option  

        self.allStreaksButtonST2 = QPushButton("All Streaks")
        # all streaks button
        self.allStreaksButtonST2.setToolTip("Get all streaks for channels in the channel list file")
        # tooltip
        self.allStreaksButtonST2.setMinimumSize(250, 50)
        # sets minimum size

        self.activeStreaksButtonST2 = QPushButton("Active Streaks")
        # all streaks button
        self.activeStreaksButtonST2.setToolTip("Get streaks marked as active (>1) from the channel points file")
        # tooltip
        self.activeStreaksButtonST2.setMinimumSize(250, 50)
        # sets minimum size

        self.taskPointsAndStreaksButtonST2 = QPushButton("All Points and Streaks")
        # pre-creates a button for both streaks and points
        self.taskPointsAndStreaksButtonST2.setToolTip("Get both channel points and streaks\nof the channels in the channel list file")
        # tooltip
        self.taskPointsAndStreaksButtonST2.setMinimumSize(250, 50)
        # sets minimum size
        self.taskPointsAndStreaksButtonST2.clicked.connect(lambda: self.taskRunner(1, 2, None))
        # if the points + streaks button is pressed, calls taskRunner with task 1 subtask 2

        self.taskChooseBackSpacerST2 = QSpacerItem(250, 100)
        # adds a spacer beween the back button and the last option

        self.taskChooseBackButtonST2 = QPushButton("Back")
        # back button, in case points was not the intended selection
        self.taskChooseBackButtonST2.setToolTip("Go back to selection menu\nEscape works, too")
        # tooltip
        self.taskChooseBackButtonST2.setMinimumSize(250, 50)
        # sets minimum size
        self.taskChooseBackButtonST2.clicked.connect(lambda: self.mainStack.setCurrentWidget(self.taskPage))
        # sends back to task page

        self.subtaskPage2Layout.addItem(self.taskChooseTopSpacerST2, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the top spacer
        self.subtaskPage2Layout.addWidget(self.allStreaksButtonST2, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the all streaks button to layout
        self.subtaskPage2Layout.addWidget(self.activeStreaksButtonST2, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the active streaks button to layout
        self.subtaskPage2Layout.addWidget(self.taskPointsAndStreaksButtonST2, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the streaks + points button
        self.subtaskPage2Layout.addItem(self.taskChooseBackSpacerST2, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the spacer
        self.subtaskPage2Layout.addWidget(self.taskChooseBackButtonST2, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the back button

        self.allStreaksButtonST2.clicked.connect(lambda: self.taskRunner(2, 1, None))
        # all streaks calls taskRunner with task 2 subtask 1
        self.activeStreaksButtonST2.clicked.connect(lambda: self.taskRunner(2, 2, None))
        # active streaks calls taskRunner with task 2 subtask 2



    ### Subtask Page 3 (Single Channel Points/Streaks) ###

        self.subtaskPage3 = QWidget()
        # subtask page 3
        self.subtaskPage3.setObjectName("Subtask Page 3")
        # object name
        self.mainStack.addWidget(self.subtaskPage3)
        # adds to stack
        self.subtaskPage3Layout = QGridLayout(self.subtaskPage3)
        # layout for subtask 3

        self.taskChooseTopSpacerST3 = QSpacerItem(250, 150)
        # adds a spacer between the top and the first option  

        self.taskSingleChannelNameST3 = QLineEdit()
        # a user input field for the channel name
        self.taskSingleChannelNameST3.setPlaceholderText("Channel name")
        # adds a placeholder (background) text
        self.taskSingleChannelNameST3.setToolTip("Write a channel to perform task on")
        # tooltip
        self.taskSingleChannelNameST3.setMinimumSize(250, 50)
        # sets minimum size
        self.taskSingleChannelNameST3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns the text to center

        self.taskSingleSubmitButtonST3 = QPushButton("Submit")
        # submit button to enter channel
        self.taskSingleSubmitButtonST3.setToolTip("Confirm selection")
        # tooltip
        self.taskSingleSubmitButtonST3.setMinimumSize(250, 50)
        # sets minimum size

        self.taskChooseBackSpacerST3 = QSpacerItem(250, 100)
        # adds a spacer beween the back button and the last option

        self.taskChooseBackButtonST3 = QPushButton("Back")
        # back button, in case points was not the intended selection
        self.taskChooseBackButtonST3.setToolTip("Go back to selection menu\nEscape works, too")
        # tooltip
        self.taskChooseBackButtonST3.setMinimumSize(250, 50)
        # sets minimum size
        self.taskChooseBackButtonST3.clicked.connect(lambda: self.mainStack.setCurrentWidget(self.taskPage))
        # sends back to task page

        self.subtaskPage3Layout.addItem(self.taskChooseTopSpacerST1, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the top spacer
        self.subtaskPage3Layout.addWidget(self.taskSingleChannelNameST3, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the channel name input field
        self.subtaskPage3Layout.addWidget(self.taskSingleSubmitButtonST3, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the submit channel button
        self.subtaskPage3Layout.addItem(self.taskChooseBackSpacerST3, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the back button spacer
        self.subtaskPage3Layout.addWidget(self.taskChooseBackButtonST3, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the back button

        self.taskSingleSubmitButtonST3.clicked.connect(lambda: self.taskRunner(3, 0, self.taskSingleChannelNameST3.text().strip()))
        # runs the task with command 3 and the channel name field's text
        self.taskSingleChannelNameST3.returnPressed.connect(lambda: self.taskRunner(3, 0, self.taskSingleChannelNameST3.text().strip()))
        # runs the task with command 3 and the channel name field's text



    ### Subtask Page 4 (Predictions) ###

        self.subtaskPage4 = QWidget()
        # subtask page 4
        self.subtaskPage4.setObjectName("Subtask Page 4")
        # object name
        self.mainStack.addWidget(self.subtaskPage4)
        # adds to stack
        self.subtaskPage4Layout = QGridLayout(self.subtaskPage4)
        # layout for subtask 4

        self.taskChooseTopSpacerST4 = QSpacerItem(250, 150)
        # adds a spacer between the top and the first option  

        self.taskSingleChannelNameST4 = QLineEdit()
        # a user input field for the channel name
        self.taskSingleChannelNameST4.setPlaceholderText("Channel name")
        # adds a placeholder (background) text
        self.taskSingleChannelNameST4.setToolTip("Write a channel to perform task on")
        # tooltip
        self.taskSingleChannelNameST4.setMinimumSize(250, 50)
        # sets minimum size
        self.taskSingleChannelNameST4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns the text to center

        self.taskSingleSubmitButtonST4 = QPushButton("Submit")
        # submit button to enter channel
        self.taskSingleSubmitButtonST4.setToolTip("Confirm selection")
        # tooltip
        self.taskSingleSubmitButtonST4.setMinimumSize(250, 50)
        # sets minimum size

        self.taskChooseBackButtonST4 = QPushButton("Back")
        # back button, in case points was not the intended selection
        self.taskChooseBackButtonST4.setToolTip("Go back to selection menu\nEscape works, too")
        # tooltip
        self.taskChooseBackButtonST4.setMinimumSize(250, 50)
        # sets minimum size
        self.taskChooseBackButtonST4.clicked.connect(lambda: self.mainStack.setCurrentWidget(self.taskPage))
        # sends back to task page

        self.taskChooseBackSpacerST4 = QSpacerItem(250, 100)
        # adds a spacer beween the back button and the last option

        self.subtaskPage4Layout.addItem(self.taskChooseTopSpacerST4, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the top spacer
        self.subtaskPage4Layout.addWidget(self.taskSingleChannelNameST4, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the channel name input field
        self.subtaskPage4Layout.addWidget(self.taskSingleSubmitButtonST4, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the submit channel button
        self.subtaskPage4Layout.addItem(self.taskChooseBackSpacerST4, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the spacer
        self.subtaskPage4Layout.addWidget(self.taskChooseBackButtonST4, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the back button

        self.taskSingleSubmitButtonST4.clicked.connect(lambda: self.taskRunner(4, 0, self.taskSingleChannelNameST4.text().strip()))
        # runs the task with command 4 and the channel name field's text
        self.taskSingleChannelNameST4.returnPressed.connect(lambda: self.taskRunner(4, 0, self.taskSingleChannelNameST4.text().strip()))
        # runs the task with command 4 and the channel name field's text



    ### Startup ###

        self.mainStack.setCurrentWidget(self.mainPage)
        # sets the main page as active page
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
        self.checkUpdate()
        # runs the update check to see if there's a new version of TEPM
        self.firstTimeUI()
        # runs the first time UI checker to see if the first time UI should appear or not



### Label Changer ###

    def changeLabel(self, text: str):
        """Function to change the passed label"""
        self.mainLabel.setText(text)
        # sets the progress label to match the passed text



### First Time UI ###

    def firstTimeUI(self):
        """Function to determine if the first time UI should be shown"""
        global profileName
        # global -> local (this gets set here if the folder already exists)

        if not os.path.exists(profilePath):
        # checks if the profile folder path is(n't) valid yet
            self.labelSwap.emit("No Profile folder found, creating one!")
            # user inform
            os.mkdir(profilePath)
            # makes a directory at the given path

        if not os.path.exists(textPath):
        # checks if the channel list.txt file exists yet
            self.labelSwap.emit("No Channel List text file found, creating default!")
            # user inform
            with open(textPath, "w") as clnt:
            # opens the text path location (makes a new file)
                clnt.write(f"Twitch\n"
                           f"TwitchRivals")
                # writes just Twitch and Twitch Rivals as the only channels (shows how the list works, 100% functional channels)

        self.subfolders = list(folders(profilePath))
        # stores the subfolders of the profile path (installation/Profile/)

        if self.subfolders and len(self.subfolders) == 1:
        # checks if there's a subfolder inside the Profile (whether an actual user profile exists or not)
            profileFolder = self.subfolders[0]
            # grabs the only subfolder
            head, tail = os.path.split(profileFolder)
            # splits the path of the folder into head (everything before last /) and tail (the last part)
            profileName = tail
            # sets the profile name to match the folder name
            self.labelSwap.emit(f"Found profile: {profileName}!")
            # user inform
            QTimer.singleShot(1500, self.hashLoader)
            # moves straight to hashLoader

        elif len(self.subfolders) > 1:
        # if there's more than 1 profile folder
            self.labelSwap.emit("Found multiple folders inside the TEPM/Profile/ folder!\nPlease ensure only one user profile folder is present and retry")
            # sets the text to inform
            return
            # stops the checks

        else:
        # if there's no profile subfolder yet
            self.mainStack.setCurrentWidget(self.profilePickPage)
            # sets active page to the profile picking page



### User Profile Name ###

    def userNameGrab(self):
        """Function to grab the user profile folder"""
        global profileName
        # global -> local (set if none exists)

        self.mainStack.setCurrentWidget(self.mainPage)
        # sets main page as active page
            
        self.chooseUsername = self.profileNameField.text().strip()
        # stores the username from the input field
        
        if self.chooseUsername == "":
        # if user fails to give one
            self.labelSwap.emit("No (valid) name given, setting profile to Default\nTo change this, delete or rename the folder inside /Profile/")
            # user inform
            profileName = "Default"
            # sets to Default
            waitTimer = 3500
            # sets the wait timer to 3500 ms, to allow user to read it
        else:
        # if user provides a name
            self.labelSwap.emit(f"Setting profile name to {self.chooseUsername}...")
            # user inform
            profileName = self.chooseUsername
            # stores the profile name as the chosen name
            waitTimer = 1200
            # sets the wait timer to 1200 ms, shorter text with no instructions

        QTimer.singleShot(waitTimer, self.hashLoader)
        # waits a time, then calls intermediary function



### Hash Load ###

    def hashLoader(self):
        """Function that loads the hash map to global var"""
        global hashMap
        # global -> local

        self.labelSwap.emit("Grabbing hashes...")
        # user inform

        if os.path.exists(hashFilePath):
        # if the hash file is found
            try:
            # goes to open
                with open(hashFilePath) as hsh:
                # opens the hash file path
                    hashMap = json.load(hsh)
                    # loads the hashmap
            except:
            # if it can't load it properly
                self.labelSwap.emit("Could not open the hash file, please ensure it's valid.\nTry downloading a new one from GitHub")
                # user inform
                return
        else:
        # if the hash file doesn't exist
            self.labelSwap.emit("No hashes.json file found, please download a new one from GitHub.")
            # user inform
            return

        self.configWindow()
        # calls the config window to proceed



### Configuration Window ###

    def configWindow(self):
        """Function to load the configuration window"""
        global streakMap, enableErrorLog, autoAddStreaks, autoRemoveStreaks, defaultBet, roundBalanceBet
        # global -> local

        self.labelSwap.emit("Reading config...")
        # user inform

        if os.path.exists(streakMapPath):
        # if the streak map file exists
            with open(streakMapPath, "r") as strk:
            # opens the streak map json
                streakMap = dict(json.load(strk))
                # loads the json map into variable

                enableErrorLog = streakMap.get("enableErrorsInCSV", True)
                # gets the boolean for error logging
                autoAddStreaks = streakMap.get("autoAddStreaks", True)
                # gets the boolean for auto-adding streaks
                autoRemoveStreaks = streakMap.get("autoRemoveStreaks", False)
                # gets the boolean for auto-removing streaks
                defaultBet = int(streakMap.get("defaultBet", 5000))
                # gets the integer for default bet
                roundBalanceBet = streakMap.get("roundBalanceBet", False)
                # gets the boolean for balance rounding for bets

                self.autoAddStreaksCheckbox.setChecked(autoAddStreaks)
                self.autoRemoveStreaksCheckbox.setChecked(autoRemoveStreaks)
                self.enableCSVErrorsCheckbox.setChecked(enableErrorLog)
                self.defaultBetLine.setText(f"{defaultBet}")
                self.roundBalanceBetCheckbox.setChecked(roundBalanceBet)
                # sets the check status based on the stored values
        else:
        # if the file doesn't exist
            self.mainStack.setCurrentWidget(self.configPage)
            # sets the config page visible (since config is required)
            return
            # doesn't progress

        self.mainStack.setCurrentWidget(self.taskPage)
        # sets the task page visible
        self.optionsButton.setEnabled(True)
        # enables the options button



### Modify Configuration ###

    def modifyConfigText(self):
        """Function to just set the text with a delay"""

        self.mainStack.setCurrentWidget(self.mainPage)
        # sets main page back to active

        self.labelSwap.emit("Modifying configuration...")
        # sets new text

        if self.optionReturn:
        # if user returns from options screen
            QTimer.singleShot(200, self.modifyConfig)
            # calls modifyConfig faster
        else:
        # if it's the first time
            self.optionReturn = True
            # sets the boolean to True so it gets caught
            QTimer.singleShot(800, self.modifyConfig)
            # calls modifyConfig slightly later
    
    def modifyConfig(self):
        """The function that actually modifies the config"""
        global enableErrorLog, streakMap, autoAddStreaks, autoRemoveStreaks, defaultBet, roundBalanceBet
        # global -> local

        streakMap["autoAddStreaks"] = self.autoAddStreaksCheckbox.isChecked()
        streakMap["autoRemoveStreaks"] = self.autoRemoveStreaksCheckbox.isChecked()
        streakMap["enableErrorsInCSV"] = self.enableCSVErrorsCheckbox.isChecked()
        streakMap["defaultBet"] = self.defaultBetLine.text().strip()
        streakMap["roundBalanceBet"] = self.roundBalanceBetCheckbox.isChecked()
        streakMap["exampleChannel"] = "exampleChannelID"
        # adds map settings

        autoAddStreaks = self.autoAddStreaksCheckbox.isChecked()
        autoRemoveStreaks = self.autoRemoveStreaksCheckbox.isChecked()
        enableErrorLog = self.enableCSVErrorsCheckbox.isChecked()
        defaultBet = int(self.defaultBetLine.text().strip())
        roundBalanceBet = self.roundBalanceBetCheckbox.isChecked()
        # sets the global variables based on the entry values

        with open(streakMapPath, "w") as strk:
        # opens the streak config location (or makes a new file)
            json.dump(streakMap, strk, indent=3)
            # dumps the map into file

        self.labelSwap.emit("Configuration modified")
        # changes label
        
        if self.optionReturn:
        # if the boolean is true
            self.mainStack.setCurrentWidget(self.taskPage)
            # sets visible
        else:
            QTimer.singleShot(1500, lambda: self.mainStack.setCurrentWidget(self.taskPage))
            # runs the task chooser config slower (user can see prompt)



### Update Checker ###

    def checkUpdate(self):
        """Function that checks if there's a new version of the program"""

        try:
        # tries to get tags
            gitTags = requests.get(
                gURL,
                headers={"User-Aagent": "TEPM"},
                timeout=5)
            # the request to get the github tags

            if gitTags.status_code == 200:
            # 200 is all good
                tags = gitTags.json()
                # grabs the json dictionary

                latestTagRaw = str(tags[0]["name"])
                # grabs the 0th element's name (latest)
                latestTag = latestTagRaw.replace(".", "").replace("v", "").strip()
                # strips the periods and v(ersion) identifier, cleans up
                currentTag = tepmVer.replace(".", "").strip()
                # the current stored tag doesn't have the v applied, just removes periods and whitespace

                if latestTag > currentTag:
                # if there's a newer version (higher number)
                    latestURL = "https://github.com/EllEff-Git/Twitch-External-Point-Manager/releases/latest"
                    # the URL to set
                    self.versionTag.setText(
                        f'TEPM v{self.version}<br>'
                        f'Update available: '
                        f'<a href="{latestURL}">'
                        f'{latestTagRaw}'
                        f'</a>'
                    )
                    # updates text to include a prompt + link to the newest update
                else:
                    self.versionTag.setText(f"TEPM v{self.version}\nLatest")
                    # updates text
            else:
                self.versionTag.setText(f"TEPM v{self.version}\nUpdate check failed")
                # not status 200 (error)
        except:
            self.versionTag.setText(f"TEPM v{self.version}\nUpdate check failed")
            # didn't go through at all



### Subtask Selection -> Task Run ###

    def taskChooser(self, task: str, taskNum: int):
        """Function to set the tasks to run based on chosen task(s)"""

        if taskNum == 1:
        # task 1 is channel points
            self.mainStack.setCurrentWidget(self.subtaskPage1)
            # sets subtask page 1 as active page

        elif taskNum == 2:
        # task 2 is streaks
            self.mainStack.setCurrentWidget(self.subtaskPage2)
            # sets subtask page 2 as active page

        elif taskNum == 3:
        # task 3 is single channel
            self.mainStack.setCurrentWidget(self.subtaskPage3)
            # sets subtask page 3 as active page

        elif taskNum == 4:
        # if it's 4 (prediction manager)
            self.mainStack.setCurrentWidget(self.subtaskPage4)
            # sets subtask page 4 as active page

        elif taskNum == 5:
        # if it's 5 (skips to browser for login management)
            self.mainStack.setCurrentWidget(self.mainPage)
            # sets main page as active page
            self.labelSwap.emit("Opening browser view...")
            # user inform
            QTimer.singleShot(1500, lambda: self.taskRunner(5))
            # calls taskRunner after 1.5s



### Task Run ###    

    def taskRunner(self, task:int=None, subtask:int=None, channel:str=None):
        """Function to run the selected task"""
        global overrideChannel, canRun, activeOnly, enableStreaks, enablePoints, predictChannel
        # global -> local

        self.mainStack.setCurrentWidget(self.mainPage)
        # sets main page as active page
        
        self.configLoaded.emit()
        # sends signal to inform controller the config is done
        bonusString = ""
        # empty string
        
        if task == 1:
        # task 1 is points-related
            if subtask == 1:
            # subtask 1 is just points
                enablePoints = True
                # sets the points to True (streaks stays false)
            elif subtask == 2:
            # subtask 2 is points and streaks
                enablePoints = True
                enableStreaks = True
                # sets both booleans to True
            signalStr = "Points"
            # sets the signal string to use

        elif task == 2:
        # task 2 is streaks-related
            if subtask == 1:
            # subtask 1 is all streaks
                enableStreaks = True
                # sets the streaks to True (points stays false)
            elif subtask == 2:
            # subtask 2 is active streaks
                enableStreaks = True
                activeOnly = True
                # sets the streak-related booleans to True
            signalStr = "Streaks"
            # sets the signal string to use

        elif task == 3:
        # task 3 is single channel
            overrideChannel = channel.strip()
            # sets the override channel global variable to match the passed channel name
            if overrideChannel == "" or not overrideChannel:
            # if none is set
                self.labelSwap.emit("No channel set! Please set one first")
                # user inform
                QTimer.singleShot(1250, lambda: self.taskChooser("Single Channel", 3))
                # re-runs the same window command
                return
                # doesn't proceed
            signalStr = "Single"
            # sets the signal string to use

        elif task == 4:
        # task 4 is channel predict
            predictChannel = channel.strip()
            # sets the prediction channel global variable to match the passed name
            if predictChannel == "" or not predictChannel:
            # if none is set
                predictChannel = "Twitch"
                # sets the channel to Twitch
                bonusString = "\n\n\nNo channel set, defaulted to Twitch..."
                # sets user inform string
            signalStr = "Predict"
            # sets the signal string to use

        elif task == 5:
        # task 5 is browser view
            signalStr = "Browser"
            # sets the signal string to use

        self.labelSwap.emit(f"Starting the main TEPM program...\n\nThis window will close and a new one will open...{bonusString}")
        # swaps the label once more

        if not task == 3:
        # if the task isn't to grab single channel
            overrideChannel = None
            # resets overrideChannel
        if not task == 4:
        # if the task isn't to predict
            predictChannel = None
            # resets predictChannel

        if canRun:
        # if the canRun is already set to True (returning from main)
            QTimer.singleShot(650, lambda: self.goToMainWindow(signalStr))
            # quits the starter application window with a small delay
        else:
        # if it's not True yet (program start)
            canRun = True
            # signs the "permission slip" for main window
            QTimer.singleShot(1500, lambda: self.goToMainWindow(signalStr))
            # quits the starter application window with a small delay

        

### Starter -> Main Window ###

    def goToMainWindow(self, action):
        """Function to call when a stop is needed (with a delay)"""
        self.starterDone.emit(action)
        # sends a signal to the pyQt signal to let the controller / main window know starter is ready



### Return to Menu ###

    def returner(self):
        """Function to call to send back to the start of the start window"""
        self.labelSwap.emit("Reloading start menu...")
        # user inform
        self.mainStack.setCurrentWidget(self.taskPage)
        # sets main page as active page 





### Main App Window ###

class tepmWindow(QWidget):
    """The application window class"""

    authValid = pyqtSignal(str)
    """A pyQt signal to confirm the authentication token has been validated successfully and to pass the action"""
    taskText = pyqtSignal(str)
    """A pyQt signal to set the task string"""
    balanceOverride = pyqtSignal(int)
    """A pyQt signal to temporarily override the balance (bet success)"""

    def __init__(self, state, passedProfile):
        super().__init__()

    ### Init / Basic ###

        self.state = state
        # stores the app state that holds variables
        self.version = tepmVer
        # stores the version in self

        self.channelTxtPath = textPath
        # stores the channels path
        self.overrideChannel = overrideChannel
        # stores the potential override channel
        self.channels = self.getChannelList()
        # stores the channels
        self.channelLength = len(self.channels)
        # stores the length of the channels list

        self.authToken = None
        # the auth token
        self.forceBrowserUI = False
        # boolean on whether to force the browser to stay up

        self.mainIcon = iconPath
        # the program's main icon
        self.defaultURL = "https://twitch.tv"
        # stores the default URL to use when opening the app
        self.programName = f"Twitch External Point Manager"
        # stores the program name
        self.pid = os.getpid()
        # gets the current process' ID

        self.browserView = QWebEngineView(self)
        # adds a new webengine view
        self.authInvalidAction = None
        # action the user was attempting to do before auth token failed

        self.predictChannelPoints = 0
        """Variable to store the predict channel's point balance"""
        self.detailsWindowBool = False
        """Whether the details window is alive"""
        self.modWindowBool = False
        """Whether the mod window is alive"""

        self.currentChannel = None
        """The currently selected channel, according to predictUpdateUI"""
        self.currentSize = 0
        """Stores how many buttons are rendered"""
        self.timerEnd = 0
        """Timer end point for open predictions"""

        self.predictionID = {}
        """Map that stores the prediction ID-related info"""
        self.predictionKeys = {}
        """Map that stores outcomes and buttons"""
        self.predictionNumbers = {}
        """Map that stores prediction numbers (bets, wins, etc)"""
        self.pastPredictions = {}
        """Map that stores previous prediction outcomes"""

        self.betValidator = QIntValidator(0, 250000)
        """Validator to use with the bet line to ensure it fits Twitch's rules"""

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(500, 300)
        # the window size

    ### Main Window Layout ###

        self.mainStack = QStackedWidget()
        """A stacked widget to show/hide individual pages"""

        self.mainLayout = QGridLayout()
        """Main layout that hosts every sublayout"""
        self.mainLayout.addWidget(self.mainStack)
        # adds the stack to the main layout

        self.mainLayout.setSpacing(25)
        # sets spacing between elements (vertical and horizontal)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers everything to middle
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins 

        self.setLayout(self.mainLayout)
        # sets the layout

    ### Task-Only Page ###

        self.taskPage = QWidget()
        """Task-only page widget"""
        self.taskPage.setObjectName("Task Page")
        # object name
        self.mainStack.addWidget(self.taskPage)
        # adds the page to the stack

        self.taskLayout = QGridLayout()
        """Layout for task-view only"""

    ### Tooltip / Task View ###

        self.taskPageText = QLabel()
        # a QLabel for the task progress
        self.taskPageText.setText("Loading...")
        # initial text
        self.taskPageText.setToolTip("Current operation")
        # tooltip
        self.taskPageText.setMinimumSize(350, 40)
        # sets a size to prevent being cut off
        self.taskPageText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to the center
        self.taskLayout.addWidget(self.taskPageText, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

        self.mainStack.setCurrentWidget(self.taskPage)
        # sets task page as the default active page on launch

    ### Browser Page ###

        self.browserStackPage = QWidget()
        """Browser page widget"""
        self.browserStackPage.setObjectName("Browser Layout")
        # object name
        self.mainStack.addWidget(self.browserStackPage)
        # adds the page to the stack

        self.browserLayout = QGridLayout(self.browserStackPage)
        """Layout to store browser elements"""

    ### Retry Token Button ###

        self.refreshTokenButton = QPushButton("Refresh Token")
        # a button to try to refresh the token
        self.refreshTokenButton.setFixedSize(125, 25)
        # sets a size
        self.refreshTokenButton.setToolTip("Press to attempt token re-validation")
        # tooltip

        self.refreshTokenButton.clicked.connect(lambda: self.authValidCheck(self.authInvalidAction))
        # calls the auth valid function when pressing the refresh button (passes the action user was trying to do before)

        self.browserLayout.addWidget(self.refreshTokenButton, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        # adds it to the right side of the taskView

    ### Browser ###

        self.browserPage = SilentWebPage(passedProfile, self.browserView)
        # forms a browser page from the passed profile and the browser view widget (uses the console silencer to stop useless error spam)
        self.browserView.setPage(self.browserPage)
        # sets the page to use the given properties

        self.browserView.setMinimumSize(1150, 700)
        # sets minimum size

        self.browserLayout.addWidget(self.browserView, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the browser to the grid layout
        self.browserView.setUrl(QUrl(self.defaultURL))
        # sets "default" url to open (twitch.tv)     

    ### Connections ###

        ctrl.starterWindowDone.connect(self.cssStyleLoader)
        # calls the auth grab when the page is done loading
        self.authValid.connect(self.uiStyle)
        # calls the ui function when auth token is checked
        self.taskText.connect(self.taskLabelChanger)
        # calls the task label changer when the task text changes
        ctrl.taskChange.connect(self.taskLabelChanger)
        # connects the controller signal to the task view changer function (lets super controller set the text)
        self.balanceOverride.connect(lambda bal: self.predictPointLabel.setText(f"Balance: {bal:,.0f} points"))
        # connects the balance override to the balance label to temporarily override it before an update (QoL)



    ### Point/Streak Grab UI ###

        self.pointGrabPage = QWidget()
        """Point/streak grabbing page"""
        self.pointGrabPage.setObjectName("Point Grab Page")
        # object name
        self.mainStack.addWidget(self.pointGrabPage)
        # adds the page to the stack

        self.pointGrabLayout = QGridLayout(self.pointGrabPage)
        """A layout that contains the point/streak grab elements"""

        self.progressBar = QProgressBar()
        """A progress bar for the point/streak grab progress"""
        self.progressBar.setValue(0)
        # sets initial progress (starts at 0)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }

            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)
        # customises the progress bar
        self.progressBar.setTextVisible(False)
        # disables the progress bar percentage (using index label)
        self.progressBar.setMinimumSize(300, 25)
        # sets the progress bar's size
        self.progressBar.setToolTip("Current progress")
        # tooltip
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to center

        self.channelLabel = QLabel()
        """Current point/streak task"""
        self.channelLabel.setToolTip("Current task")
        # tooltip
        self.channelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.channelLabel.setMinimumSize(300, 30)
        # sets fixed size
        self.channelLabel.setWordWrap(True)
        # allows the text to wrap, if it's too long

        self.totalLabel = QLabel()
        """Total found points"""
        self.totalLabel.setToolTip("Total point accumulation")
        # tooltip
        self.totalLabel.setText("Nothing found yet")
        # sets initial text
        self.totalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.currentLabel = QLabel()
        """Point/streak progress index label (x / y)"""
        self.currentLabel.setToolTip("Progress")
        # tooltip
        self.currentLabel.setText(f"0 / {self.channelLength}")
        # sets initial progress
        self.currentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.pointGrabLayout.addWidget(self.channelLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.pointGrabLayout.addWidget(self.progressBar, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.pointGrabLayout.addWidget(self.totalLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.pointGrabLayout.addWidget(self.currentLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the items to the layout

        self.pointGrabStopLayout = QGridLayout()
        """A layout to store the Menu / Exit buttons in point grab mode"""
        self.pointGrabLayout.addLayout(self.pointGrabStopLayout, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the main point grab layout



    ### Predict UI ###

        self.predictionPage = QWidget()
        """Predictions page"""

        self.predictLayout = QGridLayout(self.predictionPage)
        """A layout for the predictions"""
        self.mainStack.addWidget(self.predictionPage)
        # adds the page to the stack

    ### Predict Details ###

        self.predictInfoLayout = QGridLayout()
        """A nested layout that hosts basic information about the prediction(s)"""
        self.predictInfoLayout.setSpacing(20)
        # adds a little more spacing
        self.predictLayout.addLayout(self.predictInfoLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # top middle

        self.predictDetailLayout = QGridLayout()
        """A further nested layout that hosts prediction specifics (status, name, creation, pool, outcome, task)"""
        self.predictDetailLayout.setVerticalSpacing(20)
        # adds a little more vertical space
        self.predictInfoLayout.addLayout(self.predictDetailLayout, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # under the basic info, above the buttons

    ### Prediction Channel ###

        self.predictChannelLabel = QLabel(" ")
        """A label that holds the current channel name"""
        self.predictChannelLabel.setToolTip("Currently selected channel")
        # tooltip
        self.predictChannelLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 24px;
            }
        """)

        self.predictLastUpdateLabel = QLabel(" ")
        """A label that holds the last update time"""
        self.predictLastUpdateLabel.setToolTip("Last prediction data load timestamp")
        # tooltip
        self.predictLastUpdateLabel.setStyleSheet("""
            QLabel {
                color: white;
                font-style: italic;
                font-size: 13px;
            }
        """)
        self.predictLastUpdateLabel.setMinimumSize(350, 40)
        # min size
        self.predictLastUpdateLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        
        self.predictTaskLabel = QLabel(" ")
        """A label that holds the current task result/string"""
        self.predictTaskLabel.setStyleSheet("""
            QLabel {
                color: yellow;
                font-style: italic;
                font-size: 14px;
            }
        """)
        self.predictTaskLabel.setToolTip("Program status inform")
        # tooltip
        self.predictTaskLabel.setMinimumSize(350, 40)
        # min size
        self.predictTaskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictInfoLayout.addWidget(self.predictChannelLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the layout (top middle)
        self.predictInfoLayout.addWidget(self.predictLastUpdateLabel, 3, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the update timestamp label between the task label and the outcome layout
        self.predictInfoLayout.addWidget(self.predictTaskLabel, 4, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the current task label under the details layout



    ### Prediction Details ###

        self.predictStatusLabel = QLabel(" ")
        """A label that holds the prediction status (active, locked, paid out, refunded)"""
        self.predictStatusLabel.setToolTip("Prediction status")
        # tooltip
        self.predictStatusLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 17px;
            }
        """)
        # style sheet
        self.predictStatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictInfoLabel = QLabel(" ")
        """A label that holds the prediction name"""
        self.predictInfoLabel.setToolTip("Prediction name")
        # tooltip
        self.predictInfoLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-style: italic;
                font-size: 17px;
            }
        """)
        # style sheet
        self.predictInfoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictDetailLabel = QLabel(" ")
        """A label that holds the prediction details (creator, timestamp)"""
        self.predictDetailLabel.setToolTip("Prediction details")
        # tooltip
        self.predictDetailLabel.setStyleSheet("""
            QLabel {
                font-style: italic;
                font-size: 13px;
            }
        """)
        # style sheet
        self.predictDetailLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictTimerLabel = QLabel("00:00")
        """A label that holds the prediction timer (if active)"""
        self.predictTimerLabel.setToolTip("Prediction timer")
        # tooltip
        self.predictTimerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictPoolLabel = QLabel(" ")
        """A label that holds the total pool info"""
        self.predictPoolLabel.setStyleSheet("""
            QLabel {
                font-size: 15px;
            }
        """)
        # style sheet
        self.predictPoolLabel.setToolTip("Total points pool")
        # tooltip
        self.predictPoolLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        
        self.predictResultLabel = QLabel("Prediction result")
        """A label that holds the result"""
        self.predictResultLabel.setToolTip("Prediction Outcome")
        # tooltip
        self.predictResultLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-style: italic;
                font-size: 15px;
            }
        """)
        # style sheet
        
        self.predictResultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictDetailLayout.addWidget(self.predictStatusLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds status label to the 2nd nested layout (under the points)
        self.predictDetailLayout.addWidget(self.predictInfoLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds basic info label to the 2nd nested layout (under the status)
        self.predictDetailLayout.addWidget(self.predictDetailLabel, 2, 0, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop))
        # adds details label to the 2nd nested layout (under the prediction name)
        self.predictDetailLayout.addWidget(self.predictPoolLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds pool label to the 2nd nested layout (under the timer)
        self.predictDetailLayout.addWidget(self.predictTimerLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds timer label to the 2nd nested layout (under the details)
        self.predictDetailLayout.addWidget(self.predictResultLabel, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds result label to the 2nd nested layout (under the pool)

        self.predictInfoItems = [self.predictStatusLabel, self.predictInfoLabel, self.predictDetailLabel, self.predictTimerLabel, self.predictPoolLabel]
        """A list of all the prediction-related information labels"""



    ### Predict Button/Point Layout ###

        self.predictOutcomeLayout = QHBoxLayout()
        """A nested layout that hosts the bet selectors and point totals"""
        self.predictOutcomeLayout.setSpacing(15)
        # sets lower spacing
        self.predictOutcomeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns center
        self.predictInfoLayout.addLayout(self.predictOutcomeLayout, 5, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the info layout (under the labels)

    ### Predict Outcome 1 ###

        self.predictOutcome1 = QWidget()
        """A QWidget to hold the option 1 elements"""
        self.predictOutcome1Layout = QVBoxLayout()
        """A vertical layout to hold option 1 elements"""
        self.predictOutcome1.setLayout(self.predictOutcome1Layout)
        # sets layout

        self.predictPayout1 = QLabel("0x")
        """Prediction option 1 payout multiplier label"""
        self.predictPayout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout1.setToolTip("Prediction outcome multiplier")
        # top label 1

        self.predictOption1 = QPushButton(" ")
        """Prediction option 1 button"""
        self.predictOption1.setToolTip("Outcome 1")
        # bet option 1

        self.predictPoints1 = QLabel("0")
        """Prediction option 1 point pool label"""
        self.predictPoints1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints1.setToolTip("Prediction outcome details")
        # bottom label 1

        self.predictOutcome1Layout.addWidget(self.predictPayout1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome1Layout.addWidget(self.predictOption1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome1Layout.addWidget(self.predictPoints1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome1)
        # adds the overall widget to the layout

    ### Predict Outcome 2 ###

        self.predictOutcome2 = QWidget()
        """A QWidget to hold the option 2 elements"""
        self.predictOutcome2Layout = QVBoxLayout()
        """A vertical layout to hold option 2 elements"""
        self.predictOutcome2.setLayout(self.predictOutcome2Layout)
        # sets layout

        self.predictPayout2 = QLabel("0x")
        """Prediction option 2 payout multiplier label"""
        self.predictPayout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout2.setToolTip("Prediction outcome multiplier")
        # top label 2

        self.predictOption2 = QPushButton(" ")
        """Prediction option 2 button"""
        self.predictOption2.setToolTip("Outcome 2")
        # bet option 2

        self.predictPoints2 = QLabel("0")
        """Prediction option 2 point pool label"""
        self.predictPoints2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints2.setToolTip("Prediction outcome details")
        # bottom label 2

        self.predictOutcome2Layout.addWidget(self.predictPayout2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome2Layout.addWidget(self.predictOption2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome2Layout.addWidget(self.predictPoints2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome2)
        # adds the overall widget to the layout

    ### Predict Outcome 3 ###

        self.predictOutcome3 = QWidget()
        """A QWidget to hold the option 3 elements"""
        self.predictOutcome3Layout = QVBoxLayout()
        """A vertical layout to hold option 3 elements"""
        self.predictOutcome3.setLayout(self.predictOutcome3Layout)
        # sets layout

        self.predictPayout3 = QLabel("0x")
        """Prediction option 3 payout multiplier label"""
        self.predictPayout3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout3.setToolTip("Prediction outcome multiplier")
        # top label 3

        self.predictOption3 = QPushButton(" ")
        """Prediction option 3 button"""
        self.predictOption3.setToolTip("Outcome 3")
        # bet option 3

        self.predictPoints3 = QLabel("0")
        """Prediction option 3 point pool label"""
        self.predictPoints3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints3.setToolTip("Prediction outcome details")
        # bottom label 3

        self.predictOutcome3Layout.addWidget(self.predictPayout3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome3Layout.addWidget(self.predictOption3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome3Layout.addWidget(self.predictPoints3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome3)
        # adds the overall widget to the layout

    ### Predict Outcome 4 ###

        self.predictOutcome4 = QWidget()
        """A QWidget to hold the option 4 elements"""
        self.predictOutcome4Layout = QVBoxLayout()
        """A vertical layout to hold option 4 elements"""
        self.predictOutcome4.setLayout(self.predictOutcome4Layout)
        # sets layout

        self.predictPayout4 = QLabel("0x")
        """Prediction option 4 payout multiplier label"""
        self.predictPayout4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout4.setToolTip("Prediction outcome multiplier")
        # top label 4

        self.predictOption4 = QPushButton(" ")
        """Prediction option 4 button"""
        self.predictOption4.setToolTip("Outcome 4")
        # bet option 4

        self.predictPoints4 = QLabel("0")
        """Prediction option 4 point pool label"""
        self.predictPoints4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints4.setToolTip("Prediction outcome details")
        # bottom label 4

        self.predictOutcome4Layout.addWidget(self.predictPayout4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome4Layout.addWidget(self.predictOption4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome4Layout.addWidget(self.predictPoints4, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome4)
        # adds the overall widget to the layout

    ### Predict Outcome 5 ###

        self.predictOutcome5 = QWidget()
        """A QWidget to hold the option 5 elements"""
        self.predictOutcome5Layout = QVBoxLayout()
        """A vertical layout to hold option 5 elements"""
        self.predictOutcome5.setLayout(self.predictOutcome5Layout)
        # sets layout

        self.predictPayout5 = QLabel("0x")
        """Prediction option 5 payout multiplier label"""
        self.predictPayout5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout5.setToolTip("Prediction outcome multiplier")
        # top label 5

        self.predictOption5 = QPushButton(" ")
        """Prediction option 5 button"""
        self.predictOption5.setToolTip("Outcome 5")
        # bet option 5

        self.predictPoints5 = QLabel("0")
        """Prediction option 5 point pool label"""
        self.predictPoints5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints5.setToolTip("Prediction outcome details")
        # bottom label 5

        self.predictOutcome5Layout.addWidget(self.predictPayout5, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome5Layout.addWidget(self.predictOption5, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome5Layout.addWidget(self.predictPoints5, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome5)
        # adds the overall widget to the layout

    ### Predict Outcome 6 ###

        self.predictOutcome6 = QWidget()
        """A QWidget to hold the option 6 elements"""
        self.predictOutcome6Layout = QVBoxLayout()
        """A vertical layout to hold option 6 elements"""
        self.predictOutcome6.setLayout(self.predictOutcome6Layout)
        # sets layout

        self.predictPayout6 = QLabel("0x")
        """Prediction option 6 payout multiplier label"""
        self.predictPayout6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout6.setToolTip("Prediction outcome multiplier")
        # top label 6

        self.predictOption6 = QPushButton(" ")
        """Prediction option 6 button"""
        self.predictOption6.setToolTip("Outcome 6")
        # bet option 6

        self.predictPoints6 = QLabel("0")
        """Prediction option 6 point pool label"""
        self.predictPoints6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints6.setToolTip("Prediction outcome details")
        # bottom label 6

        self.predictOutcome6Layout.addWidget(self.predictPayout6, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome6Layout.addWidget(self.predictOption6, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome6Layout.addWidget(self.predictPoints6, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome6)
        # adds the overall widget to the layout

    ### Predict Outcome 7 ###

        self.predictOutcome7 = QWidget()
        """A QWidget to hold the option 7 elements"""
        self.predictOutcome7Layout = QVBoxLayout()
        """A vertical layout to hold option 7 elements"""
        self.predictOutcome7.setLayout(self.predictOutcome7Layout)
        # sets layout

        self.predictPayout7 = QLabel("0x")
        """Prediction option 7 payout multiplier label"""
        self.predictPayout7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout7.setToolTip("Prediction outcome multiplier")
        # top label 7

        self.predictOption7 = QPushButton(" ")
        """Prediction option 7 button"""
        self.predictOption7.setToolTip("Outcome 7")
        # bet option 7

        self.predictPoints7 = QLabel("0")
        """Prediction option 7 point pool label"""
        self.predictPoints7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints7.setToolTip("Prediction outcome details")
        # bottom label 7

        self.predictOutcome7Layout.addWidget(self.predictPayout7, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome7Layout.addWidget(self.predictOption7, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome7Layout.addWidget(self.predictPoints7, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome7)
        # adds the overall widget to the layout

    ### Predict Outcome 8 ###

        self.predictOutcome8 = QWidget()
        """A QWidget to hold the option 8 elements"""
        self.predictOutcome8Layout = QVBoxLayout()
        """A vertical layout to hold option 8 elements"""
        self.predictOutcome8.setLayout(self.predictOutcome8Layout)
        # sets layout

        self.predictPayout8 = QLabel("0x")
        """Prediction option 8 payout multiplier label"""
        self.predictPayout8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout8.setToolTip("Prediction outcome multiplier")
        # top label 8

        self.predictOption8 = QPushButton(" ")
        """Prediction option 8 button"""
        self.predictOption8.setToolTip("Outcome 8")
        # bet option 8

        self.predictPoints8 = QLabel("0")
        """Prediction option 8 point pool label"""
        self.predictPoints8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints8.setToolTip("Prediction outcome details")
        # bottom label 8

        self.predictOutcome8Layout.addWidget(self.predictPayout8, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome8Layout.addWidget(self.predictOption8, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome8Layout.addWidget(self.predictPoints8, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome8)
        # adds the overall widget to the layout

    ### Predict Outcome 9 ###

        self.predictOutcome9 = QWidget()
        """A QWidget to hold the option 9 elements"""
        self.predictOutcome9Layout = QVBoxLayout()
        """A vertical layout to hold option 9 elements"""
        self.predictOutcome9.setLayout(self.predictOutcome9Layout)
        # sets layout

        self.predictPayout9 = QLabel("0x")
        """Prediction option 9 payout multiplier label"""
        self.predictPayout9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout9.setToolTip("Prediction outcome multiplier")
        # top label 9

        self.predictOption9 = QPushButton(" ")
        """Prediction option 9 button"""
        self.predictOption9.setToolTip("Outcome 9")
        # bet option 9

        self.predictPoints9 = QLabel("0")
        """Prediction option 9 point pool label"""
        self.predictPoints9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints9.setToolTip("Prediction outcome details")
        # bottom label 9

        self.predictOutcome9Layout.addWidget(self.predictPayout9, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome9Layout.addWidget(self.predictOption9, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome9Layout.addWidget(self.predictPoints9, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome9)
        # adds the overall widget to the layout

    ### Predict Outcome 10 ###

        self.predictOutcome10 = QWidget()
        """A QWidget to hold the option 10 elements"""
        self.predictOutcome10Layout = QVBoxLayout()
        """A vertical layout to hold option 10 elements"""
        self.predictOutcome10.setLayout(self.predictOutcome10Layout)
        # sets layout

        self.predictPayout10 = QLabel("0x")
        """Prediction option 10 payout multiplier label"""
        self.predictPayout10.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout10.setToolTip("Prediction outcome multiplier")
        # top label 10

        self.predictOption10 = QPushButton(" ")
        """Prediction option 10 button"""
        self.predictOption10.setToolTip("Outcome 10")
        # bet option 10

        self.predictPoints10 = QLabel("0")
        """Prediction option 10 point pool label"""
        self.predictPoints10.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints10.setToolTip("Prediction outcome details")
        # bottom label 10

        self.predictOutcome10Layout.addWidget(self.predictPayout10, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome10Layout.addWidget(self.predictOption10, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcome10Layout.addWidget(self.predictPoints10, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all elements to layout

        self.predictOutcomeLayout.addWidget(self.predictOutcome10)
        # adds the overall widget to the layout

    ### Predict Outcome Lists ###

        self.predictOutcomeWidgets = [self.predictOutcome1, self.predictOutcome2, self.predictOutcome3,
                                    self.predictOutcome4, self.predictOutcome5, self.predictOutcome6,
                                    self.predictOutcome7, self.predictOutcome8, self.predictOutcome9,
                                    self.predictOutcome10]
        """A list of prediction betting widgets (host the top/bottom labels + button)"""

        self.predictMultipliers = [self.predictPayout1, self.predictPayout2, self.predictPayout3, self.predictPayout4,
                                self.predictPayout5, self.predictPayout6, self.predictPayout7, self.predictPayout8,
                                self.predictPayout9, self.predictPayout10]
        """A list of prediction payout labels (top)"""

        self.predictButtonList = [self.predictOption1, self.predictOption2, self.predictOption3, 
                               self.predictOption4, self.predictOption5, self.predictOption6,
                               self.predictOption7, self.predictOption8, self.predictOption9, self.predictOption10]
        """A list of prediction option buttons"""

        self.predictPoints = [self.predictPoints1, self.predictPoints2, self.predictPoints3, self.predictPoints4, 
                            self.predictPoints5, self.predictPoints6, self.predictPoints7, self.predictPoints8,
                            self.predictPoints9, self.predictPoints10]
        """A list of prediction point pool labels (bottom)"""

    ### Outcome Widget Policing ###

        for outcome in self.predictOutcomeWidgets:
        # goes through each widget
            outcome.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed
            )
            # sets a size policy

    ### Bet Button Grouping ###

        self.buttonGroup = QButtonGroup()
        """A group of prediction buttons"""
        self.buttonGroup.setExclusive(True)
        # sets exclusive (only one can be on at once)

        for button in self.predictButtonList:
        # goes through each button in the list of buttons
            button.setMinimumSize(100, 40)
            # sets minimum size
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )
            # sets the sizes to ideally match the largest
            button.setCheckable(True)
            # makes them toggleable
            button.setStyleSheet("""
                QPushButton {
                    padding: 2px 5px;
                }
            """)
            # adds padding inside (2 top/bot, 5 left/right)
            self.buttonGroup.addButton(button)
            # adds the button to the group

    

    ### Bet / Balance ###

        self.channelPointLayout = QGridLayout()
        """A layout that holds the current bet and balance labels"""
        self.channelPointLayout.setVerticalSpacing(10)
        # smaller spacing than most
        self.predictInfoLayout.addLayout(self.channelPointLayout, 6, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the higher up prediction layout

        self.currentBetLabel = QLabel("Current Bet")
        """A label that holds the current bet amount (total per channel)"""
        self.currentBetLabel.setToolTip("Total bet for this prediction in this channel")
        # tooltip
        self.currentBetLabel.setMinimumSize(350, 50)
        # min size
        self.currentBetLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictPointLabel = QLabel(" ")
        """A label that holds the current channel's point balance"""
        self.predictPointLabel.setToolTip("Current balance for this channel")
        # tooltip
        self.predictPointLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-style: italic;
                font-size: 19px;
                color: #0DD141;
            }
        """)
        # style sheet
        self.predictPointLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.channelPointLayout.addWidget(self.predictPointLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the channel point layout (below the bet pools/buttons)
        self.channelPointLayout.addWidget(self.currentBetLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the main info layout below the balance



    ### Predict Actions ###

        self.predictSuperLayout = QGridLayout()
        """Layout that holds prediction elements (extra/bet buttons)"""
        self.predictLayout.addLayout(self.predictSuperLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout under the info/details layout

        self.predictBetLayout = QGridLayout()
        """Layout that holds the betting elements (amount + bet buttons)"""
        self.predictSuperLayout.addLayout(self.predictBetLayout, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds into the super layout to the right of the mod buttons etc (col 1)

        self.predictBetSpacer = QSpacerItem(200, 5)
        """Spacer that pushes the bet buttons down"""

        self.predictAmountLine = QLineEdit()
        """Way to customise the bet amount (int entry)"""
        self.predictAmountLine.setToolTip("How many channel points to bet")
        # tooltip
        self.predictAmountLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to the center
        self.predictAmountLine.setPlaceholderText("Bet Amount (max: 250,000)")
        # sets background text
        self.predictAmountLine.setValidator(self.betValidator)
        # sets a validator to only accept digits with a max bet of 250000
        self.predictAmountLine.setMinimumSize(200, 40)
        # min size

        self.predictBetButton = QPushButton("Bet")
        """Confirm bet button"""
        self.predictBetButton.setToolTip("Confirm bet")
        # tooltip
        self.predictBetButton.setMinimumSize(70, 40)
        # min size

        self.maxBetButton = QPushButton("Max")
        """Button to bet max amount"""
        self.maxBetButton.setToolTip("Set max bet\nUses 250,000 or full balance")
        # tooltip
        self.maxBetButton.setMinimumSize(70, 40)
        # min size

        self.defaultBetButton = QPushButton("Default")
        """Button to bet default amount"""
        self.defaultBetButton.setToolTip(f"Set default bet ({int(defaultBet):,.0f})\nIf using rounding, rounds to nearest {int(defaultBet):,.0f} instead")
        # tooltip
        self.defaultBetButton.setMinimumSize(70, 40)
        # min size

        self.predictSuperLayout.addItem(self.predictBetSpacer, 0, 1, 1, 2)
        # the spacer goes above everything else, spans both columns
        self.predictBetLayout.addWidget(self.predictAmountLine, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictBetLayout.addWidget(self.maxBetButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictBetLayout.addWidget(self.defaultBetButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictBetLayout.addWidget(self.predictBetButton, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # the bet line, buttons - all go below the prediction details

        self.predictBetButton.clicked.connect(self.predictIntermediary)
        # connects the bet button to the predict intermediary
        self.defaultBetShortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        # forms a keybind for the bet button
        self.defaultBetShortcut.activated.connect(self.predictIntermediary)
        # connects the keybind to the predict intermediary

        self.maxBetButton.clicked.connect(lambda: self.betMasker("Max"))
        # connects the max bet button to the bet masking function
        self.maxBetShortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        # forms a keybind for max bet
        self.maxBetShortcut.activated.connect(lambda: self.betMasker("Max"))
        # connects the keybind to the bet masking function

        self.defaultBetButton.clicked.connect(lambda: self.betMasker("Default"))
        # connects the default bet button to the bet masking function
        self.defaultBetShortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        # forms a keybind for default bet
        self.defaultBetShortcut.activated.connect(lambda: self.betMasker("Default"))
        # connects the keybind to the bet masking function

        self.clearBetShortuct = QShortcut(QKeySequence("Ctrl+Y"), self)
        # forms a keybind for clearing the bet field
        self.clearBetShortuct.activated.connect(lambda: self.betMasker("Clear"))
        # connects the keybind to the bet masking function

        self.doubleBetShortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        # forms a keybind for doubling the current bet
        self.doubleBetShortcut.activated.connect(lambda: self.betMasker("Double"))
        # connects the keybind to the bet masking function

        self.halveBetShorcut = QShortcut(QKeySequence("Ctrl+H"), self)
        # forms a keybind for halving the current bet
        self.halveBetShorcut.activated.connect(lambda: self.betMasker("Halve"))
        # connects the keybind to the bet masking function

        self.savePredictionShorcut = QShortcut(QKeySequence("Ctrl+S"), self)
        # forms a keybind for saving the prediction history
        self.savePredictionShorcut.activated.connect(self.savePredictions)
        # connects the keybind to the prediction saving function



    ### Extra Actions ###

        self.extraButtonLayout = QGridLayout()
        """A layout that contains the additional buttons (mod, details, history)"""
        self.extraButtonLayout.setObjectName("Menu/Exit Button Layout")
        # object name
        self.predictSuperLayout.addLayout(self.extraButtonLayout, 1, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # aligns to the right to go closer to the prediction buttons (spans 2 rows to fit next to the channel change)

        self.modButton = QPushButton("Mod View")
        """Button to open mod view"""
        self.modButton.setToolTip("Open the moderator window")
        # tooltip
        self.modButton.setMinimumSize(80, 40)
        # min size

        self.detailsButton = QPushButton("Details")
        """Button to display further information about the bet"""
        self.detailsButton.setToolTip("Open the prediction details window")
        # tooltip
        self.detailsButton.setMinimumSize(80, 40)
        # min size

        self.historyButton = QPushButton("History")
        """Button to display further information about past user bets"""
        self.historyButton.setToolTip("Open the prediction history window")
        # tooltip
        self.historyButton.setMinimumSize(80, 40)
        # min size

        self.helpButton = QPushButton("Help")
        """Button to display a help window"""
        self.helpButton.setToolTip("Open the help window")
        # tooltip
        self.helpButton.setMinimumSize(80, 40)
        # min size

        self.extraButtonLayout.addWidget(self.modButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.extraButtonLayout.addWidget(self.detailsButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.extraButtonLayout.addWidget(self.helpButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.extraButtonLayout.addWidget(self.historyButton, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all buttons to the button layout

        self.modButton.clicked.connect(lambda: self.modCheck("Window"))
        # connects the mod button to the mod check (-> mod view, if mod)
        self.detailsButton.clicked.connect(lambda: ctrl.startDetailSignal.emit())
        # connects the detail button to the details window
        self.helpButton.clicked.connect(lambda: ctrl.startHelpSignal.emit())
        # connects the help button to the help window
        self.historyButton.clicked.connect(lambda: (self.savePredictions, ctrl.startHistorySignal.emit()))
        # connects the history button to the prediction save function and history window
    


    ### Channel Swap ###

        self.predictChannelLayout = QGridLayout()
        """A layout that holds the channel swapping elements (channel entry, change button)"""
        self.predictSuperLayout.addLayout(self.predictChannelLayout, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the layout under the bet layout

        self.predictChannelLine = QLineEdit()
        """Change the channel (text entry)"""
        self.predictChannelLine.setToolTip("Enter another streamer here and press Change (or Enter) to move to their stream")
        # tooltip
        self.predictChannelLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to center
        self.predictChannelLine.setPlaceholderText("Change Channel")
        # change channel text
        self.predictChannelLine.setMinimumSize(200, 40)
        # min size

        self.predictChannelSwapButton = QPushButton("Change")
        """Change the channel (button)"""
        self.predictChannelSwapButton.setToolTip("Confirm stream change")
        # tooltip
        self.predictChannelSwapButton.setMinimumSize(70, 40)
        # min size

        self.predictChannelLayout.addWidget(self.predictChannelLine, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictChannelLayout.addWidget(self.predictChannelSwapButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout (under the bets)

        self.predictChannelSwapButton.clicked.connect(lambda: self.predictUI("Swap"))
        # connects the swap button to the UI swapping
        self.predictChannelLine.returnPressed.connect(lambda: self.predictUI("Swap"))
        # connects pressing enter (return) to the UI swapping
        ctrl.newPData.connect(self.predictUpdateUI)
        # connects the new prediction data signal to the predict UI updater



    ### Exit UI ###

        self.stopLayout = QGridLayout()
        """A layout that contains the Main and Exit buttons"""
        self.stopLayout.setHorizontalSpacing(35)
        # 30 px gaps
        self.mainLayout.addLayout(self.stopLayout, 4, 0)
        # adds the layout at the very bottom location
        
        self.menuButton = QPushButton("Menu")
        """A button to return to the menu"""
        self.menuButton.setToolTip("Return to the main menu\nCloses this window to reopen the starter")
        # tooltip
        self.menuButton.setMinimumSize(150, 50)
        # size

        self.exitButton = QPushButton("Exit")
        """A button to Exit"""
        self.exitButton.setToolTip("Quit the application")
        # tooltip
        self.exitButton.setMinimumSize(150, 50)
        # size

        self.stopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.stopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds all the items to the layout

        self.menuButton.clicked.connect(lambda: self.backToTheLobby("Menu"))
        # connects to the menu
        self.exitButton.clicked.connect(self.backToTheLobby)
        # connects to the exit function



    ### Element Lists ###

        self.pointGrabItems = [self.progressBar, self.channelLabel, self.totalLabel, self.currentLabel]
        """A list of point grab elements"""

        self.predictItems = [self.predictChannelLabel, self.predictStatusLabel, self.predictLastUpdateLabel,
                            self.predictInfoLabel, self.predictDetailLabel, self.predictTimerLabel,
                            self.predictPoolLabel, self.predictResultLabel, self.predictTaskLabel,
                            self.currentBetLabel, self.predictPointLabel, self.predictAmountLine, 
                            self.predictBetButton, self.maxBetButton, self.defaultBetButton, 
                            self.modButton, self.detailsButton, self.helpButton, 
                            self.historyButton, self.predictChannelLine, self.predictChannelSwapButton]
        """A list of prediction elements"""



### Browser Window UI ###

    def browserWindow(self):
        """A function to determine if the browser view should appear or not"""
        # if the status is False (auth token not valid, need to log in or something), or browser-only is enabled (then it should just be this window)
        self.mainStack.setCurrentWidget(self.browserStackPage)
        # sets the browser page as the active view
        self.refreshTokenButton.hide()
        # hides the refresh button (not a question of token validity)
        self.eop()
        # shows the end of program/process buttons



### Headless UI ###

    def headlessUI(self, action:str):
        """A function to add the headless UI layout widgets (points/streaks)"""

        if action == "Points":
        # if the point grabbing is enabled, streaks disabled
            self.channelLabel.setText("Starting point grabber...")
            # sets initial text

        elif action == "Streaks":
        # if the point grabbing is disabled, streaks enabled
            self.channelLabel.setText("Starting streak grabber...")
            # sets initial text

        else:
        # something else?
            self.channelLabel.setText("Starting grabber...")
            # sets initial text

        if overrideChannel:
        # if the override channel is set (doesn't really need a progress bar, 1/1)

            self.totalLabel.hide()
            self.currentLabel.hide()
            self.progressBar.hide()
            # hides both point/streak labels + progress bar

            self.mainStack.setCurrentWidget(self.pointGrabPage)
            # sets the point grab page as visible

        else:
        # if override isn't set (must be a list)

            self.totalLabel.setText("Nothing found yet")
            # sets initial text
            self.currentLabel.setText(f"0 / {len(self.channels)}")
            # sets the first channel text
            self.progressBar.setValue(0)
            # resets progress bar

            self.progressBar.show()
            self.channelLabel.show()
            self.totalLabel.show()
            self.currentLabel.show()
            # shows the items

            self.mainStack.setCurrentWidget(self.pointGrabPage)
            # sets the point grab page as visible



### Progress Handler ###

    def handleProgress(self, progressDict: dict):
        """A function to manage the progress bar and channel name"""

        dictType = progressDict["type"]
        # the type of dictionary sent (full or single)

        if dictType == "Full":
        # if the dictionary is a full one (going through a list of channels)

            channel = progressDict["channel"]
            # the channel name (str)
            index = progressDict["index"]
            # the channel's position in the list (0:X)
            pointsOn = progressDict["pointsOn"]
            # boolean for whether points are being checked
            points = progressDict["points"]
            # point count (int)
            error = progressDict["error"]
            # boolean for whether an error occurred
            total = progressDict["total"]
            # the total points so far
            streaksOn = progressDict["streaksOn"]
            # boolean for whether streaks are being checked
            streak = progressDict["streak"]
            # the current channel's streak
            expiryDateRaw = progressDict["expiresAt"]
            # grabs all the relevant information from the passed dictionary
            if expiryDateRaw:
            # if it's set and not False
                expiryDateUTC = datetime.datetime.fromisoformat(expiryDateRaw.replace("Z", "+00:00"))
                # formats it to datetime 
                expiryDateLocal = expiryDateUTC.astimezone()
                # swaps to current timezone
                expiryDate = expiryDateLocal.strftime("%B %d at %I:%M %p").replace(" 0", " ")
                # finalizes it into eg. "April 21 at 11:06 AM" (the example I had)
            else:
                expiryDate = False
                # disables

            percentage = int(((index + 1) / self.channelLength ) * 100)
            # calculates the current percentage (index+1 out of the total = 0-1 * 100 = percentage)

            self.progressBar.setValue(percentage)
            # sets the progress bar value

            if streaksOn:
            # if streaks are being checked
                if streak > 0:
                # if there's a streak
                    streakString = f"streak of {streak}"
                    # forms a string with the streak

                    if streak < 10:
                    # if the streak is > 0 but < 10
                        if streak < 7:
                        # if the streak is < 7
                            if streak < 3:
                            # if the streak is < 3
                                streakPoints = ((streak - 1) * 350)
                                # total is 350 or 0 (either it's 2 -> 1 or 1 -> 0)
                            elif streak == 3:
                            # streak is exactly 3
                                streakPoints = (1050)
                                # total is just 1050 (3 * 350)
                            elif streak == 4:
                            # streak is exactly 4
                                streakPoints = (1050 + 400)
                                # total is 1050 for first 3 days + 400 for 4th day (only custom value)
                            elif streak == 5:
                            # streak is exactly 5
                                streakPoints = (1050 + 400 + 900)
                                # total is 1050 for 3, 400 for 4 and 900 for 5
                            else:
                            # 7 > streak > 5
                                streakPoints = (streak - 5) * 450
                                # calculates the amount over 5
                                streakPoints += (1050 + 400 + 900)
                                # adds the first 5 days worth
                        elif streak == 7:
                        # streak is exactly 7
                            streakPoints = (1050 + 2200)
                            # adds up the points earned in the first 7 days (1050 + (4 * 450 + 400))
                        else:
                        # 10 > streak > 7
                            streakPoints = ((streak - 7) * 450)
                            # calculates the amount over 7
                            streakPoints += (1050 + 2200)
                            # adds the first 7 days worth
                    elif streak == 10:
                    # if the streak is exactly 10
                        streakPoints = (1050 + 2200 + 1800)
                        # adds up the points earned from first 10 days
                    else:
                    # streak is > 10
                        streakPoints = (1050 + 2200 + 1800)
                        # first calculates the first 10 days of points
                        batches, remainder = divmod((streak - 10), 5)
                        # divides the streak-10 by 5 (batches of streaks)
                        streakPoints += (batches * (450 * 6))
                        # adds up the batches (5 * 450 for the days, +450 per batch for bonus)
                        streakPoints += (remainder * 450)
                        # adds up the remainder (450 per day)

                else:
                # if the streak is 0
                    streakString = f"no active streak"
                    # forms a none-streak string
                    streakPoints = 0
                    # point total is 0

            if pointsOn:
            # if point-checking is enabled
                if points == "Not checked":
                # if the points have a set string
                    pointString = f""
                    # sets the point string to empty
                    midString = "A"
                    # makes the midString "A" -> "A streak of"
                else:
                # if the points are set to something else (a number)
                    pointString = f"{points:,} points found"
                    # formats the number to use formatting (no decimals, thousand comma)
                    if streaksOn:
                    # if streaks are enabled
                        midString = f" and a"
                        # "x points found and a streak of"

                if total == "Not checked":
                # if the total is unchecked (no point gathering)
                    totalString = f""
                    # sets to empty
                else:
                # if the total is not that (number)
                    totalString = f"Points across channels: {total:,}"
                    # formats the total number

                if error:
                # if there's an error reported
                    self.channelLabel.setText(f"Error with {channel}, couldn't get points")
                    # sets an error text
                else:
                # if no error
                    if streaksOn:
                    # if the streaks are enabled
                        if expiryDate:
                        # if the expiry date is set
                            if streak > 0:
                            # active, real streak
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nThis streak is worth {streakPoints:,.0f} points")
                                # sets the text to match
                            else:
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}")
                                # points, no streak length (set string) and no streak points
                        else:
                        # if there's an expiry date
                            if streak > 0:
                            # active, real streak
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nThis streak is worth {streakPoints:,.0f} points\nStreak expiring at {expiryDate}!")
                                # sets warning
                            else:
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nStreak expiring at {expiryDate}!")
                                # sets the text to match
                    else:
                    # streaks disabled
                        self.channelLabel.setText(f"{pointString} for {channel}!")
                        # sets the text to match

                self.totalLabel.setText(f"{totalString}")
                # sets the total string to match

            else:
            # if point-checking isn't enabled (must mean streaks are)
                self.totalLabel.setText("")
                # clears the total label
                if error:
                # if there's an error
                    self.channelLabel.setText(f"Error with {channel}, couldn't get streak")
                    # sets an error text
                else:
                # if no error

                    streakVerbose = ""
                    # empty placeholder string

                    if 35 < streak < 366:
                    # doesn't trigger any checks if below 36 or above 366
                        if streak == 36 or streak == 37:
                        # streak is 10% of a year
                            streakVerbose = "Every journey begins with a single step... and you're already 10% there!"
                        elif streak == 91 or streak == 92:
                        # streak is 25% of a year
                            streakVerbose = "Imagine you got paid a dollar for every 365-day streak... you'd be up to a quarter now!"
                        elif streak == 182 or streak == 183:
                        # streak is 50% of a year
                            streakVerbose = "Did you know migratory birds experience shifts in their magnetic orientation every 6 months or so?"
                        elif 355 <= streak <= 359:
                        # streak is between 355 and 359
                            streakVerbose = "Closing in on a year!"
                        elif 360 <= streak <= 364:
                        # streak is between 360 and 364
                            streakVerbose = "You're basically there!"
                        elif streak == 365 or streak == 366:
                        # streak is a year
                            streakVerbose = "Happy 1st streakaversary! What a milestone <3"
                    elif streak > 729:
                    # streak is over 1y364d
                        if streak % 365 == 0 or streak % 366 == 0:
                            # if the streak is divisible by 365 or 366 and leaves nothing

                            year = int(streak // 365)
                            # stores the year to 0 decimal points (since 366 can also fit here, it could return Y.00273972602)

                            if (year % 100) > 3:
                            # checks if the streak being divided lands between 10 and 20 ()
                                suffix = "th"
                                # if yes, suffix is n"th"
                            else:
                            # if not
                                suffix = {2: "nd", 3: "rd"}.get(year % 10, "th")
                                # suffix is selected separately ("2nd" or "3rd", falls back to "th" if doesn't match 2 or 3)
                            
                            streakVerbose = f"Happy {year}{suffix} streakaversary!"
                            # string with year + suffix (2nd, 3rd or nth)

                    if streak == 0:
                    # if the streak is 0
                        self.channelLabel.setText(f"{channel} has no active streak!")
                        # no streak text
                    elif streak < 100 and (str(streak).startswith("8") or streak == 18 or streak == 11):
                    # if streak is <100, and one of: the first number of streak is an 8 (eighty-X or just 8) or it's 11 or 18
                        if not expiryDate:
                        # no expiry date
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!\nThis streak is worth {streakPoints:,.0f} points!\n{streakVerbose}")
                            # sets the text to match (it has "an" as prefix, not "a")
                        else:
                        # if there's a date
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!\nThis streak is worth {streakPoints:,.0f} points!\n{streakVerbose}\nStreak expires at {expiryDate}!")
                            # sets the text to match (it has "an" as prefix, not "a")
                    else:
                        if not expiryDate:
                        # no expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!\nThis streak is worth {streakPoints:,.0f} points!\n{streakVerbose}")
                            # sets the text to match
                        else:
                        # yes expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!\nThis streak is worth {streakPoints:,.0f} points!\n{streakVerbose}\nStreak expires at {expiryDate}!")
                            # sets text with streak warning

            self.currentLabel.setText(f"{(index + 1)} / {self.channelLength}")
            # sets the current channel index string
        
        elif dictType == "Single":
        # if the dictionary is a single channel
            channel = progressDict["channel"]
            # the channel name (str)
            points = progressDict["points"]
            # point count (int)
            error = progressDict["error"]
            # boolean for whether an error occurred
            streak = progressDict["streak"]
            # the current channel's streak

            pointString = f"{points:,.0f} points"
            # formats the number to use formatting (no decimals, thousand comma)

            if error:
            # if there's an error reported
                self.channelLabel.setText(f"Error with {channel}, couldn't get points")
                # sets an error text
            else:
            # no error ->
                self.channelLabel.setText(f"{pointString} and a streak of {streak} found for {channel}")
                # sets the text to match



### Progress Done ###

    def progressDone(self, errors: int, streak: int, expiryList: list=None, points: int=None):
        """A function to change the headless UI into completion mode"""

        preFinalText = self.totalLabel.text()
        # gets the text from the label
        self.progressBar.hide()
        # hides the progress bar

        if enablePoints:
        # if points are enabled
            if enableStreaks:
            # if streaks are enabled
                self.totalLabel.setText(f"{preFinalText} - highest streak: {streak}")
                # makes the total label state the max streak as well
            else:
            # if streaks aren't enabled
                self.totalLabel.setText(f"{preFinalText}")
                # sets the text to match
        elif enableStreaks:
        # if only streaks are enabled
            self.totalLabel.setText(f"Highest streak: {streak}")
        else:
        # if neither is, must be a single channel
            self.totalLabel.setText(f"")
            # sets no label

        if not expiryList or len(expiryList) == 0:
        # if the expiry list isn't passed or is empty
            expiryString = f""
            # sets the string to naught
        else:
        # list is passed and not empty
            expiryStringList = []
            # empty list of strings
            for entry in expiryList:
            # for every dictionary entry (channel = {"expires": stamp})
                entryString = f"{entry}: {entry["expires"]}"
                # forms a string like: "caseoh_: may 17th"
                expiryStringList.append(entryString)
                # adds the string into the list
            expiryString = f"Channels with expiring streaks: {", ".join(expiryStringList)}"
            # turns the list into a string

        if not overrideChannel:
        # if override channel wasn't set
            if errors > 0:
            # if there was at least one error
                finalString = (
                            f"All channels scoured - stats have been saved to CSV!\n\n"
                            f"TEPM was unable to store points for {errors} out of {len(self.channels)} channels\n\n"
                            f"{expiryString}\n\n"
                            f"Feel free to exit, thank you for using TEPM <3\n"
                            )
                # forms final string with error count
            else:
            # if there were no errors
                finalString = (
                            f"All channels scoured - stats have been saved to CSV!\n\n"
                            f"{expiryString}\n\n"
                            f"Feel free to exit, thank you for using TEPM <3\n"
                            )
                # forms final string with no errors
        else:
        # if override channel was set
            if errors == 0:
            # no errors
                finalString = f"{overrideChannel}:\n{points:,.0f} points and a streak of {streak}!"
                # forms final string
            else:
            # error
                finalString = f"Couldn't get points and/or streak for {overrideChannel}!"
                # forms final string with error

        self.channelLabel.setText(finalString)
        # final UI update with the formed string
        self.eop()
        # enables menu buttons (end of program)



### End of Program ###

    def eop(self):
        """Function to enable the exit and menu buttons"""
        self.menuButton.show()
        self.exitButton.show()
        # just enables the buttons



### Return to Menu ###

    def backToTheLobby(self, action:str):
        """Function to send you back to the menu"""

        if action == "Menu":
        # if called for return to menu
            ctrl.windowSwap("Starter")
            # shows the starter window
            ctrl.stopPredictionWorker.emit()
            # calls the stopper to stop polling new prediction data
            self.savePredictions()
            # saves when going to menu
        elif action == "Save":
        # if called to save the prediction details
            self.savePredictions()
            # calls the savePredictions to save current stats
        else:
        # exit button
            self.savePredictions()
            # calls the savePredictions to save current stats
            ctrl.browserProfile.deleteLater()
            self.browserPage.deleteLater()
            self.browserView.deleteLater()
            # deletes the browser-related variables
            app.exit()
            # closes the app



### Save Prediction History ###

    def savePredictions(self):
        """Function to save the prediction history"""

        if os.path.exists(predictHistoryPath):
        # if the prediction history file already exists
            with open(predictHistoryPath, "r", encoding="utf-8") as prdH:
                # opens the history file in read mode
                    predictionHistory = json.load(prdH)
                    # loads the map
        else:
        # file doesn't exist
            predictionHistory = {}
            # empty map
        
        self.pastPredictions = predictionHistory | self.pastPredictions
        # merges the prediction history dictionaries into one "new" one (uses the newer self.pastPrediction values if clashing)

        with open(predictHistoryPath, "w", encoding="utf-8") as nprdH:
        # opens the file in write mode
            json.dump(self.pastPredictions, nprdH, indent=3, default=str, ensure_ascii=False)
            # dumps the prediction history into file

        self.predictionUserInform("Saved prediction history!")
        # user inform
        


### UI Style Picker ###

    def uiStyle(self, action:str):
        """Function to change the UI when called for"""

        self.refreshTokenButton.hide()
        # hides the token button by default

        if action == "Predict":
        # prediction screen

            self.setMinimumSize(850, 950)
            self.resize(850, 950)
            # the window size

            self.swapMainUI(action)
            # swaps the elements

        elif action == "Browser":
        # if it's browser-only view

            self.setMinimumSize(1150, 850)
            self.resize(1150, 850)
            # resizes the window to "normal" browser size

            self.swapMainUI(action)
            # calls the UI changer
        
        else:
        # points/streaks view

            self.setMinimumSize(500, 600)
            self.resize(500, 600)
            # the window size

            self.swapMainUI(action)
            # swaps the elements

            QTimer.singleShot(2000, self.startPointWorker)
            # calls the point manager to start getting points



### Swap UI ###

    def swapMainUI(self, action:str):
        """Function that swaps the UI layout between predict and point/streak grab"""

        self.menuButton.setParent(None)
        self.exitButton.setParent(None)
        # removes the parent layout, so it can be re-given here

        if action == "Predict":
        # prediction UI activate

            self.stopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
            self.stopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds them to the stop layout (prediction UI)

            self.savePredictions()
            # calls the prediction save to get the current map of past predictions

            self.predictUI("Init")
            # calls the prediction UI to start

        elif action == "Browser":
        # browser view UI activate

            self.browserLayout.addWidget(self.menuButton, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
            self.browserLayout.addWidget(self.exitButton, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds them to the browser layout

            self.browserWindow()
            # calls the browser window (forces full window size and shows it)

        else:
        # point / streak grab UI activate

            self.pointGrabStopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
            self.pointGrabStopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds them to the point grab layout

            self.headlessUI(action)
            # calls the headless UI to start



### Prediction UI ###

    def predictUI(self, action:str = None, channel:str = None):
        """Function that handles prediction UI changes"""

        if action == "Init":
        # init action
            self.mainStack.setCurrentWidget(self.predictionPage)
            # sets the prediction page as visible
            self.predictionPage.show()
            # enables the prediction page
            ctrl.predictionWorkerStart()
            # starts the predict/balance refresh thread loop
            self.eop()
            # calls "end of program" to show menu and exit buttons
            ctrl.predictionTimerOverride.emit()
            # sends a signal to skip the initial 15 second wait to get first data right away
            self.currentChannel = predictChannel
            # grabs the current channel from the global variable 
            
        elif action == "Swap":
        # if user pressed swap button
            newChannel = self.predictChannelLine.text().strip()
            # temp var for channel
            if not newChannel or newChannel == "":
            # if the channel is empty
                self.predictionUserInform("No streamer set, please enter one to change streams")
                # user inform
            else:
                ctrl.newChannelQueue.put_nowait(newChannel)
                # adds the new channel to the channel queue
                ctrl.newChannelSignal.emit()
                # sends a signal to indicate a new channel
                self.predictChannelLine.setText("")
                # clears the text entry field

        elif action == "Case":
        # case sensitive name swap
            newChannel = channel
            # grabs the passed argument name
            ctrl.newChannelQueue.put_nowait(newChannel)
            # adds the new channel to the channel queue (doesn't request new data because the channel is the same)
            ctrl.newChannelSignal.emit()
            # sends a signal to indicate a new channel
            self.predictChannelLine.setText("")
            # clears the text entry field



### Prediction Result -> Update Label ###

    def predictStatusUpdate(self, color: str):
        """Function to update the status label style"""

        self.predictStatusLabel.setStyleSheet("""
                    QLabel {{
                        font-weight: bold;
                        font-size: 16px;
                        color: {customColor};
                    }}
                """.format(customColor=color))
        # updates the color of the prediction status label with the passed color



### Prediction Data -> Update All Labels ###

    def predictLabelUpdater(self, statusText: str, infoText: str, detailText: str, color: str):
        """Function to update all prediction-related labels\n
        statusText = prediction status\n
        infoText = prediction name\n
        detailText = creator, timestamp"""

        self.predictStatusLabel.setText(statusText)
        # sets the status label
        self.predictInfoLabel.setText(infoText)
        # sets the info label
        self.predictDetailLabel.setText(detailText)
        # sets the details label
        self.predictStatusUpdate(color)
        # sets the text color



### Prediction Data -> Update Bet Label ###

    def betLabelUpdater(self, text:str, color:str=None):
        """Function to change the current bet label"""

        self.currentBetLabel.setText(text)
        # sets the text from parameter

        if color == "Green":
            self.currentBetLabel.setStyleSheet("""
                QLabel {
                    color: #0DD141;
                    font-style: italic;
                    font-size: 14px;
                }
            """)
            # default style (green text)
        elif color == "Red":
        # bet loss
            self.currentBetLabel.setStyleSheet("""
                QLabel {
                    color: #820C04;
                    font-style: italic;
                    font-size: 14px;
                }
            """)
            # loss style (red text)
        # elif color == "White":

        self.currentBetLabel.show()
        # ensures the label is visible



### Screen Resize ###

    def screenResize(self, buttonCount: int):
        """Resizes screen based on active # of buttons"""
        
        self.buttonWidth = 140
        # how wide one button should count as (px)
        newSize = max(850, int(buttonCount * self.buttonWidth))
        # calculates a new size for the screen width (to fit buttons), picks the larger width from 850 and (x*y)

        self.setMinimumSize(newSize, 950)
        self.resize(newSize, 950)
        # the window size



### Prediction -> UI Update ###

    def predictUpdateUI(self, prediction: dict):
        """Function to update UI based on prediction/balance data"""

        totalPoints = 0
        # starts total point counter at 0
        shouldUpdate = True
        # boolean for "should the full package be updated"
        missedResolve = False
        # boolean for "did a new prediction start before the previous one was registered"

        if prediction["success"]:
        # if it was a success

            ctrl.detailsDataSignal.emit(prediction)
            # sends the whole dictionary to the controller -> details window

            pointsName = prediction["pointsName"]
            # grabs the points' name

            if pointsName:
            # if the points are named and isn't null
                pointsString = pointsName
                # assigns the points string to use the given name
            else:
            # if they aren't named by the streamer
                pointsString = "points"
                # assigns base name

            oldID = self.predictionID.get("lastID", None)
            oldType = self.predictionID.get("lastType", None)
            # grabs the old ID and type to compare

            eventID = prediction["id"]
            # grabs the event ID from the prediction dictionary
            eventType = prediction["type"]
            # grabs the event type (active, locked, resolved)

            oldEvent = self.predictionID.get(eventID, {"state": False})
            # gets the previous prediction's data
            oldEventType = oldEvent["state"]
            # gets the previous event's type (active, locked, resolved)

            self.predictChannelPoints = prediction.get("balance", 0)
            # sets the balance to match (default 0 if not found)
            self.predictPointLabel.setText(f"Balance: {self.predictChannelPoints:,.0f} {pointsString}")
            # update the balance label

            caseName = prediction.get("caseName", False)
            # grabs the case sensitive name, if it's available

            if caseName and (caseName != self.currentChannel):
            # if the case sensitive name is set and it's not the same as the currently displayed channel
                self.currentChannel = caseName
                # updates the internal name scheme
                newChannel = True
                # boolean that stores whether it's a new channel or same as the previous
            else:
            # case name == current channel (no swap)
                newChannel = False
                # boolean that stores whether it's a new channel or same as the previous

            if oldEventType and (oldEventType != eventType):
            # if there is a previously stored event type and the new one doesn't match it
                if oldEventType == "locked" and eventType == "active":
                # if the previously stored state was locked, and the new one is active (means the resolved was missed)
                    missedResolve = True
                    # sets the boolean to True

            if (oldID == eventID) and (oldType == eventType):
            # if the IDs match and the types match (same dictionary)
                shouldUpdate = False
                # changes the boolean to prevent full update
            else:
            # not the same data
                self.predictionID["lastID"] = eventID
                # swaps the event ID for the prediction ID

                if (self.predictionID.get("lastType", None) == "active") and (eventType == "resolved"):
                # if the event went from active to resolved (only realistically possible if swapping streams or refund)
                    if newChannel:
                    # if it's a new channel (then refund-checking doesn't matter)
                        pass
                        # stops checking
                    else:
                    # not a new channel, event went from active -> resolved
                        lastNumbers = self.predictionNumbers.get(eventID, {"balance": None})
                        # stores the event ID's bet-related numbers (if they exist)
                        if lastNumbers.get("balance", None) is not None:
                        # if the balance exists from last store
                            pointChange = self.predictChannelPoints - lastNumbers["balance"]
                            # calculates how much the points changed by 
                            bet = lastNumbers.get("bet", 0)
                            # gets the previously stored bet
                            if bet > 0:
                            # if bet isn't 0
                                payoutMulti = (pointChange / bet)
                                # calculates a payout multiplier
                                if 0.9 <= payoutMulti <= 1.1:
                                # if the payout multiplier falls in between 0.9 and 1.1 (means it more than likely was NOT a payout, but a return of bet)
                                    eventType = "refunded"
                                    # changes the eventType to refunded

                self.predictionID["lastType"] = eventType
                # copies the new values over so they can be compared next time

            timeNow = datetime.datetime.now().astimezone().strftime("%#H:%M:%S")
            # grabs current time and formats it
            self.predictLastUpdateLabel.setText(f"Last update: {timeNow}")
            # sets the task indicator to indicate the task that has been tasked

            if shouldUpdate:
            # if there's new data (hides these to reset button count)
                for widget in self.predictOutcomeWidgets:
                # goes through the outcome widgets (the betting buttons + labels)
                    widget.hide()
                    # hides the widget

                self.predictChannelLabel.setText(self.currentChannel)
                # updates the channel label
                
                if eventType == "active":
                # if the active predict list has more than 0 elements

                    localTime = prediction["localTS"]
                    # grabs the local timestamp (still in datetime format)
                    timer = int((prediction["timer"]) - 2)
                    # grabs the prediction timer (-2 due to delay)
                    self.timerEnd = localTime + datetime.timedelta(seconds=timer)
                    # calculates the end of the timer, stores in self
                    self.labelTimer = QTimer()
                    # sets up a QTimer

                    self.labelTimer.timeout.connect(self.predictionTimer)
                    # connects the timer "timeout" (interval ending)
                    self.predictionTimer()
                    # runs the first update
                    self.labelTimer.start(1000)
                    # starts it with an interval of 1000ms (1s)

                else:
                # if it's not active
                    try:
                    # checks if the timer is enabled
                        if self.labelTimer:
                        # if the label timer is set
                            self.labelTimer = None
                            # clears the timer
                            self.predictTimerLabel.setText(" ")
                            # clears the timer field
                    except:
                    # if it's not yet defined
                        pass
                        # doesn't do anything
                    self.predictTimerLabel.setText(" ")
                    # empties the text field (preserves the spacing, no actual timer)

            title = prediction["title"]
            # grabs the prediction title
            outcomes = prediction["outcomes"]
            # grabs the list of outcomes
            creator = prediction["creator"]
            # grabs the creator name
            timestamp = prediction["timestamp"]
            # grabs the timestamp

            ownVoteID = prediction["votedOutcome"]
            # gets the outcome user (may have) voted for
            ownVoteSum = int(prediction["votedSum"])
            # gets the amount user (may have) voted with
            ownVoteWin = prediction.get("sumWon", 0)
            # gets the total won points (null until resolved)
            storedVoteDict = self.predictionNumbers.get(eventID, {"bet": 999999})
            # grabs the stored dictionary from prediction numbers (falls back to dict with bet = 999999 if it doesn't exist)

            if not (ownVoteSum == storedVoteDict["bet"]):
            # if the vote sum doesn't match the previously stored vote
                shouldUpdate = True
                # sets the boolean to True so the UI gets fully updates
                self.predictionNumbers[eventID] = {"bet": ownVoteSum, "option": ownVoteID, "balance": self.predictChannelPoints}
                # stores the bet, voted outcome and current balance in the dictionary with the eventID as key

            if not ownVoteID:
            # no vote ID = no bet (it already gets checked in grab to be for *this* event)
                self.betLabelUpdater(" ", None)
                # updates the bet label to empty

            for x in range(len(outcomes)):
            # goes through each outcome again (needs to do it 2x because first need the total points for labeling)
                optionPoints = outcomes[x]["totalPoints"]
                # gets the points given to the option
                totalPoints += int(optionPoints)
                # adds the points to the total
            
            self.predictionKeys[eventID] = {}
            # creates a keymap for this event (or clears)

            if self.predictionID.get(eventID, False):
            # if the event has an entry already
                self.predictionID[eventID]["state"] = eventType
                # updates the current event's state to match
            else:
            # no entry for the event yet
                self.predictionID[eventID] = {"state": eventType}
                # creates a new entry instead

            buttonCount = 0
            # starts a counter for buttons

            outcomesList = []
            # empty list of outcome titles

            for x in range (len(outcomes)):
            # goes through each option
                optionName = outcomes[x]["title"]
                # gets the name of the option
                outcomesList.append(optionName)
                # adds to list

                optionID = outcomes[x]["id"]
                # gets the outcome ID
                if ownVoteID == optionID:
                # if the user vote matches this vote
                    self.predictionID[eventID]["title"] = optionName
                    self.predictionID[eventID]["id"] = optionID
                    # stores the name and ID of the outcome voted for, in this event

                optionPoints = outcomes[x]["totalPoints"]
                # gets the points given to the option
                optionUsers = outcomes[x]["totalUsers"]
                # gets the users that went in on the option

                if totalPoints > 0:
                # if there's more than 0 points in the total pool
                    pointShare = ((optionPoints / totalPoints) * 100)
                    # gets the share of points out of the total (decimal, converts to %)
                else:
                # if not
                    pointShare = 0
                    # the share is 0 of 0

                buttonX = self.predictButtonList[x]
                # grabs the xth bet button
                buttonX.setText(optionName)
                # sets the option name to match

                pointsX = self.predictPoints[x]
                # grabs the xth pool label
                optionString = f"{optionPoints:,.0f} {pointsString}\n({pointShare:.1f}%)\n{optionUsers:,.0f} users"
                # forms a string 
                pointsX.setText(optionString)
                # sets the label to match

                payoutX = self.predictMultipliers[x]
                # grabs the xth payout label
                if optionPoints > 0:
                # if the option has more than 0 points
                    payout = (totalPoints / optionPoints)
                    # calculates the payout multiplier
                else:
                # if it doesn't (then technically the payout is 1:1 (0 -> 0)
                    payout = 1
                    # sets to 1
                payoutX.setText(f"{payout:.2f}x")
                # sets the multiplier with 2 decimal precision

                self.predictionNumbers[eventID][optionID] = {"payout": payout}
                # stores the payout multiplier

                self.predictOutcomeWidgets[x].show()
                # enables the xth widget (label + button + label)

                self.predictionKeys[eventID][optionID] = buttonX
                self.predictionKeys[eventID][buttonX] = optionID
                # stores the outcome and button as keys:values for each other

                buttonCount += 1
                # adds 1

            if buttonCount != self.currentSize:
            # checks if there's a different amount of buttons than last time
                self.currentSize = buttonCount
                # sets the current size
                self.screenResize(buttonCount)
                # calls the resizer with the count, to ensure all buttons fit and there's not empty space

            if ownVoteID:
            # if user voted in this event
                voteShare = ((ownVoteSum / totalPoints) * 100)
                # calculates user's share of the total pool in percentages
                if voteShare < 1:
                # if the vote accounts for less than 1 percent
                    self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} {pointsString}\nYour bet: {voteShare:.3f}%")
                    # sets the text with 3 decimal points (eg. 0.333%)
                elif voteShare <= 5:
                # if the vote accounts for less than or eq to 5 percent
                    self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} {pointsString}\nYour bet: {voteShare:.2f}%")
                    # sets the text with 2 decimal points (eg. 0.33%)
                else:
                # if the vote accounts for more than 5 percent
                    self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} {pointsString}\nYour bet: {voteShare:.1f}%")
                    # sets the text with 1 decimal point (eg. 0.3%)
            else:
            # user did not vote in this event
                self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} {pointsString}\n")
                # sets the total pool label
            
            if shouldUpdate:
            # if the boolean is set to True (means the event status or bet has changed)

                if eventType == "active":
                # if the prediction is active
                    self.maxBetButton.setEnabled(True)
                    self.defaultBetButton.setEnabled(True)
                    self.predictBetButton.setEnabled(True)
                    self.predictAmountLine.setEnabled(True)
                    # enables the bet-related options
                    self.predictLabelUpdater("Open Prediction:", f"{title}", f"Started by {creator}, started {timestamp}", "green")
                    # calls the updater to change UI
                    self.predictResultLabel.setText(" ")
                    # clears the result field

                    if ownVoteID:
                    # if user voted
                        betString = f"Current bet: {ownVoteSum:,.0f} on {self.predictionID[eventID]["title"]}"
                        # forms a string to indicate bet
                        self.betLabelUpdater(betString, "Green")
                        # updates bet label
                        buttonToSelect = self.predictionKeys[eventID][ownVoteID]
                        # gets the stored option ID's (voted outcome ID) linked button identifier
                        self.predictButtonManager("Vote", buttonToSelect)
                        # calls to lock the option selection buttons
                    else:
                    # user didn't vote yet
                        self.predictButtonManager("Init", None, True)
                        # calls for the buttons to get unlocked/reset

                    ctrl.timerSwap.emit(3)
                    # if the event is active, speeds up update timer to get more data quicker

                if eventType != "active" or missedResolve:
                # prediction isn't active (locked/resolved), or there was a resolved prediction that was missed (this is only true if it's active, so it can't double-submit)
                    self.maxBetButton.setEnabled(False)
                    self.defaultBetButton.setEnabled(False)
                    self.predictBetButton.setEnabled(False)
                    self.predictAmountLine.setEnabled(False)
                    # disables the bet-related options
                    self.predictAmountLine.setText("")
                    # clears the prediction amount

                    ctrl.timerSwap.emit(7)
                    # if the event is locked, slows the updater down to ~normal speed

                    if eventType == "locked":
                    # if the prediction is locked
                        self.predictLabelUpdater("Closed Prediction:", f"{title}", f"Started by {creator}, closed {timestamp}", "orange")
                        # calls the updater to change UI
                        self.predictResultLabel.setText(" ")
                        # clears the result field

                        if ownVoteID:
                        # if user voted
                            betWin = ((ownVoteSum * self.predictionNumbers[eventID][ownVoteID]["payout"]) - ownVoteSum)
                            # gets the potential bet win by taking the user vote, multiplying with the payout for that option and subtracting own vote
                            betString = f"You bet {ownVoteSum:,.0f} on {self.predictionID[eventID]["title"]}\n(+{betWin:,.0f} on win)"
                            # forms a string to indicate bet
                            self.betLabelUpdater(betString, "Green")
                            # sets text to match
                            self.predictButtonManager("Vote", self.predictionKeys[eventID][ownVoteID])
                            # calls to lock the option buttons, sets the button to show selected
                        else:
                        # user didn't vote
                            self.predictButtonManager("Lock", None, True)
                            # calls to lock everything, no selection

                    elif missedResolve:
                    # if there was a missed resolved prediction
                        prediction = prediction["oldPred"]
                        # swaps the dictionary to use the old prediction's dictionary instead
                        if prediction:
                        # if the dictionary is valid (if none is found, it's set to False)
                            if not self.pastPredictions.get(eventID, None):
                            # if there's no stored details for this event/prediction already
                                chartStamp = prediction["chartStamp"]
                                # grabs the datetime formatted timestamp to pass
                                if ownVoteID:
                                # if user voted
                                    self.pastPredictions[eventID] = {"channel": self.currentChannel, "title": title, "timestamp": chartStamp, "outcomes": outcomesList, "winner": winOutcomeTitle, "balance": self.predictChannelPoints, "bet": ownVoteSum, "W/L": winState, "gain": newPoints}
                                    # stores the event details with vote details
                                else:
                                # user didn't vote
                                    self.pastPredictions[eventID] = {"channel": self.currentChannel, "title": title, "timestamp": chartStamp, "outcomes": outcomesList, "winner": winOutcomeTitle, "balance": self.predictChannelPoints}
                                    # stores the event details with no vote details

                    else:
                    # prediction is resolved (paid out)
                        winOutcomeDict = prediction["winner"]
                        # gets the winning outcome dictionary, otherwise uses set dictionary
                        winOutcomeID = winOutcomeDict["id"]
                        # grabs the winning ID
                        winOutcomeTitle = winOutcomeDict["title"]
                        # grabs the winning title

                        if winOutcomeID == "refunded":
                        # if outcome is a refund
                            self.predictLabelUpdater(f"Prediction was refunded!", f"{title}", f"Started by {creator}, ended {timestamp}", "red")
                            # calls the updater to change UI
                            self.betLabelUpdater("Bet refunded", "Green")
                            # ensures the bet is cleared
                            self.predictButtonManager("Init", None, True)
                            # clears the status', unlocks buttons
                        else:
                        # if the outcome is anything else
                            self.predictLabelUpdater("Paid Out Prediction:", f"{title}", f"Started by {creator}, ended {timestamp}", "orange")
                            # calls the updater to change UI
                            self.predictButtonManager("Winner", self.predictionKeys[eventID][winOutcomeID])
                            # calls the predict button manager to highlight winner in green

                            if ownVoteID:
                            # if user voted
                                if ownVoteID == winOutcomeID:
                                # if the stored outcome is the same as the winner
                                    self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                    # text if user bet and won
                                    newPoints = (ownVoteWin - ownVoteSum)
                                    # gets the amount of points won (gained)
                                    newPointsPercent = ((newPoints / ownVoteSum) * 100)
                                    # gets the percentage of bet that the new points amount to
                                    winString = f"You won {ownVoteWin:,.0f} {pointsString} with a bet of {ownVoteSum:,.0f} {pointsString}! (+{(newPoints):,.0f} / {newPointsPercent:.1f}%)"
                                    # forms win string
                                    self.betLabelUpdater(winString, "Green")
                                    # bet label update
                                    winState = "Win"
                                    # stores a winstate
                                else:
                                # if the stored is not the same
                                    self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                    # text if user bet and lost
                                    self.betLabelUpdater(f"You lost {ownVoteSum:,.0f} {pointsString}", "Red")
                                    # bet label update
                                    winState = "Loss"
                                    # stores a winstate
                                    newPoints = (0 - ownVoteSum)
                                    # stores the loss 
                            else:
                            # no status, no bet
                                self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                # text if user did not bet
                                self.betLabelUpdater(" ")
                                # bet label update

                        if not self.pastPredictions.get(eventID, None):
                        # if there's no stored details for this event/prediction already
                            chartStamp = prediction["chartStamp"]
                            # grabs the datetime formatted timestamp to pass
                            if ownVoteID:
                            # if user voted
                                self.pastPredictions[eventID] = {"channel": self.currentChannel, "title": title, "timestamp": chartStamp, "outcomes": outcomesList, "winner": winOutcomeTitle, "balance": self.predictChannelPoints, "bet": ownVoteSum, "W/L": winState, "gain": newPoints}
                                # stores the event details with vote details
                            else:
                            # user didn't vote
                                self.pastPredictions[eventID] = {"channel": self.currentChannel, "title": title, "timestamp": chartStamp, "outcomes": outcomesList, "winner": winOutcomeTitle, "balance": self.predictChannelPoints}
                                # stores the event details with no vote details

        else:
        # if it wasn't a success (usually a stream with no prior history)
            errorMsg = prediction["error"]
            # stores the error message
            if "10054" in errorMsg:
            # if the windows network error 10054 is present in the error string
                errorMsg = "Windows network error! Please wait..."
                # overrides the error message 

            self.predictionUserInform(f"Failed to get prediction details for {predictChannel}!\n({errorMsg})")
            # changes the text to inform (includes error message)

            self.maxBetButton.setEnabled(False)
            self.defaultBetButton.setEnabled(False)
            self.predictBetButton.setEnabled(False)
            self.predictAmountLine.setEnabled(False)
            # disables the betting buttons

            self.predictChannelLabel.setText(predictChannel)
            # sets the label to match given channel
            self.predictLabelUpdater("No prediction", " ", " ", "Red")
            # sets empty labels
            self.betLabelUpdater(" ")
            # sets empty bet
            self.predictPoolLabel.setText(" ")
            # empties the pool label

            for widget in self.predictOutcomeWidgets:
            # goes through every outcome widget
                widget.hide()
                # hides it
            self.predictOutcome1.show()
            # shows only the first one

            self.predictPayout1.setText("0.00x")
            # sets placeholder payout label
            self.predictOption1.setText("Nonexistent Option")
            # sets empty bet button name
            self.predictPoints1.setText(f"0 Points\n(100%)\n0 users")
            # sets placeholder pool label for the first widget



### Predict Intermediary ###

    def predictIntermediary(self):
        """Sits between the bet button and makePrediction"""

        if not self.betMasker("Check"):
        # runs betmasker before, checks if it returns False
            return
            # stops (betMasker already sets a reason)

        selectedButton = None
        # starts as None
        selectedButton = self.buttonGroup.checkedButton()
        # sets the selected button as the option

        if selectedButton == None:
        # if none are selected
            event = self.predictionID.get("lastID", None)
            # gets the "last" (current) ID
            if event:
            # if the event is defined already (shouldn't ever fail, but safety)
                try:
                # tries to get the outcome of the user vote
                    votedOption = self.predictionID[event]["id"]
                    # gets the voted outcome ID
                    selectedButton = self.predictionKeys[event][votedOption]
                    # gets the selected button via linked prediction key
                except:
                # if it can't find that info
                    selectedButton = None
                    # sets to none

        try:
        # tries to get the text
            bet = int(self.predictAmountLine.text().strip())
            # grabs the bet integer from the current bet line
        except:
        # if it fails (empty)
            bet = False
            # sets to false (flags)

        eventID = self.predictionID["lastID"]
        # grabs the event ID from the ID map
        eventType = self.predictionID["lastType"]
        # grabs the current event type (active, locked, resolved)

        if eventType == "Locked":
        # if the event is locked
            self.predictionUserInform(f"Cannot bet on a closed prediction!")
            # user inform
            return
            # stops
        elif eventType == "Resolved":
        # if the event is resolved (paid out)
            self.predictionUserInform(f"Cannot bet on a paid out prediction!")
            # user inform
            return
            # stops

        if not selectedButton or not bet:
        # if either option is not set
            self.predictionUserInform("No bet set or outcome selected, please try again!")
            # sets error text
        else:
        # if both are set successfully
            optionName = selectedButton.text()
            # grabs the text of the button
            try:
                outcomeID = self.predictionKeys[eventID][selectedButton]
                # grabs the outcome ID linked to that option from the key map
            except:
                outcomeID = None
                # sets to none

            currentBet = self.predictionNumbers.get(eventID, {"option": None})["option"]
            # grabs the current voted outcome ID
            balance = self.predictChannelPoints
            # grabs the current balance for the channel to send

            if outcomeID:
            # if outcomeID is defined (didn't fail, was set correctly)
                if currentBet == outcomeID or not currentBet:
                # if there's already a bet with this outcome or no bet set yet
                    ctrl.makeBet.emit(bet, eventID, outcomeID, optionName, balance)
                    # calls the pyQt signal with the details (bet int, outcomeID)
                else:
                # the bet is not the same as the selected button (more than likely visually screwed)
                    ctrl.makeBet.emit(bet, eventID, currentBet, optionName, balance)
                    # sends the bet with the current bet ID instead (overrides the selected button, in case there's non)
            else:
            # if it wasn't defined (either didn't get set properly or failed to grab)
                self.predictionUserInform(f"Failed to send bet due to internal error!")
                # user inform



### Prediction Buttons ###

    def predictButtonManager(self, action: str = None, passedButton = None, refresh: bool = False):
        """Function to ensure the buttons only have one active at one time\n
            Action = Winner, Init, Lock (how to style buttons)\n
            Button = QPushButton (which button to select)\n
            Refresh = Bool (force all buttons to reset)"""

        if passedButton and not refresh:
        # if the button argument is defined and a refresh isn't forced
            selectedButton = passedButton
            # sets the selected button from button
        else:
        # if no button is passed or there's a force refresh (to reset)
            selectedButton = None
            # sets None

        for button in self.predictButtonList:
        # goes through every button

            if action == "Winner":
            # choosing winning outcome
                if button == selectedButton:
                # if the button is the selected one
                        button.setProperty("state", "Winner")
                        # sets the property to winner
                        button.style().unpolish(button)
                        button.style().polish(button)
                        button.update()
                        # refreshes the button style
                else:
                    button.setProperty("state", "Loser")
                    # sets the property to loser
                    button.style().unpolish(button)
                    button.style().polish(button)
                    button.update()
                    # refreshes the button style
                button.setEnabled(False)
                # buttons disabled because no bet active yet

            else:
            # startup / lock / vote
                if button == selectedButton:
                # if the button is the selected one
                        button.setProperty("state", "Selected")
                        # sets the property to selected
                        button.style().unpolish(button)
                        button.style().polish(button)
                        button.update()
                        # refreshes the button style
                else:
                # not selected
                        button.setProperty("state", None)
                        # empties property
                        button.style().unpolish(button)
                        button.style().polish(button)
                        button.update()
                        # refreshes / clears the style

                if action == "Init":
                # startup / reset
                    button.setEnabled(True)
                    # buttons should be on by default
                else:
                # lock / vote
                    button.setEnabled(False)
                    # buttons turned off when locked (can't change bet once confirmed)



### modCheck ###

    def modCheck(self, action:str=None) -> bool:
        """Checks if user is moderator before allowing mod view open"""

        userData = statusGrabber(self.state, predictChannel)
        # calls status grabber with the state and current channel

        if userData["success"]:
        # operation successful
            if userData["mod"]:
            # if the mod boolean is true
                if action == "Window":
                # if the call is to open the mod window
                    ctrl.startModSignal.emit()
                    # sends a signal to the mod starter
                return True
                # a mod
            else:
            # user is not a mod
                self.predictionUserInform("No moderator status in this channel")
                # no mod inform
                return False
                # not a mod
        else:
        # operation not successful
            self.predictionUserInform("Could not get moderator status, can't open view")
            # user inform
            return False
            # something went wrong, can't auth



### Bet Masking ###

    def betMasker(self, action: str = None):
        """Function to ensure the bet remains valid"""

        if action == "Clear":
        # clear via keybind
            self.predictAmountLine.setText(f"")
            # clears the bet
            return
            # stops

        try:
        # tries to get the current bet written
            currentBet = int(self.predictAmountLine.text().strip())
            # grabs the bet from the predict amount line
        except:
        # if it fails (is empty)
            currentBet = 0
            # sets to 0

        if action == "Halve" or action == "Double":
        # halve/double request via keybind
            if currentBet != 0:
            # if the bet isn't 0
                if action == "Halve":
                # halve request
                    currentBet = int(currentBet / 2)
                    # splits the bet in half
                else:
                # double request
                    currentBet = int(currentBet * 2)
                    # doubles the bet
                self.predictAmountLine.setText(f"{currentBet}")
                # sets the current bet
                return
                # stop
            else:
            # bet is 0
                if action == "Halve":
                # halve request
                    self.predictionUserInform("Cannot halve 0 points!")
                    # user inform
                else:
                # double request
                    self.predictionUserInform("Cannot double 0 points!")
                    # user inform
                return
                # stop
        

        if currentBet == 0 and (action not in ["Max", "Default"]):
        # if the bet is 0, and it's not a Max/Default (those set the points after)
            self.predictionUserInform("Cannot bet 0 points")
            # user inform
            return False
            # stops

        currentBal = self.predictChannelPoints
        # grabs the balance from the variable

        if action == "Max":
        # if it calls to enter max points
            if currentBal < 250000:
            # if user has < 250k
                self.predictAmountLine.setText(f"{currentBal}")
                # all in
            else:
            # user has >= 250k
                self.predictAmountLine.setText("250000")
                # sets Twitch max bet

        elif action == "Default":
        # if it calls to enter the default
            if roundBalanceBet:
            # if balance rounding is enabled
                leftover, bet = divmod(currentBal, defaultBet)
                # performs divmod on the current balance to form the bet 
                # (eg. balance of 34,982, default bet of 10,000 -> balance of 30,000 and a bet of 4,982)
                if bet == 0:
                # if the bet is 0 (meaning the divmod lead to a perfect division)
                    bet = defaultBet
                    # sets the default bet size instead
                self.predictAmountLine.setText(f"{bet}")
                # sets the calculated bet into the bet amount line
            else:
            # balance rounding isn't enabled
                self.predictAmountLine.setText(f"{defaultBet}")
                # sets the configured default bet instead

        else:
        # if it doesn't call for max
            if currentBet > currentBal:
            # if the bet is larger than the current balance
                self.predictionUserInform("Bet cannot exceed balance!")
                # user inform
                self.predictAmountLine.setText(f"{currentBal}")
                # enforces the max bet

                if action == "Check":
                # if this is a check request
                    return False
                    # returns False (wasn't valid)

            if action == "Check":
            # if this is a check request, and it has made it this far
                return True
                # returns True (is valid)



### Style Loader ###

    def cssStyleLoader(self, action=str):
        """Function that loads the CSS stylesheet"""

        with open(cssPath, "r") as seess:
        # opens the CSS stylesheet
            self.setStyleSheet(seess.read())
            # sets the stylesheet for the class

        if action != "Browser":
        # ensures it's not browser only
            self.extractAuthToken(action)
            # calls the next stage
        else:
        # action is browser
            self.browserWindow()
            # calls the browser window shower



### Auth Token Grabber ###

    def extractAuthToken(self, action):
        """Function to get the auth token from storage"""

        self.authTokenTimer = QTimer()
        """A timer to forcefully skip auth token extracting if not done"""
        self.authTokenTimer.setSingleShot(True)
        # only activates once
        self.authTokenTimer.timeout.connect(self.authNotValid)
        # connects the timeout to authNotValid
        self.authTokenTimer.start(5000)
        # runs in 5 seconds

        storedCookies = self.browserView.page().profile().cookieStore()
        # gets the stored cookies
        self.cookies = []
        # empty list for cookies

        self.taskText.emit("Parsing cookies for authorisation token...")
        # user update

        try:
        # ensures there's no cookie calls yet
            storedCookies.cookieAdded.disconnect()
            # removes any/all cookie calls
        except TypeError:
        # if that fails (there aren't any calls)
            pass
            # skip

        def cookieParser(cookie):
        # subfunction to parse the cookies
            name = cookie.name().data().decode("utf-8", "ignore")
            # gets the name of the cookie
            value = cookie.value().data().decode("utf-8", "ignore")
            # gets the value of the cookie

            self.cookies.append((name, value))
            # adds both to the list of cookies

            if name == "auth-token":
            # if the name of the cookie matches
                self.state.authToken = value
                # stores the value of that cookie in the variable
                storedCookies.cookieAdded.disconnect()
                # stops looking for cookies
                self.taskText.emit("Auth token found, validating...")
                # user update
                self.authTokenTimer.stop()
                # cancels the timer
                self.authValidCheck(action)
                # calls the validation 

        storedCookies.cookieAdded.connect(cookieParser)
        # when a cookie gets added, calls the cookieParser
        storedCookies.loadAllCookies()
        # starts loading the cookies in local storage



### Auth Token Validity Check ###

    def authValidCheck(self, action):
        """Function to ensure the auth token is valid"""
        try:
        # if the token is set, tries to check a channel
            testChannel = "Twitch"
            # uses Twitch's own channel as a test (should never be banned/have issues???)
            points = pointGrabber(self.state, testChannel)
            # gets the return from the pointGrabber
            result = points.get("success", False)
            # returns the success boolean (defaults to False if none returns)
            if result:
            # if the result is True (success)
                self.taskText.emit("Auth token successfully validated...\nStarting TEPM...")
                # user update
                self.authValid.emit(action)
                # sets the pyqt signal
            else:
            # if the result is False (failure)
                self.taskText.emit(f"Could not proceed due to {points.get("error", "Unknown Error!")}")
                # user inform
        except:
        # if the channel check fails
            self.authNotValid(action)
            # calls the invalid token function



### Auth Not Valid ###

    def authNotValid(self, action:str):
        """Function to handle auth token not being valid"""
        self.taskText.emit("Token could not be validated, ensure you're logged in to Twitch\nIf this persists, ensure the hashes in hashes.json are valid")
        # changes UI text to error
        self.mainStack.setCurrentWidget(self.browserStackPage)
        # sets the browser view active
        self.refreshTokenButton.show()
        # shows the refresh token button
        self.authInvalidAction = action
        # stores the action the user was trying to perform in self



### Prediction Timer ###

    def predictionTimer(self):
        """Function to change the timer label for open predictions"""
        timeNow = datetime.datetime.now().astimezone()
        # grabs current time
        timeLeft = int((self.timerEnd - timeNow).total_seconds())
        # stores how many seconds are left (datetime delta -> seconds -> int)

        if timeLeft <= 0:
        # if the time left is less than a second
            self.predictTimerLabel.setText("00:00")
            # sets end
            self.labelTimer.stop()
            # stops the timer
            self.labelTimer.deleteLater()
            # deletes current timer
            return
            # stops
        
        minutes, seconds = divmod(timeLeft, 60)
        # divides the seconds left into minutes and seconds
        self.predictTimerLabel.setText(f"{minutes:02}:{seconds:02}")
        # sets the timer label to match formatted timer (00:00)



### Prediction User Inform ###

    def predictionUserInform(self, text:str):
        """Function to display a user inform message for a short duration"""
        self.predictTaskLabel.setText(text)
        # sets the called text inform
        self.predictInformTimer = QTimer()
        # makes a QTimer
        self.predictInformTimer.timeout.connect(lambda: self.predictTaskLabel.setText(" "))
        # when the timer is up, resets the text
        self.predictInformTimer.setSingleShot(True)
        # only runs once
        self.predictInformTimer.start(5000)
        # sets the timer to last 5 seconds



### Task View Changer ###

    def taskLabelChanger(self, text):
        """Function to change the task view via external signals"""
        self.predictionUserInform(text)
        self.taskPageText.setText(text)
        # swaps both predict task and task page texts (either one could be up)



### Channel Lister ###

    def getChannelList(self) -> list:
        """The function to grab the list of channels"""
        self.channels = []
        # clears the list

        if predictChannel == None:
        # if there's no prediction channel

            if self.overrideChannel == None:
            # if there's no override channel set
                if activeOnly:
                # if the active streaks only check is enabled
                    self.channels = [
                                    entry for entry in streakMap 
                                    if entry not in excludedEntries
                                    ]
                    # adds streaks from streakMap (excludes set entries)
                else:
                # if active streaks only is not on
                    with open(self.channelTxtPath) as channelFile:
                    # opens the channel list.txt file 
                        for channel in channelFile:
                        # goes through each line (channel)
                            channel = channel.strip("\n")
                            # removes the newline marker
                            self.channels.append(channel)
                            # adds the channel to the list of channels

                self.taskText.emit(f"Found {len(self.channels)} channels...")
                # user update

            else:
            # if the boolean is true (single channel passed)
                self.channels.append(self.overrideChannel)
                # adds the override channel to the list of channels
                self.taskText.emit(f"Checking single channel: {self.overrideChannel}...")
                # user update
        
        else:
        # if the prediction channel is set
            self.channels.append(predictChannel)
            # adds the predict channel

        return self.channels
        # returns the list of channels to caller



### Point Worker Starter ###

    def startPointWorker(self):
    # a starter for the point worker

        self.pointThread = QThread()
        # creates a new thread
        self.pointThread.setObjectName("Point Grabber Thread")
        # object name (debug)
        self.pointWorker = PointWorker(self.state, self.channels)
        # creates a worker with the state, channel list

        self.pointWorker.moveToThread(self.pointThread)
        # moves the worker to its own thread

        self.pointThread.started.connect(self.pointWorker.run)
        # thread start connects to worker run

        self.pointWorker.pointWorkerProgress.connect(self.handleProgress)
        # connects the worker progress to handleProgress (when there's a progress update -> updates headless UI)
        self.pointWorker.pointWorkerDone.connect(self.progressDone)
        # connects to the progressDone function (when everything is done -> final UI update -> quit)
        self.pointWorker.pointWorkerDone.connect(self.pointThread.quit)
        self.pointWorker.pointWorkerDone.connect(self.pointWorker.deleteLater)
        # when the prediction wants to stop, quits the thread and the worker
        self.pointThread.finished.connect(self.pointThread.deleteLater)
        # when the thread is done (no worker), deletes the thread itself, too

        self.pointThread.start()
        # starts thread



### Channel ID Grab ###

def channelIDGrab(state, channel):
    """A function to grab the channelID"""

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    idPayload = {
        # forms a payload just for the ID
            "operationName": hashMap["ChannelID Operation"],
            # this was the first operation I found that has a return for the ID without requesting with the ID
            "variables": {
                "login": channel,
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": hashMap["ChannelID Hash"],
                    # the hash for the operation, may change
                    "version": int(hashMap["ChannelID Version"])
                    # the hash version
                }
            }
        }

    try:
    # tries to make a request
        idRequest = reqSession.post(rURL, json = idPayload, headers = headers)
        # makes request to get the 
        idData = idRequest.json()
        # stores the resulting data json
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # attempts to access the returned json
        if idData and idData["data"]:
        # if there's a return package and the package has "data"
            channelID = int(idData["data"]["channel"]["id"])
            # grabs the channel ID from the returned data package
            return {"success": True, "channelID": channelID}
            # returns the channel ID
        else:
            return {"success": False, "error": "ChannelID not found"}
            # returns failure dict
    except:
    # if it can't access/fails at 
        return {"success": False, "error": "ChannelID failure"}
        # returns a failure dict



### Point Grabber ###

def pointGrabber(state, channel: str) -> dict:
    """The function that grabs the channel points via GraphQL"""

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type
    
    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Channel Point Operation"],
        "variables": {
            "channelLogin": channel
            # which channel to "login" to
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Channel Point Hash"],
                "version": int(hashMap["Channel Point Version"])
                # this hash is found in devTools console, (search for balance -> GQL with "ChannelPointsContext" operation)
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"
            pointData = data["data"]["community"]["channel"]["self"]["communityPoints"]
            # stores the location of the points in the data json
            points = pointData.get("balance", 0)
            # grabs the actual points (returns 0 if none found)
            caseName = data["data"]["community"]["displayName"]
            # stores the case sensitive name (visual thing)
            pointsName = data["data"]["community"]["channel"]["communityPointsSettings"]["name"]
            # gets the name of the channel points
            try:
                return {"success": True, "error": "None", "points": points, "caseName": caseName, "pointsName": pointsName}
                # returns a dictionary with the formatted name

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data!"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Streak Grabber ###

def streakGrabber(state, channel: str, channelID:str = None) -> dict:
    """The function that grabs streak information"""

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type
    
    if channelID == None:
    # if no channelID is passed
        tempChannelID = channelIDGrab(state, channel)
        # calls the channelIDGrab with the channel
        if tempChannelID["success"]:
        # if the channel ID dictionary is a success
            channelID = tempChannelID["channelID"]
            # grabs the channel ID
    
    if channelID != None:
    # if the channelID is now not None
        payload = {
        # forms a payload from the required information
            "operationName": hashMap["Streak Operation"],
            "variables": {
                "channelID": str(int(channelID)),
                # ensures the channelID is in string form
                "shouldIncludeAllSuspendedStreaks": False
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": hashMap["Streak Hash"],
                    "version": int(hashMap["Streak Version"])
                    # this hash is found in devTools console, (search for watch streak -> GQL with "RewardList" operation)
                }
            }
        }

        try:
        # tries to make a request
            request = reqSession.post(rURL, json = payload, headers = headers)
            # forms a data request
            data = request.json()
            # stores the resulting data json
        except Exception as reqErr:
        # if there's an error (typically network-related)
            return {"success": False, "error": reqErr}
            # returns dictionary with fail and error

        try:
        # tries to read the received data file
            if data and data["data"]:
            # checks if the data package is valid and that there's a header for "data"
                streak = data["data"]["channel"]["self"]["watchStreakMilestone"]["watchStreakMilestone"]
                # stores the location of the streak in the data json
                expires = data["data"]["channel"]["self"]["watchStreakMilestone"]["expiresAt"]
                # grabs the expiry data
                if expires:
                # if the expiry date has a value
                    expiryDate = expires
                    # stores the expiry date
                else:
                # if there's no value
                    expiryDate = None
                    # sets none                       
                try:
                    return {"success": True, "error": "None", "streak": streak["value"], "channelID": channelID, "expires": expiryDate}
                    # returns a dictionary with success

                except Exception as twErr:
                # saves the error as tw(itch)Err(or)
                    return {"success": False, "error": f"{str(twErr)}"}
                    # returns a dictionary with failure
            else:
            # if the data package isn't valid and/or there's no data header
                return {"success": False, "error": "No data received"}
                # returns a dictionary with failure

        except Exception as dtErr:
        # saves the error as d(a)t(a)Err(or)
            return {"success": False, "error": f"{str(dtErr)}"}
            # returns a dictionary with failure
    else:
    # if there's still no ID
        return {"success": False, "error": "No channelID!"}
        # returns a dictionary with failure



### Status Grabber ###

def statusGrabber(state, channel: str) -> dict:
    """The function that checks user status in a channel"""
    
    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Channel Status Operation"],
        "variables": {
            "channelLogin": channel
            # which channel to "login" to
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Channel Status Hash"],
                "version": hashMap["Channel Status Version"]
                # this hash is found in devTools console, (search for GQL with "Chat_ChannelData" operation)
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
                selfData = data["data"]["channel"]["self"]
                # grabs the nested channel data
                editor = selfData["isEditor"]
                # boolean for editor
                vip = selfData["isVIP"]
                # boolean for VIP
                mod = selfData["isModerator"]
                # boolean for VIP

                return {"success": True, "error": "None", "editor": editor, "vip": vip, "mod": mod}  
                # returns a dictionary with success

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Predict Info Grabber ###

def grabPrediction(state, channel: str) -> dict:
    """The function that grabs prediction data"""

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Prediction Operation"],
        "variables": {
            "channelLogin": channel
            # which channel to "login" to
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Prediction Hash"],
                "version": hashMap["Prediction Version"]
                # this hash is found in devTools console, (search for GQL with "predictionContext" operation)
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
                channelData = data["data"]["community"]["channel"]
                # nested data
                canPredict = channelData["predictionSettings"]["isEligibleForPredictions"]
                # boolean for if the user can predict or not
                activePredicts = channelData["activePredictionEvents"]
                # list of active prediction events
                lockedPredicts = channelData["lockedPredictionEvents"]
                # list of locked prediction events
                resolvedPredicts = channelData["resolvedPredictionEvents"]["edges"]
                # list of ended predictions
                ownPredicts = channelData.get("self", False)
                # list of your own predictions (may not exist)
                if ownPredicts:
                # if the grab was successful
                    ownPredicts = ownPredicts["recentPredictions"]
                    # grabs the further dictionary with recent bets
                return {"success": True, "error": "None", "allowed": canPredict, "active": activePredicts, "locked": lockedPredicts, "resolved": resolvedPredicts, "recents": ownPredicts}  
                # returns a dictionary with success

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Predict Sender / Better ###

def sendPrediction(state, bet: int, eventID: str, outcomeID: str) -> dict:
    """Function that makes a bet (prediction) on given channel"""

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Bet Operation"],
        "variables": {
            "input": {
                "eventID": eventID,
                "outcomeID": outcomeID,
                "points": bet,
                "transactionID": uuid.uuid4().hex
                # 32-character uuid, no dashes (hex)
            }
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Bet Hash"],
                "version": hashMap["Bet Version"]
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
            # tries to get the prediction information from the data
                predictionData = data["data"]["makePrediction"]
                # nested data

                if predictionData["error"] == "null" or not predictionData["error"]:
                # if the error field is null (no error)
                    return {"success": True, "error": "None"}  
                    # returns a dictionary with success
                else:
                # if it's not null
                    return {"success": False, "error": predictionData["error"]}
                    # returns the dictionary with the given error

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Start Prediction (Mod-Only) ###

def startPrediction(state, title: str, duration: int, outcomes: list, channelID:str = None) -> dict:
    """Function that starts a bet (prediction) on given channel
        Outcomes needs to be a list with 10 > outcomes >= 2, in format: \n 
        [{"title": opt1, "color": "BLUE"}, {"title": opt2, "color": "PINK"}]
        \n If more than 2 options are set, they all use BLUE"""

    print("An attempt was made to start a prediction", title, channelID, duration, outcomes)

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    if channelID == None:
    # if no channelID is passed
        channel = predictChannel
        # grabs the channel from global prediction variable
        tempChannelID = channelIDGrab(state, channel)
        # calls the channelIDGrab with the channel
        if tempChannelID["success"]:
        # if the channel ID dictionary is a success
            channelID = tempChannelID["channelID"]
            # grabs the channel ID

    if channelID != None:
    # if it's now set
        payload = {
        # forms a payload from the required information
            "operationName": hashMap["Prediction Make Operation"],
            "variables": {
                "input": {
                    "title": title,
                    # name of prediction
                    "channelID": str(int(channelID)),
                    # ensures the channelID is in string form
                    "predictionWindowSeconds": duration,
                    # how many seconds the prediction is open for
                    "outcomes": outcomes
                    # list of outcomes
                }
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": hashMap["Prediction Make Hash"],
                    "version": hashMap["Prediction Make Version"]
                }
            }
        }

        try:
        # tries to make a request
            request = reqSession.post(rURL, json = payload, headers = headers)
            # forms a data request
            data = request.json()
            # stores the resulting data json
        except Exception as reqErr:
        # if there's an error (typically network-related)
            return {"success": False, "error": reqErr}
            # returns dictionary with fail and error

        try:
        # tries to read the received data file
            if data and data["data"]:
            # checks if the data package is valid and that there's a header for "data"                    
                try:
                # tries to get the prediction information from the data
                    predictionData = data["data"]["makePrediction"]
                    # nested data

                    if predictionData["error"] == "null" or not predictionData["error"]:
                    # if the error field is null (no error)
                        return {"success": True, "error": "None"}  
                        # returns a dictionary with success
                    else:
                    # if it's not null
                        return {"success": False, "error": predictionData["error"]}
                        # returns the dictionary with the given error

                except Exception as twErr:
                # saves the error as tw(itch)Err(or)
                    return {"success": False, "error": f"{str(twErr)}"}
                    # returns a dictionary with failure
            else:
            # if the data package isn't valid and/or there's no data header
                return {"success": False, "error": "No data received"}
                # returns a dictionary with failure

        except Exception as dtErr:
        # saves the error as d(a)t(a)Err(or)
            return {"success": False, "error": f"{str(dtErr)}"}
            # returns a dictionary with failure
    else:
    # if there's still no ID
        return {"success": False, "error": "No channelID!"}
        # returns a dictionary with failure



### Payout Prediction (Mod-Only) ###

def payoutPrediction(state, eventID: str, outcomeID: str) -> dict:
    """Function that pays out a given prediction"""

    print("An attempt was made to pay out a prediction", eventID, outcomeID)

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Prediction Resolve Operation"],
        "variables": {
            "input": {
                "eventID": eventID,
                "outcomeID": outcomeID
            }
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Prediction Resolve Hash"],
                "version": hashMap["Prediction Resolve Version"]
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
        print(data) # DEBUG
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
            # tries to get the prediction information from the data
                predictionData = data["data"]["cancelPredictionEvent"]
                # nested data

                if predictionData["error"] == "null" or not predictionData["error"]:
                # if the error field is null (no error)
                    return {"success": True, "error": "None"}  
                    # returns a dictionary with success
                else:
                # if it's not null
                    return {"success": False, "error": predictionData["error"]}
                    # returns the dictionary with the given error

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Delete Prediction (Mod-Only) ###

def deletePrediction(state, eventID: str) -> dict:
    """Function that deletes and refunds a given prediction"""

    print("An attempt was made to delete a prediction", eventID)

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Prediction Delete Operation"],
        "variables": {
            "input": {
                "eventID": eventID
            }
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Prediction Delete Hash"],
                "version": hashMap["Prediction Delete Version"]
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
        print(data) # DEBUG
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
            # tries to get the prediction information from the data
                predictionData = data["data"]["makePrediction"]
                # nested data

                if predictionData["error"] == "null" or not predictionData["error"]:
                # if the error field is null (no error)
                    return {"success": True, "error": "None"}  
                    # returns a dictionary with success
                else:
                # if it's not null
                    return {"success": False, "error": predictionData["error"]}
                    # returns the dictionary with the given error

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure



### Lock Prediction (Mod-Only) ###

def lockPrediction(state, eventID: str) -> dict:
    """Function that locks/closes a given prediction"""

    print("An attempt was made to lock a prediction", eventID)

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": hashMap["ClientID"],
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type

    payload = {
    # forms a payload from the required information
        "operationName": hashMap["Prediction Lock Operation"],
        "variables": {
            "input": {
                "eventID": eventID
            }
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Prediction Lock Hash"],
                "version": hashMap["Prediction Lock Version"]
            }
        }
    }

    try:
    # tries to make a request
        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json
        print(data) # DEBUG
    except Exception as reqErr:
    # if there's an error (typically network-related)
        return {"success": False, "error": reqErr}
        # returns dictionary with fail and error

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"                    
            try:
            # tries to get the prediction information from the data
                predictionData = data["data"]["makePrediction"]
                # nested data

                if predictionData["error"] == "null" or not predictionData["error"]:
                # if the error field is null (no error)
                    return {"success": True, "error": "None"}  
                    # returns a dictionary with success
                else:
                # if it's not null
                    return {"success": False, "error": predictionData["error"]}
                    # returns the dictionary with the given error

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data received"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure





### Authorisation Token "Storage" ###

class AppState:
    """A class to store the authorisation token"""
    def __init__(self):
        self.authToken = None
        # simply stores the auth token here, so that everything can access it





### Point/Streak/Predict Manager ###

class PointWorker(QObject):
    """A class to handle point/streak grabbing"""
    # signals to communicate with UI
    pointWorkerProgress = pyqtSignal(dict)
    # stores the percentage, channel name and points inside a pyqt signal, to update UI
    pointWorkerDone = pyqtSignal(int, int, list, int)
    # gets set when done

    def __init__(self, state, channels):
        super().__init__()
        self.state = state
        # stores the appstate (gets pushed to pointGrabber, has token)
        self.channels = channels
        # stores channels passed
        self.running = True
        # sets running to true
        self.streakMap = streakMap 
        # the streak map that contains the streak-grabbable channels
        self.overrideChannel = overrideChannel
        # the channel to potentially override with

    @pyqtSlot()
    def run(self):
    # runs the point worker

        csvEntries = {}
        # creates a new map to place each channel into
        self.progressDict = {}
        # empty dictionary, filled per loop, sent to UI
        self.expiringList = []
        # empty list for expiring streak channels
        self.totalPoints = 0
        # stores the total amount of points gathered
        self.errorCount = 0
        # starts a counter for errors (how many channels couldn't be saved)
        self.maxStreak = 0
        # starts a maximum streak store

        if self.overrideChannel == None:
        # if no override channel is defined, goes through the list

            for num, channel in enumerate(self.channels):
            # goes through each channel in the list (gets channel and index)

                errorBool = False
                # defaults the error boolean to false

                if enablePoints:
                # if the point grabbing is enabled
                    points = pointGrabber(self.state, channel)
                    # calls the point grabber to get the channel's point amount

                    if points["success"]:
                    # checks the points entry for success boolean
                        foundPoints = int(points["points"])
                        # stores the points
                        self.totalPoints = (self.totalPoints + foundPoints)
                        # adds the channel's points to the total amount
                    else:
                    # if the point entry success is False (something went wrong)
                        foundPoints = "Not found"
                        # stores string
                        errorBool = True
                        # sets the error bool to true (will tell the UI to display error text)
                        self.errorCount = (self.errorCount + 1)
                        # on error, adds an error to counter
                else:
                # if point checking is disabled
                    foundPoints = "Not checked"
                    self.totalPoints = "Not checked"
                    # sets the points to nothing

                if enableStreaks:
                # if the streak-grabbing is enabled
                    if enablePoints:
                    # if points and streaks are enabled, slows down the process a bit more
                        QThread.msleep(1000)
                        # sleeps for a second (slows down for UX + Twitch)

                    if activeOnly:
                    # if the boolean for the "active streaks only" is true, won't check *all* channels
                        if channel in streakMap:
                        # if the channel is in the streak map
                            streak = streakGrabber(self.state, channel, int(streakMap[channel]["ID"]))
                            # calls the streak grabber with the channel ID (doesn't need to make a second request in this case)
                        else:
                        # if the channel *isn't* in the map
                            streak = {"success": False, "error": "No active streak stored"}
                            # forms a custom dictionary to pass to csv
                    else:
                    # if the boolean isn't active only, goes through all
                        if channel in streakMap:
                        # if the channel is in the streak map
                            streak = streakGrabber(self.state, channel, int(streakMap[channel]["ID"]))
                            # calls the streak grabber with the channel ID (doesn't need to make a second request in this case)
                        else:
                        # if the channel isn't in the map
                            streak = streakGrabber(self.state, channel)
                            # calls the streak grabber to get the streak

                    if streak["success"]:
                    # if the streak success entry is true
                        streakNum = int(streak["streak"])
                        # gets the streak
                        if not streak.get("expires") == None:
                        # if there's a set expiry date (not None)
                            expiring = True
                            # sets the flag to True so it gets spotted
                            expiryDate = streak.get("expires", "Soon")
                            # gets the date from the dictionary (has a fallback of "Soon")
                            self.expiringList.append({channel["expires"]: expiryDate})
                            # adds the expiring channel's expiry date to a list to display at the end ("soon" as fallback)
                        else:
                        # if there's no date (not expiring)
                            expiring = False
                            # sets the flag to False so it doesn't get set

                        if streakNum > 1 and channel not in streakMap and autoAddStreaks:
                        # if there's a streak present and the channel isn't stored yet, plus the config option to add them to the streak map is on
                            streakMap[channel] = {
                                "ID": int(streak["channelID"]),
                                "Active": True
                            }
                            # stores the channel with its ID and state
                        elif streakNum == 0 and channel in streakMap and autoRemoveStreaks:
                        # if there's no streak, the channel is in the map and the option to remove stales is on
                            streakMap[channel] = {
                                "ID": int(streak["channelID"]),
                                "Active": False
                            }
                            # sets the streak state to false
                    else:
                    # if the streak entry is false
                        streakNum = 0
                        # sets to default of 0
                        errorBool = True
                        # sets bool for error to true
                        expiring = False
                        # sets the bool for expiry to False

                    if streakNum > self.maxStreak:
                    # if the current streak is larger than the stored max streak
                        self.maxStreak = streakNum
                        # reassigns the max streak to match

                else:
                # if the streak-grabbing is disabled
                    streakNum = 0
                    # sets the streak number to 0
                    expiring = False
                    # sets to false automatically
                
                if enablePoints and not enableStreaks:
                # if only points are on
                    errorReason = points.get("error", "None")
                    # gets the error reason from points, None if none is found
                else:
                # if points are off or streaks are on
                    errorReason = streak.get("error", "None")
                    # gets the error reason from streak instead, None if none found

                if enableErrorLog:
                # if errors should be logged to CSV
                    csvEntries[channel] = {
                        "points": foundPoints,
                        "streak": streakNum,
                        "error": errorBool,
                        "reason": errorReason
                    }
                    # creates a csv entry for the channel with the error and its reason
                else:
                # if errors shouldn't be logged to CSV
                    csvEntries[channel] = {
                        "points": foundPoints,
                        "streak": streakNum,
                        "error": errorBool
                    }
                    # stores the points and streak in the channel's csv entry

                if expiring:
                # if there's an expiration date
                    self.progressDict = {
                        "type": "Full",
                        "channel": channel,
                        "index": num,
                        "pointsOn": enablePoints,
                        "points": foundPoints,
                        "error": errorBool,
                        "total": self.totalPoints,
                        "streaksOn": enableStreaks,
                        "streak": streakNum,
                        "expiresAt": streak["expires"]
                    }
                    # forms a progress dictionary to pass
                else:
                # if there's no expiry date
                    self.progressDict = {
                        "type": "Full",
                        "channel": channel,
                        "index": num,
                        "pointsOn": enablePoints,
                        "points": foundPoints,
                        "error": errorBool,
                        "total": self.totalPoints,
                        "streaksOn": enableStreaks,
                        "streak": streakNum,
                        "expiresAt": False
                    }
                    # forms a progress dictionary to pass

                self.pointWorkerProgress.emit(self.progressDict)
                # sends a progress update to the headless UI updater

                QThread.msleep(1000)
                # waits 1s/channel

            with open(streakMapPath, "w") as strk:
            # opens the streak config location
                json.dump(streakMap, strk, indent=3)
                # dumps the map into file
            
            self.csvWriter(csvEntries, self.errorCount, self.maxStreak, self.expiringList, None)
            # calls the csvWriter with the formed map (dictionary) and the number of errors (gets passed to finished UI)

        else:
        # if a channel override is set (only one channel)

            channel = self.overrideChannel
            # sets the channel to the override

            points = pointGrabber(self.state, channel)
            # calls the point grabber to get the channel's point amount

            if points["success"]:
            # checks the points entry for success boolean
                foundPoints = int(points["points"])
                # stores the points
                errorBool = False
                # sets the error bool to false
                self.totalPoints = foundPoints
                # total is the channel's total
            else:
            # if the point entry success is False (something went wrong)
                foundPoints = "Not found"
                # stores string
                errorBool = True
                # sets the error bool to true (will tell the UI to display error text)
                self.errorCount += 1
                # on error, adds an error to counter

            streak = streakGrabber(self.state, channel)
            # calls the streak grabber to get the streak

            if streak["success"]:
            # if the streak success entry is true
                streakNum = int(streak["streak"])
                # gets the streak
            else:
            # if the streak entry is false
                streakNum = 0
                # sets to default of 0

            if enableErrorLog:
            # if error logging is enabled
                csvEntries[channel] = {
                    "points": foundPoints,
                    "streak": streakNum,
                    "error": errorBool,
                    "reason": f"{points["error"]}, {streak["error"]}"
                }
                # forms the csvEntry for the channel
            else:
            # error logging disabled
                csvEntries[channel] = {
                    "points": foundPoints,
                    "streak": streakNum,
                    "error": errorBool
                }
                # forms the csvEntry for the channel, without the error reason

            self.progressDict = {
                "type": "Single",
                "channel": channel,
                "index": 1,
                "pointsOn": enablePoints,
                "points": foundPoints,
                "error": errorBool,
                "total": self.totalPoints,
                "streaksOn": enableStreaks,
                "streak": streakNum
            }
            # forms a progress dictionary to pass

            self.pointWorkerProgress.emit(self.progressDict)
            # sends a progress update to the headless UI updater

            self.csvWriter(csvEntries, self.errorCount, streakNum, None, foundPoints)
            # calls the csvWriter with the formed map (dictionary) and the number of errors (gets passed to finished UI)

            

### CSV Writer ###

    def csvWriter(self, csvEntries: dict, errors: int, maxStreak: int, expiryList: list=None, overridePoints: int = None):
        """The function that writes the final CSV"""

        rows = []
        # starts with no rows
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        # takes the current timestamp (doesn't need second-level precision for each entry)

        for channel, values in csvEntries.items():
        # goes through each channel and gets both the points and channel
            rows.append({
                "Channel": channel,
                # stores the channel name
                "Points": values.get("points", "Not found"),
                # stores the points (not found if can't find)
                "Streak": values.get("streak", "Not found"),
                # stores the streak (not found if it can't find)
                "Error": values.get("error", ""),
                # stores the error boolean (nothing if none is set)
                "Reason": values.get("reason", ""),
                # stores the error reason (nothing if none is set)
                "Timestamp": timestamp
                # stores the timestamp (can be used to calculate points/timeframe later)
            })
            # adds the given parameters to a new row

        dataframe = pnd.DataFrame(rows)
        # forms a dataframe from the formed rows

        dataframe.to_csv(csvPath, index=False)
        # pushes everything to the csv file

        if not expiryList:
        # if the expiry list isn't defined (not passed)
            expiryList = []
            # makes an empty list
        if not overridePoints:
        # if the singlePoints wasn't passed
            overridePoints = 0
            # sets to 0

        self.pointWorkerDone.emit(errors, maxStreak, expiryList, overridePoints)
        # once done, sends a signal to the finished pyqt signal with the error count, highest streak and expiration list
        self.running = False
        # stops itself





### Prediction Class ###

class PredictionWorker(QObject):
    """A class to handle the prediction data grabbing and manipulation"""
    dataSignal = pyqtSignal(dict, dict)
    """A pyQt signal to send data back to handler function"""
    stopSignal = pyqtSignal()
    """A pyQt signal to indicate the worker task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True

        ctrl.timerSwap.connect(self.timerChange)
        # connects the timer swap signal to the timer change function
        ctrl.predictionTimerOverride.connect(self.timerOverride)
        # connects the timer override signal to the timer override function
        ctrl.makeBet.connect(self.bet)
        # connects the makeBet signal to the bet function
        ctrl.newChannelSignal.connect(self.predictChannelSwap)
        # connects the new channel signal to the swapper

        self.timer = 15
        # a timer stored here that determines how often the refreshes occur
        self.refresh = threading.Event()
        # a threading event to store the timer in
        self.stopSignal.connect(self.stopper)
        # connects the stop signal to the stopper

        self.dataLock = threading.Lock()
        # a threading lock to prevent multiple data calls at once (causes old data to appear during/after)



### Prediction Channel Swap ###

    def predictChannelSwap(self):
        """Function to update the prediction channel"""
        global predictChannel
        # global -> local

        newChannel = ctrl.newChannelQueue.get_nowait()
        # grabs the channel from the queue

        predictChannel = newChannel
        # updates the prediction channel

        self.timerOverride()
        # calls the override to get new data quickly



### Run Prediction Worker ###

    def run(self):
        """Function that loops function calls"""
        while self.running:
        # while the running status is True
            self.refresh.wait(timeout=self.timer)
            # waits the timer duration, if a threading event is not set before that
            self.refresh.clear()
            # clears the event queue
            self.intermed()
            # keeps calling the intermediary command with a timed cooldown

### Stop Prediction Worker ###

    def stopper(self):
        """Function to stop the worker"""
        self.running = False
        # sets running status to False, stops running



### Override Timer ###

    def timerOverride(self) -> threading.Event:
        """Function that sets an event, overriding the current timer"""
        self.refresh.set()
        # sets an event, forcing run() to immediately run intermed, refreshing data faster



### Timer Change ###

    def timerChange(self, newTime: int):
        """Function that changes the internally stored timer (to speed up or slow down refreshing)"""
        self.timer = newTime
        # swaps the timer to the new time



### Intermed ###

    def intermed(self) -> pyqtSignal:
        """Intermediary function that merges two data grab function calls"""
        if not self.dataLock.acquire(blocking=False):
        # if the dataLock is in use, this function is already running a different call, if not, grabs the lock
            return
            # doesn't proceed
        pData = self.getPrediction()
        # calls getPrediction to get new data
        bData = self.getBalance()
        # calls getBalance to get new data
        self.dataSignal.emit(pData, bData)
        # sends the returned dictionary through the pyQt signal
        self.dataLock.release()
        # releases the lock, allowing a new instance of intermed() to run



### Get Prediction ###

    def getPrediction(self) -> dict:
        """Function to get prediction data"""

        return grabPrediction(self.state, predictChannel)
        # calls predictGrabber with the state and globally defined predict channel



### Get Balance ###

    def getBalance(self) -> dict:
        """Function to get balance"""

        return pointGrabber(self.state, predictChannel)
        # calls pointGrabber with the state and globally defined predict channel



### Send Bet ###

    def bet(self, bet: int, eventID: str, outcomeID: str, selected: str, balance: int):
        """Function to make/send a bet"""
  
        betInfo = sendPrediction(self.state, bet, eventID, outcomeID)
        # calls the prediction sender with the state, the bet amount and the prediction details

        if betInfo["success"]:
        # if the return is a success
            ctrl.taskChange.emit(f"Bet {bet:,.0f} on {selected}\nMay the odds be ever in your favor!")
            # sets info text
            ctrl.mainWindow.predictAmountLine.setText("")
            # clears the text
            newBal = int(balance - bet)
            # calculates the new balance 
            ctrl.mainWindow.balanceOverride.emit(newBal)
            # sends a signal to indicate the new balance (to give instant UI update, rather than wait for next auto-update)
        else:
        # if the return isn't a success
            err = betInfo["error"]
            # grabs the error message from the return
            ctrl.taskChange.emit(f"Failed to send bet! Error: {err}")
            # updates user on error





### Mod Window Class ###

class ModWindow(QObject):
    """A class to handle the moderator window"""

    dataSignal = pyqtSignal()
    """A pyQt signal to send data back to handler function"""
    stopSignal = pyqtSignal()
    """A pyQt signal to indicate the worker task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True

### Manage Prediction ###

    def predictionManager(self, state, action:str, title:str=None, eventID:str=None, outcomeID:str=None, outcomes:list=None, duration:int=None, channelID:int=None):
        """Function to manage predictions\n
        Start = title, duration, outcomes, channelID\n
        Delete = eventID\n
        Payout = eventID, outcomeID\n
        Lock = eventID\n"""
        # long, very informative doc, mmmyeesss

        modStatus = ctrl.mainWindow.modCheck()
        # gets the mod status from modCheck

        if not modStatus:
        # if the return is false
            return
            # stops (can't do anything if not a mod anyway)

        if action == "Start":
        # start prediction (make a new one)
            strDict = startPrediction(state, title, duration, outcomes, channelID)
            # calls prediction starter
            if strDict["success"]:
            # if the return has success True
                print("made prediction yippie")
            else:
                print("didn't make prediction saj")

        elif action == "Delete":
        # delete the prediction
            delDict = deletePrediction(state, eventID)
            # calls prediction deleter
            if delDict["success"]:
                print("deleted prediction yippie")
            else:
                print("didn't delete, saj")

        elif action == "Payout":
        # pay out an option
            payDict = payoutPrediction(state, eventID, outcomeID)
            # calls prediction payout
            if payDict["success"]:
                print("paid out prediction yippie")
            else:
                print("didn't pay out, saj")

        elif action == "Lock":
        # lock/close prediction
            lockDict = lockPrediction(state, eventID)
            # calls prediction locker
            if lockDict["success"]:
                print("locked prediction, yippie")
            else:
                print("didn't lock prediction, saj")





### Help Window ###

class HelpWindow(QObject):
    """A class to handle the help window"""

    dataSignal = pyqtSignal()
    """A pyQt signal to send data back to handler function"""
    stopSignal = pyqtSignal()
    """A pyQt signal to indicate the worker task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True

        self.stopSignal.connect(self.stopper)
        # connects the stop signal to the stopper
        ctrl.helpLifeSignal.connect(self.lifeCheck)
        # connects the life signal to the lifecheck function

### Run Help Worker ###

    def run(self):
        """Function that runs the help window"""
        if hasattr(self, "helpWindowSP") and self.helpWindowSP.poll() is None:
        # checks if the window is already running and defined
            self.helpWindowSP.terminate()
            # terminates
            self.helpWindowSP.kill()
            # kills
        self.helpWindowSP = subprocess.Popen([helpWindowPath], cwd=directory, stdin=subprocess.PIPE, bufsize=0, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # opens the help window exe, passes the current working directory and allows input

### Stop Help Worker ###

    def stopper(self):
        """Function to stop the worker"""
        self.running = False
        # sets running status to False, stops running

### Life Check ###

    def lifeCheck(self):
        """Function to check if the window is still alive"""
        if self.helpWindowSP.poll() is not None:
        # polls if the window is still alive (not alive if this is True)
            self.stopper()
            # calls the stop function
            ctrl.helpStoppedSignal.emit()
            # sends a signal to inform the window is stopped
            return
            # stops running it





### History Window Class ###

class HistoryWindow(QObject):
    """A class to handle the history window"""

    dataSignal = pyqtSignal()
    """A pyQt signal to send data back to handler function"""
    stopSignal = pyqtSignal()
    """A pyQt signal to indicate the worker task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True

        self.stopSignal.connect(self.stopper)
        # connects the stop signal to the stopper
        ctrl.historyLifeSignal.connect(self.lifeCheck)
        # connects the life signal to the lifecheck function

### Run History Worker ###

    def run(self):
        """Function that runs the history window"""
        if hasattr(self, "historyWindowSP") and self.historyWindowSP.poll() is None:
        # checks if the window is already running and defined
            self.historyWindowSP.terminate()
            # terminates
            self.historyWindowSP.kill()
            # kills
        self.historyWindowSP = subprocess.Popen([historyWindowPath], cwd=directory, stdin=subprocess.PIPE, bufsize=0, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # opens the history window exe, passes the current working directory and allows input

### Stop History Worker ###

    def stopper(self):
        """Function to stop the worker"""
        self.running = False
        # sets running status to False, stops running

### Life Check ###

    def lifeCheck(self):
        """Function to check if the window is still alive"""
        if self.historyWindowSP.poll() is not None:
        # polls if the window is still alive (not alive if this is True)
            self.stopper()
            # calls the stop function
            ctrl.historyStoppedSignal.emit()
            # sends a signal to inform the window is stopped
            return
            # stops running it





### Details Window Class ###

class DetailsWindow(QObject):
    """A class to handle the details window"""

    dataSignal = pyqtSignal()
    """A pyQt signal to send data back to handler function"""
    stopSignal = pyqtSignal()
    """A pyQt signal to indicate the worker task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True

        self.stopSignal.connect(self.stopper)
        # connects the stop signal to the stopper
        ctrl.detailsDataSignal.connect(self.detailsInput)
        # connects the details data signal to the stopper (main -> ctrl -> here -> details window)

### Run Details Worker ###

    def run(self):
        """Function that runs the details window"""
        if hasattr(self, "displayWindowSP") and self.displayWindowSP.poll() is None:
        # checks if the window is already running and defined
            self.displayWindowSP.terminate()
            # terminates
            self.displayWindowSP.kill()
            # kills
        self.displayWindowSP = subprocess.Popen([detailWindowPath], cwd=directory, stdin=subprocess.PIPE, bufsize=0, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # opens the prediction display window exe, passes the current working directory and allows input

### Stop Details Worker ###

    def stopper(self):
        """Function to stop the worker"""
        self.running = False
        # sets running status to False, stops running

### Handle Input ###

    def detailsInput(self, inputDict: dict):
        """Function to manage the details window input"""

        if self.displayWindowSP.poll() is not None:
        # polls if the window is still alive (not alive if this is True)
            self.stopper()
            # calls the stop function
            ctrl.detailsStoppedSignal.emit()
            # sends signal to inform the window is stopped
            return
            # stops running it
        
        try:
        # if the window is alive, tries to send data (try in case the connection fails)
            dataPacket = json.dumps(inputDict, default=str)
            # converts the dictionary into json (uses default=str because of datetime objects)
            self.displayWindowSP.stdin.write(dataPacket)
            # writes the packet to the display window program (sends)
            self.displayWindowSP.stdin.flush()
            # ensures all messages are sent
        except:
        # if it can't reach the window (it's gone)
            self.stopper()
            # calls the stop window





### Controller Class ###

class SuperController(QObject):
    """A class to handle the cross-class/function communication and startup"""

### Main Window ###

    starterWindowDone = pyqtSignal(str)
    """A pyQt signal to signal the starter window is done loading"""
    taskChange = pyqtSignal(str)
    """A pyQt signal to tell the main window to change the current task string"""

### Super Controller ###

    newPData = pyqtSignal(dict)
    """A pyQt signal to send data to mainWindow's predictUpdateUI"""

### Prediction Worker ###

    timerSwap = pyqtSignal(int)
    """A pyQt signal to change the prediction/balance refresh timer"""
    predictionTimerOverride = pyqtSignal()
    """A pyQt signal to set an event and immediately override timer"""
    makeBet = pyqtSignal(int, str, str, str, int)
    """A pyQt signal to form a bet (bet: int, eventID: str, outcomeID: str, name: str, balance: int)"""
    stopPredictionWorker = pyqtSignal()
    """A pyQt signal to stop the prediction worker"""
    newChannelSignal = pyqtSignal()
    """A pyQt signal to change the prediction channel"""
    newChannelQueue = queue.Queue()
    """A Queue to place a new prediction channel into"""

### Details Worker ###

    detailsDataSignal = pyqtSignal(dict)
    """A pyQt signal to send a dictionary of data to the prediction details window"""
    startDetailSignal = pyqtSignal()
    """A pyQt signal to start the details view"""
    detailsStoppedSignal = pyqtSignal()
    """A pyQt signal to inform the window has stopped"""

### Help Worker ###

    startHelpSignal = pyqtSignal()
    """A pyQt signal to start the help view"""
    helpLifeSignal = pyqtSignal()
    """A pyQt signal to poll the status of the help window"""
    helpStoppedSignal = pyqtSignal()
    """A pyQt signal to inform the window has stopped"""

### Mod Worker ###

    startModSignal = pyqtSignal()
    """A pyQt signal to start the mod view"""
    modLifeSignal = pyqtSignal()
    """A pyQt signal to poll the status of the mod window"""
    modStoppedSignal = pyqtSignal()
    """A pyQt signal to inform the window has stopped"""

### History Worker ###

    startHistorySignal = pyqtSignal()
    """A pyQt signal to start the history view"""
    historyLifeSignal = pyqtSignal()
    """A pyQt signal to poll the status of the history window"""
    historyStoppedSignal = pyqtSignal()
    """A pyQt signal to inform the window has stopped"""

### Init ###

    def __init__(self):
        super().__init__()

        self.state = appState
        # stores the app state "storage"

        self.startWindow = StarterWindow()
        # stores and starts the starter window class
        self.startWindow.show()
        # shows the window
        self.mainWindow = None
        # not defined yet
        self.mainDefined = False
        # boolean to store main window definition state

        self.startWindow.configLoaded.connect(self.mainStarter)
        # calls mainStarter once the start window is done with config
        self.startWindow.starterDone.connect(self.mainContinuer)
        # when the starter is done, signals the next stage (mainWindow -> extractAuthToken)

        self.profilePath = profilePath
        # stores the profile path from global
        self.profileName = profileName
        # stores the profile name from global

        self.browserProfile = QWebEngineProfile(self.profileName, self)
        # sets the browser profile to the given profile (default is Default)
        self.browserProfile.setCachePath(os.path.join(self.profilePath, self.profileName))
        # sets the cache path (<installation>/Data/Profile/<profileName>/)
        self.browserProfile.setPersistentStoragePath(os.path.join(self.profilePath, self.profileName))
        # sets the storage path (<installation>/Data/Profile/<profileName>/)

        self.settings = self.browserProfile.settings()
        # manages the browser settings
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        # ensures local storage is enabled 
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        # ensures plugins are allowed to function
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # ensures javascript is enabled

        self.stopPredictionWorker.connect(self.predictionWorkerStop)
        # connects the signal to the function

    ### Details View ###

        self.detailsWindowBool = False
        """Boolean to check if details window is active"""
        self.startDetailSignal.connect(self.startDetailView)
        # connects the starter signal to the function
        self.detailsStoppedSignal.connect(self.detailsWorkerStop)
        # connects the stop signal to the function

    ### Help View ###

        self.helpWindowBool = False
        """Boolean to check if help window is active"""
        self.startHelpSignal.connect(self.startHelpView)
        # connects the starter signal to the function
        self.helpStoppedSignal.connect(self.helpWorkerStop)
        # connects the stop signal to the function

    ### Mod View ###

        self.moderatorWindowBool = False
        """Boolean to check if moderator window is active"""
        self.startModSignal.connect(self.startModView)
        # connects the starter signal to the function

    ### History View ###
        
        self.historyWindowBool = False
        """Boolean to check if history window is active"""
        self.startHistorySignal.connect(self.startHistoryView)
        # connects the starter signal to the function
        self.historyStoppedSignal.connect(self.historyWorkerStop)
        # connects the stop signal to the function



### Main Window Starter ###

    def mainStarter(self):
        """Function to start the main window"""
        if self.mainWindow == None:
        # if mainWindow hasn't been defined yet (first start)
            self.mainWindow = tepmWindow(self.state, self.browserProfile)
            # stores and starts the main window class
        else:
        # if it has been defined (returning)
            pass
            # does nothing (continuer will take care of all)

### Main Window Continuer ###

    def mainContinuer(self, action):
        """Function to progress the main window"""
        self.startWindow.hide()
        # hides the start window

        if not self.mainDefined:
        # if the boolean is false, meaning mainWindow hasn't been defined yet
            self.starterWindowDone.emit(action)
            # emits signal to inform mainWindow it's done
            self.mainDefined = True
            # sets the boolean to True so it doesn't do it next time
            self.mainWindow.show()
            # shows the main window
        else:
        # boolean is True, meaning it has been defined and is hiding
            self.windowSwap(action)
            # calls the window swap with the action passed
    


### Worker Starter Generic Function ###

    def startWorker(self, workerClass, dataFunction, threadName:str):
        """Shared function to start the different worker classes"""
        
        thread = QThread()
        # makes a thread for the passed worker class
        thread.setObjectName(threadName)
        # object name (debug)

        worker = workerClass(self.state)
        # assigns worker to the passed class, passes state
        worker.moveToThread(thread)
        # sets the worker to use the formed thread

        thread.started.connect(worker.run)
        # when the thread starts, runs the worker

        worker.stopSignal.connect(thread.quit)
        # connects the worker stopping to quitting the thread
        # the class must have a signal called "stopSignal" for this to work

        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        # deletes both the thread and the worker when the thread is done

        worker.dataSignal.connect(dataFunction)
        # connects the passed function (function that handles the next data) to the worker's signal
        # the class must have a signal called "dataSignal" that connects to this

        thread.start()
        # starts the thread

        return worker, thread
        # returns the references to both the worker and thread



### Prediction Worker Start ###

    def predictionWorkerStart(self):
        """Function to start the prediction worker thread/class"""
        self.predictWorker, self.predictThread = self.startWorker(
            PredictionWorker,
            # the class to start
            self.predictionDataGrab,
            # the data handler
            "PredictionThread"
            # name of the thread
        )
        # calls startWorker with given arguments to start a thread/worker for prediction grabbing 

### Prediction Worker Stop ###

    def predictionWorkerStop(self):
        """Function to stop the prediction worker thread/class"""
        if getattr(self, "predictWorker", None):
        # if the worker exists and is defined
            try:
            # tries (this crashes annoyingly frequently otherwise)
                self.predictWorker.stopSignal.emit()
                # sends a signal telling the worker to stop
            except:
            # if it can't send the signal
                pass 
                # it doesn't actually exist, it just hallucinates
            self.predictWorker = None
            # reassigns as None

        if getattr(self, "predictThread", None):
        # if the thread exists and is defined
            self.predictThread.quit()
            # calls for the thread to quit (stop)
            self.predictThread.wait()
            # waits for the thread to stop
            self.predictThread = None
            # reassigns as None



### Details View Worker Start ###

    def detailsWorkerStart(self):
        """Function to start the details worker thread/class"""
        self.detailsWorker, self.detailsThread = self.startWorker(
            DetailsWindow,
            # assigns the class
            self.detailsData,
            # assigns the return data handler
            "DetailsThread"
            # names the thread
        )

### Details View Worker Stop ###

    def detailsWorkerStop(self):
        """Function to stop the details worker thread/class"""
        if getattr(self, "detailsWorker"):
        # if the worker exists and is defined
            try:
            # tries (this crashes annoyingly frequently otherwise)
                self.detailsWorker.stopSignal.emit()
                # sends a signal telling the worker to stop
            except:
            # if it can't send the signal
                pass 
                # it doesn't actually exist, it just hallucinates
            self.detailsWorker = None
            # reassigns as None

        if getattr(self, "detailsThread", None):
        # if the thread exists and is defined
            self.detailsThread.quit()
            # calls for the thread to quit (stop)
            self.detailsThread.wait()
            # waits for the thread to stop
            self.detailsThread = None
            # reassigns as None
        self.detailsWindowBool = False
        # swaps the boolean to False to allow a new window creation



### Help View Worker Start ###

    def helpWorkerStart(self):
        """Function to start the help worker thread/class"""
        self.helpWorker, self.helpThread = self.startWorker(
            HelpWindow,
            # assigns the class
            self.helpData,
            # assigns the return data handler
            "HelpThread"
            # names the thread
        )

### Help View Worker Stop ###

    def helpWorkerStop(self):
        """Function to stop the help worker thread/class"""
        if hasattr(self, "helpWorker") and self.helpWorker:
        # if the worker exists and is defined
            try:
            # tries (this crashes annoyingly frequently otherwise)
                self.helpWorker.stopSignal.emit()
                # sends a signal telling the worker to stop
            except:
            # if it can't send the signal
                pass 
                # it doesn't actually exist, it just hallucinates
            self.helpWorker = None
            # reassigns as None

        
        if hasattr(self, "detailsThread") and self.helpThread:
        # if the thread exists and is defined
            self.helpThread.quit()
            # calls for the thread to quit (stop)
            self.helpThread.wait()
            # waits for the thread to stop
            self.helpWorker = None
            # reassigns as None
        self.helpWindowBool = False
        # swaps the boolean to False to allow a new window creation



### History View Worker Start ###

    def historyWorkerStart(self):
        """Function to start the history worker thread/class"""
        self.historyWorker, self.historyThread = self.startWorker(
            HistoryWindow,
            # assigns the class
            self.historyData,
            # assigns the return data handler
            "HistoryThread"
            # names the thread
        )

### History View Worker Stop ###

    def historyWorkerStop(self):
        """Function to stop the help worker thread/class"""
        if getattr(self, "historyWorker", None):
        # if the worker exists and is defined
            try:
            # tries (this crashes annoyingly frequently otherwise)
                self.historyWorker.stopSignal.emit()
                # sends a signal telling the worker to stop
            except:
            # if it can't send the signal
                pass 
                # it doesn't actually exist, it just hallucinates
            self.historyWorker = None
            # reassigns as None

        if getattr(self, "historyThread", None):
        # if the thread exists and is defined
            self.historyThread.quit()
            # calls for the thread to quit (stop)
            self.historyThread.wait()
            # waits for the thread to stop
            self.historyThread = None
            # reassigns as None
        self.historyWindowBool = False
        # swaps the boolean to False to allow a new window creation



### Mod View Worker Start ###

    def moderatorWorkerStart(self):
        """Function to start the moderator view worker thread/class"""
        self.moderatorWorker, self.moderatorThread = self.startWorker()
        # incomplete



### Details Data ###

    def detailsData(self, reply: str):
        """?"""
        print(reply)

### Help Data ###

    def helpData(self, reply:str):
        """?"""
        print(reply)

### Mod Data ###

    def modData(self, modAction: dict):
        """Mod data dictionary return reading function"""
        print(modAction)

### History Data ###

    def historyData(self, reply:str):
        """?"""
        print(reply)

### Prediction Data ###

    def predictionDataGrab(self, prediction: dict, balance: dict) -> pyqtSignal:
        """Function to handle prediction data"""

        if prediction["success"]:
        # if it was a success
            activePrediction = prediction["active"]
            # stores the active prediction
            lockedPrediction = prediction["locked"]
            # stores the locked prediction
            resolvedPredictions = prediction["resolved"]
            # stores the resolved prediction
            myPredictions = prediction.get("recents", False)
            # stores user's previous predictions (of the channel)
            if myPredictions:
            # if the dictionary is valid and contains something
                lastPrediction = myPredictions[0]
                # gets the 0th element in the list of predictions
                lastBetID = lastPrediction["event"]["id"]
                # gets the ID of the last prediction
            else:
            # not valid/empty
                lastBetID = False
                # sets gibberish string to not match current

            if len(activePrediction) > 0:
            # if the active predict list has more than 0 elements
                truePrediction = activePrediction[0]
                # grabs the 0th element from the list (now a dictionary)
                truePrediction["type"] = "active"
                # sets the type to active
                rawTimestamp = truePrediction["createdAt"]
                # grabs the raw creation timestamp (YYYY-MM-DDTHH:MM:SS.*ms*Z)

            elif len(lockedPrediction) > 0:
            # if the locked predict list has more than 0 elements
                truePrediction = lockedPrediction[0]
                # grabs the 0th element from the list (now a dictionary)
                truePrediction["type"] = "locked"
                # sets the type to locked
                rawTimestamp = truePrediction["lockedAt"]
                # grabs the lock timestamp
 
            elif len(resolvedPredictions) > 0:
            # if the resolved (passed) predict list has more than 0 elements
                truePrediction = resolvedPredictions[0]["node"]
                # grabs the 0th element from the list (now a dictionary), grabs the node (information)
                truePrediction["type"] = "resolved"
                # sets the type to resolved
                rawTimestamp = truePrediction["endedAt"]
                # grabs the end stamp

            else:
            # channel has no listed predictions (never ran or ran too long ago)
                truePrediction = False
                # sets it to false

            if len(activePrediction) > 0 and len(resolvedPredictions) > 0:
            # if there's an open prediction and old predictions
                truePrediction["resolvedPred"] = resolvedPredictions[0]
                # adds the old prediction (in case the updates are too fast)
            else:
            # if that's not the case (no active or active + no resolved)
                truePrediction["resolvedPred"] = False
                # false boolean in the place of a prediction dictionary
            
            if truePrediction:
            # if there's a prediction of any type
                title = truePrediction["title"]
                # grabs the prediction title
                outcomes = truePrediction["outcomes"]
                # grabs the list of outcomes
                creator = truePrediction["createdBy"]["displayName"]
                # grabs the creator name
                eventID = truePrediction["id"]
                # grabs the event ID from the prediction dictionary

                if eventID == lastBetID:
                # if there's a bet on this prediction
                    votedOutcome = lastPrediction["outcome"]["id"]
                    # gets the ID of the voted option
                    votedSum = lastPrediction["points"]
                    # gets the total bet
                    sumWon = lastPrediction["pointsWon"]
                    # gets the won points
                else:
                # no bet
                    votedOutcome = False
                    votedSum = 0
                    sumWon = 0
                    # sets empty/gibberish standins

                winner = truePrediction["winningOutcome"]
                # grabs the winning outcome (this is null for active/locked)
                timer = truePrediction["predictionWindowSeconds"]
                # how long the timer is (how long the prediction is/was open for)

                timestampUTC = datetime.datetime.fromisoformat(rawTimestamp.replace("Z", "+00:00"))
                # formats it to datetime 
                timestampLocal = timestampUTC.astimezone()
                # swaps to current timezone
                historyStamp = timestampLocal.isoformat()
                # converts the timestamp back to iso format (for prediction history charting)
                predictionStamp = timestampLocal.strftime("%B %#d at %#H:%M:%S")
                # finalizes it into legible format

                if balance["success"]:
                # if the balance returned a success dictionary
                    currentBal = balance["points"]
                    # grabs the points
                    caseName = balance["caseName"]
                    # grabs the case sensitive name
                    pointsName = balance["pointsName"]
                    # grabs the name of the channel points (null if not set)
                else:
                # if not
                    currentBal = 0
                    # sets the balance to 0
                    caseName = False
                    # sets the case sensitive name to False
                    pointsName = False
                    # sets the points' name to False

                finalPrediction = {
                    "success": True,
                    "type": truePrediction["type"],
                    "id": eventID,
                    "title": title,
                    "outcomes": outcomes,
                    "timestamp": predictionStamp,
                    "chartStamp": historyStamp,
                    "creator": creator,
                    "winner": winner,
                    "timer": timer,
                    "localTS": timestampLocal,
                    "balance": currentBal,
                    "caseName": caseName,
                    "votedOutcome": votedOutcome,
                    "votedSum": votedSum,
                    "sumWon": sumWon,
                    "pointsName": pointsName,
                    "oldPred": truePrediction["resolvedPred"]
                }
                # forms a dictionary with easier-to-access data than the full thing (reduces work for UI)

            else:
            # no prediction data
                finalPrediction = {
                    "success": False,
                    "error": "No data!"
                }
                # fail dictionary

            self.newPData.emit(finalPrediction)
            # sends the dictionary with success state

        else:
        # if it was not a success
            self.newPData.emit({"success": False, "error": prediction["error"]})
            # sends a dictionary with fail state



### Swap Window ###

    def windowSwap(self, window: str):
        """Function to swap active window"""

        if window == "Starter":
        # calls for starter window to be visible (start -> main -> start)
            self.startWindow.returner()
            # calls the returner function to send back to the start
            self.startWindow.show()
            # shows the starter window
            self.mainWindow.hide()
            # hides the main window
        else:
        # not starter (main -> start -> main)
            self.mainWindow.uiStyle(window)
            # calls the main window with the passed window type
            self.mainWindow.show()
            # shows the main window
            self.startWindow.hide()
            # hides the starter window



### Mod View ###

    def startModView(self):
        """Function to open the mod view"""
        self.taskChange.emit("Mod view is not yet implemented")
        # temp user inform

### Details View ###

    def startDetailView(self):
        """Function to open the prediction details view"""
        self.taskChange.emit("Details view is not yet implemented")
        # temp user inform

        #if self.detailsWindowBool:
        # if the boolean is already set to True
            #self.taskChange.emit("Details view is already active!")
            # user inform
        #else:
        # boolean isn't True (yet)
            #self.detailsWorkerStart()
            #calls the details worker to start
            #self.detailsWindowBool = True
            # sets the boolean to True to prevent a new window start
        
### History View ###

    def startHistoryView(self):
        """Function to open the prediction history view"""
        if self.historyWindowBool:
        # if the boolean is already set to True
            self.historyLifeSignal.emit()
            # runs the lifeCheck function to check the status of the window
            self.taskChange.emit("History window is already active!")
            # user inform
        else:
        # boolean isn't True (yet)
            self.historyWorkerStart()
            # calls the history worker to start
            self.historyWindowBool = True
            # sets the boolean to True to prevent a new window start

### Help View ###

    def startHelpView(self):
        """Function to open the help window"""
        if self.helpWindowBool:
        # if the boolean is already set to True
            self.helpLifeSignal.emit()
            # runs the lifeCheck function to check the status of the window
            self.taskChange.emit("Help window is already active!")
            # user inform

        else:
        # boolean isn't True (yet)
            self.helpWorkerStart()
            # calls the help worker to start
            self.helpWindowBool = True
            # sets the boolean to True to prevent a new window start





### Ditch JavaScript Errors ###

class SilentWebPage(QWebEnginePage):
    """A class to bypass JS errors (that keep spamming console)"""
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Function that catches JS messages/errors"""
        pass
        # does nothing with them





### Window Startup ###

app = QApplication(sys.argv)
"""The application"""
appState = AppState()
"""App state instance to store some variables"""
ctrl = SuperController()
"""The window controller class"""

sys.exit(app.exec())
# starts the application (exits when done)