import os, sys, requests, datetime, json, re
# Required program management
import pandas as pnd
# Soft required for CSV management (not required, but improves formatting)
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



tepgVer = "0.4.19.0442"
"""TEPG program version (Y.MM.DD.HHMM)"""



directory = None
"""The base directory of the program, where TEPG.exe resides"""
iconPath = None
"""The path of the app icon png"""



if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "tepgIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "tepgIcon.png")
    # reassigns the path variables accordingly



profilePath = os.path.join(directory, "Data", "Profile")
"""The user profile path"""
textPath = os.path.join(directory, "Channel List.txt")
"""The list of channels, txt"""
csvPath = os.path.join(directory, "Channel Points.csv")
"""The CSV file path"""
clientIDPath = os.path.join(directory, "Data", "clientID.txt")
"""The Client ID text file path"""
streakMapPath = os.path.join(directory, "Streak List.json")
"""The streak map json file path"""



profileName = None
"""The user profile (folder) name"""
clientID = None
"""The client ID, stored in clientID.txt"""
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
streakMap = {}
"""The map that holds all the streak list information"""
excludedEntries = ["enableErrorsInCSV", "autoAddStreaks", "autoRemoveStreaks", "exampleChannel"]
"""A list of entries that shouldn't count for the streak list"""
overrideChannel = None
"""The single channel name, if using single channel"""
canRun = False
"""Boolean that determines if the main window can start (True after first window completes)"""
activeOnly = False
"""Boolean that determines if the grabbed streaks should be previously active"""
browserOnly = False
"""Boolean that determines if the main window should run in browser-only view"""



reqSession = requests.Session()
"""A request session that stores cached request information"""

os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = f"--user-data-dir={profilePath} --profile-directory={profileName} --enable-widevine --enable-gpu --enable-hls --disable-webgpu"
# environment flags for the chromium webengine (directory stuff, ensures hardware acceleration is on)



def folders(path):
    """Function to check subfolder existence"""
    for folder in os.listdir(path):
        # goes through each folder in the given path
        if os.path.isdir(os.path.join(path, folder)):
            # if the directory is real
            yield os.path.join(path, folder)
            # joins and goes to next





### Starter Window UI ###





class starterWindow(QMainWindow):
    """A class for the first window that pops up"""

    labelSwap = pyqtSignal(str)
    # a pyQt signal to swap the label

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.version = tepgVer
        # stores the version in self

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPG Starter v{self.version}"
        # stores the program name

        self.windowSizeX = max(1000, int(startApp.primaryScreen().size().width() / 3))
        self.windowSizeY = max(600, int(startApp.primaryScreen().size().height() / 3))
        # base window sizes (min of 1000 pixels ~33% of the main monitor's width and height)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size

    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(20)
        # sets spacing of 20px to each

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 50)
        self.mainLayout.setRowMinimumHeight(2, 100)
        self.mainLayout.setRowMinimumHeight(3, 50)
        self.mainLayout.setRowMinimumHeight(4, 50)
        # sets the minimum height for rows

        self.mainLayout.setColumnMinimumWidth(0, 100)
        self.mainLayout.setColumnMinimumWidth(1, 200)
        self.mainLayout.setColumnMinimumWidth(2, 300)
        self.mainLayout.setColumnMinimumWidth(3, 200)
        self.mainLayout.setColumnMinimumWidth(4, 100)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(3, 1)
        self.mainLayout.setColumnStretch(4, 0)
        self.mainLayout.setColumnStretch(2, 1)
        # allows columns 1, 2 and 3 (center) to stretch
        self.mainLayout.setRowStretch(2, 1)
        # allows row 2 (center) to stretch

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("TEPG starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too big
        self.mainLabel.setFixedSize(300, 50)
        # tells the label to prefer the main layout's size
        self.mainLayout.addWidget(self.mainLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label to the main layout (should be top, always)

    ### Hideable/Showable Elements ###

        self.userInputField = QLineEdit()
        # creates a new QLineEdit for user to input into
        self.userInputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # alings to center
        self.userInputField.setFixedSize(300, 30)
        # sets size
        self.mainLayout.addWidget(self.userInputField, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the qline to layout (row 1, col 0)
        self.userInputField.hide()
        # hides by default

    ### Intermediary ###

        self.setCentralWidget(self.container)
        # sets the container to fill the window
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
        self.firstTimeUI()
        # runs the first time UI checker to see if the first time UI should appear or not

### Label Changer ###

    def changeLabel(self, text: str):
        """Function to change the passed label"""
        self.mainLabel.setText(text)
        # sets the passed label's text to the passed text string

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

    ### User Profile Check ###

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
            QTimer.singleShot(1500, self.clientIDCheck)
            # moves straight to client ID check

        elif len(self.subfolders) > 1:
        # if there's more than 1 profile folder
            self.labelSwap.emit("Found multiple folders inside the TEPG/Profile/ folder!\nPlease ensure only one user profile folder is present and retry")
            # sets the text to inform
            return
            # stops the checks

        else:
        # if there's no profile subfolder yet
            self.labelSwap.emit("No profile configured, please enter a new profile name:\nThis is purely cosmetic")
            # swaps the label
            self.userInputField.setPlaceholderText("Default")
            # sets the default text
            self.userInputField.show()
            # unhides the text input element

            self.usernameButton = QPushButton("Submit")
            # makes a new button to save the name
            self.usernameButton.setFixedSize(100, 50)
            # sets size
            self.mainLayout.addWidget(self.usernameButton, 2, 3, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds the button to layout (row 2, col 3)

            self.usernameButton.clicked.connect(self.userNameGrab)
            # on click, calls the next part

### User Profile Name ###

    def userNameGrab(self):
        """Function to grab the user profile folder"""
        global profileName
        # global -> local (set if none exists)
            
        self.chooseUsername = self.userInputField.text()
        # stores the username from the input field
        
        if self.chooseUsername.strip() == "":
        # if user fails to give one
            self.labelSwap.emit("No (valid) name given, setting profile to Default\nTo change this, delete or rename the folder inside /Profile/")
            # user inform
            profileName = "Default"
            # sets to Default
            waitTimer = 4000
            # sets the wait timer to 4000 ms, to allow user to read it
        else:
        # if user provides a name
            self.labelSwap.emit(f"Setting profile name to {self.chooseUsername}")
            # user inform
            profileName = self.chooseUsername
            # stores the profile name as the chosen name
            waitTimer = 2000
            # sets the wait timer to 2000 ms, shorter text with no instructions

        self.usernameButton.deleteLater()
        # deletes the username button
        self.mainLayout.removeWidget(self.usernameButton)
        # removes the button from the layout
        self.userInputField.hide()
        # hides the input field
        self.userInputField.setText("")
        # empties the text

        QTimer.singleShot(waitTimer, self.userNameIntermediary)
        # waits 3s, then calls intermediary function

    def userNameIntermediary(self):
        """Function to slow down the UI (better UX)"""

        self.labelSwap.emit("Getting Client ID...")
        # user inform
        QTimer.singleShot(1500, self.clientIDCheck)
        # calls the next stage

### Client ID Grab ###

    def clientIDCheck(self):
        """Function to grab the client ID"""
        global clientID
        # global -> local

        clientIDFail = False
        # defaults the failure to false

        if os.path.exists(clientIDPath):
        # if the client ID file exists
            try:
            # tries to get the ID
                with open(clientIDPath, "r") as clnt:
                # opens the client id text file
                    clientIDraw = clnt.readline()
                    # reads the line
                    trash, clientID = clientIDraw.split("= ")
                    # splits by "= " presence
                    clientID = clientID.strip()
                    # ensures no whitespace
            except:
            # if it can't get the ID
                clientIDFail = True
                # sets the boolean to True
        else:
        # if the file doesn't exist
            clientIDFail = True
            # sets the boolean to True

        if clientIDFail:
        # if the file doesn't exist or there's an error
            self.labelSwap.emit("No Client ID found!\nPlease enter your Twitch Client ID:")
            # changes the text to inform
            self.userInputField.setPlaceholderText("30-character ID")
            # sets the base text
            self.userInputField.show()
            # unhides the input field

            self.clientIDButton = QPushButton("Submit")
            # makes a new button to save the name
            self.clientIDButton.setFixedSize(60, 35)
            # sets size
            self.mainLayout.addWidget(self.clientIDButton, 2, 3, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds the button to layout (row 2, col 3)

            self.clientIDinvalidText = QLabel("")
            # error text (makes empty by default)
            self.clientIDinvalidText.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )
            # sets alignment to top-center of the slot
            self.clientIDinvalidText.setFixedSize(300, 50)
            # sets a fixed size (helps with spacing)
            self.mainLayout.addWidget(self.clientIDinvalidText, 3, 2, alignment=Qt.AlignmentFlag.AlignTop)
            # adds the widget under the text input field

            self.clientIDButton.clicked.connect(self.clientIDVerify)
            # on click, calls the next part
        else:
        # if the file opens just fine with no error
            self.configWindow()
            # moves to the config window right away

### Client ID "Validation" ###

    def clientIDVerify(self):
        """Function that ensures the client ID is 'valid' (fits regEx criteria)"""
        tempID = self.userInputField.text()
        # stores the ID
        
        if bool(re.fullmatch(r"[A-Za-z0-9]{30}", tempID)):
        # if the ID matches regular expression with length = 30 and normal letters/numbers, it's more than likely valid
            self.clientIDinvalidText.deleteLater()
            # fully deletes the ID invalid text
            self.clientIDSaver()
            # calls the ID saver, because the ID is likely valid
        else:
        # if the ID isn't valid (doesn't match regEx)
            self.clientIDinvalidText.setText("Client ID is not valid, please enter a valid Twitch Client ID")
            # shows the invalid text

### Client ID Save ###

    def clientIDSaver(self):
        """Function that saves the client ID if one is not set yet"""
        global clientID
        # global -> local
            
        clientID = self.userInputField.text()
        # takes the client ID from user input

        with open(clientIDPath, "w") as clnt:
        # opens the client ID location (makes a new file)
            clnt.write(f"Client ID = {clientID}")
            # writes the client ID string to file

        self.clientIDButton.deleteLater()
        # deletes the button
        self.mainLayout.removeWidget(self.clientIDButton)
        # removes the button
        self.userInputField.deleteLater()
        # removes the input field

        self.configWindow()
        # calls the config window next, since all tasks are done for first popup

### Configuration Window

    def configWindow(self):
        """Function to show the configuration window"""
        global streakMap, enableErrorLog, autoAddStreaks, autoRemoveStreaks
        # global -> local

        self.configLayout = QGridLayout()
        # creates a layout just for the config file

        self.mainLayout.addLayout(self.configLayout, 2, 1, 2, 3)
        # adds the config layout to the center of the doc (spans from 2x1 to 3x3)

        if os.path.exists(streakMapPath):
        # if the client ID file exists
            with open(streakMapPath, "r") as strk:
            # opens the client id text file
                streakMap = json.load(strk)
                # loads the json map into variable
            try:
            # tries to get the values
                enableErrorLog = streakMap["enableErrorsInCSV"]
                # gets the boolean for error logging
                autoAddStreaks = streakMap["autoAddStreaks"]
                # gets the boolean for auto-adding streaks
                autoRemoveStreaks = streakMap["autoRemoveStreaks"]
                # gets the boolean for auto-removing streaks
            except:
            # if the value grab fails
                self.labelSwap.emit("Error reading the config file, please re-configure")
                # user inform
                QTimer.singleShot(3000, self.prepConfig)
                # calls the modifyConfig after a couple seconds

            self.labelSwap.emit("Would you like to change your options or keep current configuration?")
            # changes label to prompt next stage

            self.configWindowKeep = QPushButton("Keep")
            self.configWindowModify = QPushButton("Modify")
            # adds buttons to move to next task

            self.configWindowKeep.setFixedSize(100, 50)
            self.configWindowModify.setFixedSize(100, 50)
            # sets sizes

            self.configLayout.addWidget(self.configWindowKeep, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
            self.configLayout.addWidget(self.configWindowModify, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
            # adds the buttons to layout

            self.configWindowKeep.clicked.connect(self.taskChooserConfig)
            # connects the no to move on to task choosing
            self.configWindowModify.clicked.connect(self.prepConfig)
            # connects the yes to move to the modifyConfig

        else:
        # if the file doesn't exist
            self.prepConfig()
            # calls the modifyConfig to set options

### Configuration Selection ###

    def prepConfig(self):
        """Function to prepare for the configuration modification"""
        
        try:
        # tries to remove the buttons (they might not exist, if the streak config file doesn't exist yet)
            self.configWindowKeep.deleteLater()
            self.configWindowModify.deleteLater()
            # removes the buttons
        except:
        # if they don't exist
            None
            # does nothing

        self.labelSwap.emit("Select the options to use, please")
        # changes the main label
        
        self.autoAddStreaksCheckbox = QCheckBox("Automatically add streaks")
        # adds a checkbox for autoAddStreaks
        self.autoRemoveStreaksCheckbox = QCheckBox("Automatically remove streaks")
        # adds a checkbox for autoRemoveStreaks
        self.enableCSVErrorsCheckbox = QCheckBox("Enable error storing in CSV")
        # adds a checkbox for enableErrorLog

        self.autoAddStreakText = QLabel("Automatically add channels into the streak list, if they have an active streak")
        self.autoRemoveStreaksText = QLabel("Automatically remove stale streaks (previously stored, but now 0)")
        self.enableCSVErrorsText = QLabel("Whether to add any point grab errors into CSV")
        # adds tooltips for all 3

        self.autoAddStreaksCheckbox.setChecked(autoAddStreaks)
        self.autoRemoveStreaksCheckbox.setChecked(autoRemoveStreaks)
        self.enableCSVErrorsCheckbox.setChecked(enableErrorLog)
        # sets the check status based on the stored booleans (false by default)

        self.autoAddStreakText.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self.autoRemoveStreaksText.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self.enableCSVErrorsText.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        # centers all 3 text fields to the top of their slots

        self.configLayout.addWidget(self.autoAddStreaksCheckbox, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.autoRemoveStreaksCheckbox, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.configLayout.addWidget(self.enableCSVErrorsCheckbox, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds checkboxes to layout

        self.configLayout.addWidget(self.autoAddStreakText, 2, 0)
        self.configLayout.addWidget(self.autoRemoveStreaksText, 4, 0)
        self.configLayout.addWidget(self.enableCSVErrorsText, 6, 0)
        # adds the text widgets to layout

        self.configLayoutTopSpacer = QSpacerItem(50, 50)
        self.configLayoutBotSpacer = QSpacerItem(50, 50)
        # adds layout spacers

        self.configLayout.addItem(self.configLayoutTopSpacer, 0, 0)
        self.configLayout.addItem(self.configLayoutBotSpacer, 7, 0)
        # adds the spacers to layout

        self.configPrepDoneButton = QPushButton("Done")
        # adds a button to submit the config
        self.configPrepDoneButton.setFixedSize(100, 50)
        # sets size
        self.mainLayout.addWidget(self.configPrepDoneButton, 4, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

        self.configPrepDoneButton.clicked.connect(self.modifyConfigText)
        # done -> modify config

### Modify Configuration ###

    def modifyConfigText(self):
        """Function to just set the text with a delay"""

        self.autoAddStreaksCheckbox.hide()
        self.autoRemoveStreaksCheckbox.hide()
        self.enableCSVErrorsCheckbox.hide()
        # hides the checkboxes
        self.autoAddStreakText.deleteLater()
        self.autoRemoveStreaksText.deleteLater()
        self.enableCSVErrorsText.deleteLater()
        # deletes the texts
        self.mainLayout.removeWidget(self.configPrepDoneButton)
        # removes/hides all the previous widgets from the screen

        self.configPrepDoneButton.deleteLater()
        # deletes the widgets

        self.labelSwap.emit("Modifying configuration...")
        # sets new text
        QTimer.singleShot(1500, self.modifyConfig)
        # calls modifyConfig 2 seconds later
    
    def modifyConfig(self):
        """The function that actually modifies the config"""
        global enableErrorLog, streakMap, autoAddStreaks, autoRemoveStreaks
        # global -> local

        streakMap["autoAddStreaks"] = self.autoAddStreaksCheckbox.isChecked()
        streakMap["autoRemoveStreaks"] = self.autoRemoveStreaksCheckbox.isChecked()
        streakMap["enableErrorsInCSV"] = self.enableCSVErrorsCheckbox.isChecked()
        streakMap["exampleChannel"] = "exampleChannelID"
        # adds map settings

        autoAddStreaks = self.autoAddStreaksCheckbox.isChecked()
        autoRemoveStreaks = self.autoRemoveStreaksCheckbox.isChecked()
        enableErrorLog = self.enableCSVErrorsCheckbox.isChecked()
        # sets the global booleans based on the checkbox values

        self.autoAddStreaksCheckbox.deleteLater()
        self.autoRemoveStreaksCheckbox.deleteLater()
        self.enableCSVErrorsCheckbox.deleteLater()
        # deletes the checkboxes from memory after they've been checked

        with open(streakMapPath, "w") as strk:
        # opens the streak config location (or makes a new file)
            json.dump(streakMap, strk, indent=3)
            # dumps the map into file

        self.labelSwap.emit("Configuration modified...")
        # changes label

        QTimer.singleShot(3000, self.taskChooserConfig)
        # runs the task chooser config

### Task Selection ###

    def taskChooserConfig(self):
        """Function to select which tasks the program should perform"""
        try:
            self.configWindowKeep.deleteLater()
            self.configWindowModify.deleteLater()
            # deletes the elements used in config (keep and modify)
            self.configLayout.deleteLater()
            # deletes the layout used in the config stage
        except Exception as err:
            print(f"uh-oh: {err}")

        self.labelSwap.emit("Please select a task to perform:")
        # swaps main label

        self.taskLayout = QGridLayout()
        # creates a new layout for the tasks to use

        self.mainLayout.addLayout(self.taskLayout, 2, 1, 2, 3)
        # adds the config layout to the center of the doc (spans from 2x1 to 3x3)

        self.pointGrabTask = QPushButton("Channel Points")
        self.streakGrabTask = QPushButton("Channel Streaks")
        self.singleGrabTask = QPushButton("Single Channel")
        self.skipToBrowser = QPushButton("Skip to browser view")
        # adds the buttons to determine task

        self.pointGrabTask.setMinimumSize(250, 40)
        self.streakGrabTask.setMinimumSize(250, 40)
        self.singleGrabTask.setMinimumSize(250, 40)
        self.skipToBrowser.setMinimumSize(250, 40)
        # sets the sizes of the buttons

        self.taskLayout.addWidget(self.pointGrabTask, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.streakGrabTask, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.singleGrabTask, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.skipToBrowser, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the buttons to layout

        try:
        # tries to add the spacers (may already exist)
            self.taskLayoutTopSpacer = QSpacerItem(50, 50)
            self.taskLayoutBotSpacer = QSpacerItem(50, 100)
            # adds a top and bottom spacer
        except:
        # if it can't (they likely already exist)
            None
            # does nothing

        self.taskLayout.addItem(self.taskLayoutTopSpacer, 0, 0)
        self.taskLayout.addItem(self.taskLayoutBotSpacer, 5, 0)
        # adds the spacers to layout (above and below selections, to squish them a bit

        self.pointGrabTask.clicked.connect(lambda: self.taskChooser("Channel Points", 1))
        self.streakGrabTask.clicked.connect(lambda: self.taskChooser("Channel Streaks", 2))
        self.singleGrabTask.clicked.connect(lambda: self.taskChooser("Single Channel", 3))
        self.skipToBrowser.clicked.connect(lambda: self.taskChooser("Skip to Browser", 4))
        # calls the task chooser to further check the task(s)

### Subtask Selection -> Task Run ###

    def taskChooser(self, task: str, taskNum: int):
        """Function to set the tasks to run based on chosen task(s)"""
        global browserOnly
        # global -> local
        try:
        # tries to delete previous elements
            self.pointGrabTask.deleteLater()
            self.streakGrabTask.deleteLater()
            self.singleGrabTask.deleteLater()
            self.skipToBrowser.deleteLater()
            # removes/deletes the previous elements
        except:
        # if the deletion fails (shouldn't, but better than crashing)
            None
            # does nothing

        self.labelSwap.emit(f"Selected {task}...")
        # user inform (may be pretty quick flash)

        self.taskChooseBackButton = QPushButton("Back")
        # back button, in case points was not the intended selection
        self.taskChooseBackButton.setMinimumSize(250, 40)
        # sets minimum size
        self.taskChooseBackButton.clicked.connect(self.returnToConfigChooser)
        # calls the chooser config caller with 1 step (goes back to task selection)

        self.taskPointsAndStreaksButton = QPushButton("All Points and Streaks")
        # pre-creates a button for both streaks and points
        self.taskPointsAndStreaksButton.setMinimumSize(250, 40)
        # sets minimum size
        self.taskPointsAndStreaksButton.clicked.connect(lambda: self.taskRunner(1, 2, None))
        # if the points + streaks button is pressed, calls taskRunner with task 1 subtask 2

        self.taskChooseBackSpacer = QSpacerItem(250, 40)
        # adds a spacer that can be placed between the other buttons and "back"

        self.subtaskLayout = QGridLayout()
        # creates a new layout for the buttons
        self.taskLayout.addLayout(self.subtaskLayout, 2, 0)
        # adds the layout under the top spacer and text field, center (only) column

        if taskNum == 1:
        # task 1 is channel points
            self.labelSwap.emit(f"Select a {task} subtask:")
            # swap label
            
            self.allPointsButton = QPushButton("All Points")
            # all points button
            self.allPointsButton.setMinimumSize(250, 40)
            # sets minimum size

            self.subtaskLayout.addWidget(self.allPointsButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the all points button to layout
            self.subtaskLayout.addWidget(self.taskPointsAndStreaksButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the streaks + points button
            self.subtaskLayout.addItem(self.taskChooseBackSpacer, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the spacer
            self.subtaskLayout.addWidget(self.taskChooseBackButton, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button

            self.allPointsButton.clicked.connect(lambda: self.taskRunner(1, 1, None))
            # all points calls taskRunner with task 1 subtask 1

        elif taskNum == 2:
        # task 2 is streaks
            self.labelSwap.emit(f"Select a {task} subtask:")
            # swap label

            self.allStreaksButton = QPushButton("All Streaks")
            # all streaks button
            self.allStreaksButton.setMinimumSize(250, 40)
            # sets minimum size

            self.activeStreaksButton = QPushButton("Active Streaks")
            # all streaks button
            self.activeStreaksButton.setMinimumSize(250, 40)
            # sets minimum size

            self.subtaskLayout.addWidget(self.allStreaksButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the all streaks button to layout
            self.subtaskLayout.addWidget(self.activeStreaksButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the active streaks button to layout
            self.subtaskLayout.addWidget(self.taskPointsAndStreaksButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the streaks + points button
            self.subtaskLayout.addItem(self.taskChooseBackSpacer, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the spacer
            self.subtaskLayout.addWidget(self.taskChooseBackButton, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button

            self.allStreaksButton.clicked.connect(lambda: self.taskRunner(2, 1, None))
            # all streaks calls taskRunner with task 2 subtask 1
            self.activeStreaksButton.clicked.connect(lambda: self.taskRunner(2, 2, None))
            # active streaks calls taskRunner with task 2 subtask 2

        elif taskNum == 3:
        # task 3 is single channel
            self.labelSwap.emit("Please enter a channel:")
            # swap label

            self.taskSingleSubmitButton = QPushButton("Submit")
            # submit button to enter channel
            self.taskSingleSubmitButton.setMinimumSize(250, 40)
            # sets minimum size

            self.taskSingleChannelName = QLineEdit()
            # a user input field for the channel name
            self.taskSingleChannelName.setPlaceholderText("Channel name")
            # adds a placeholder (background) text
            self.taskSingleChannelName.setMinimumSize(250, 40)
            # sets minimum size
            self.taskSingleChannelName.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # aligns the text to center

            self.subtaskLayout.addWidget(self.taskSingleChannelName, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the channel name input field
            self.subtaskLayout.addWidget(self.taskSingleSubmitButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the submit channel button
            self.subtaskLayout.addItem(self.taskChooseBackSpacer, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button spacer
            self.subtaskLayout.addWidget(self.taskChooseBackButton, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button

            self.taskSingleSubmitButton.clicked.connect(lambda: self.taskRunner(3, 0, self.taskSingleChannelName.text()))
            # runs the task with command 3 and the channel name field's text

        elif taskNum == 4:
        # if it's 4 (skips to browser for login management)
            self.labelSwap.emit("Opening browser view...")
            # user inform
            browserOnly = True
            # sets the global boolean to True (tells the later functions to not run logic)
            QTimer.singleShot(1500, self.taskRunner)
            # calls taskRunner after 1.5s

### Back to Config Chooser ###

    def returnToConfigChooser(self):
        """Function to return back to the config selection screen"""
        try:
        # tries (may "fail")
            while self.subtaskLayout.count():
            # while there's items in the subtask layout
                item = self.subtaskLayout.takeAt(0)
                # grabs the item at position 0
                try:
                # tries to take the widget info (can't if it's an item like spacer)
                    widget = item.widget()
                    # grabs the widget from the item
                    if widget:
                    # if there's a widget set
                        widget.deleteLater()
                        # deletes the widget
                except:
                # if it can't (probably a spacer)
                    self.subtaskLayout.removeItem(item)
                    # removes it instead
            self.subtaskLayout.deleteLater()
            # finally, deletes the whole layout
        except:
        # fail usually just means an item was deleted unexpectedly (which is fine)
            None
            # does nothing
        
        self.taskChooserConfig()
        # calls the task chooser config after

### Task Run ###    

    def taskRunner(self, task:int=None, subtask:int=None, channel:str=None):
        """Function to run the selected task"""
        global overrideChannel, canRun, activeOnly, enableStreaks, enablePoints
        # global -> local
        try:
        # tries (may "fail")
            while self.subtaskLayout.count():
            # while there's items in the subtask layout
                item = self.subtaskLayout.takeAt(0)
                # grabs the item at position 0
                try:
                # tries to take the widget info (can't if it's an item like spacer)
                    widget = item.widget()
                    # grabs the widget from the item
                    if widget:
                    # if there's a widget set
                        widget.deleteLater()
                        # deletes the widget
                except:
                # if it can't (probably a spacer)
                    self.subtaskLayout.removeItem(item)
                    # removes it instead
            self.subtaskLayout.deleteLater()
            # finally, deletes the whole layout
        except:
        # fail usually just means an item was deleted unexpectedly (which is fine)
            None
            # does nothing
        
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

        elif task == 3:
        # task 3 is single channel
            overrideChannel = channel.strip()
            # sets the override channel global variable to match the passed channel name

        else:
        # anything not 1-3 (just 4 or a mistake) falls here
            None
            # doesn't change anything

        self.labelSwap.emit("Starting the main TEPG program...\nThis window will close and a new one will open...")
        # swaps the label once more

        canRun = True
        # sets the "permission slip" for the next stage to True (allows next window)

        QTimer.singleShot(3000, self.stopper)
        # quits the starter application window with a small delay

### Stopper ###

    def stopper(self):
        """Function to call when a stop is needed (with a delay)"""
        self.close()
        # just closes the window





### Starter Startup ###

startApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
startWindow = starterWindow()
# creates a window
startApp.exec()
# exceutes the app task (runs the QApplication)





### Main App Window ###





class tepgWindow(QMainWindow):
    """The application window class"""

    authValid = pyqtSignal(bool)
    # creates a bool signal to check if the authentication code is ready
    taskText = pyqtSignal(str)
    # creates a string signal to set the task view to
    browserShow = pyqtSignal(bool)
    # creates a bool signal to check if the browser window should be shown, or a smaller preloader

    def __init__(self, state):
        super().__init__()

    ### Init / Basic ###

        self.state = state
        # stores the app state that holds variables
        self.version = tepgVer
        # stores the version in self

        self.profilePath = profilePath
        # stores the profile path
        self.profileName = profileName
        # stores the profile name

        self.csvPath = csvPath
        # stores the csv file path
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
        self.programName = f"Twitch Exact Point Grabber v{self.version}"
        # stores the program name
        self.pid = os.getpid()
        # gets the current process' ID

        self.browserView = QWebEngineView(self)
        # adds a new webengine view

        self.windowSizeX = int(app.primaryScreen().size().width() / 1.5)
        self.windowSizeY = int(app.primaryScreen().size().height() / 1.5)
        # base window sizes (~66% of the main monitor's width and height)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size 

    ### Main Window Layout ###

        self.mainLayout = QGridLayout()
        # creates a layout
        self.mainLayout.setSpacing(15)
        # sets spacing
        self.container = QWidget()
        # makes a container 
        self.container.setLayout(self.mainLayout)
        # sets the container to use the layout
        self.setCentralWidget(self.container)
        # sets the container to the middle

    ### Tooltip / Task View ###

        self.taskView = QLabel()
        # creates a line edit text field for the task progress
        self.taskView.setText("Opening browser view...")
        # initial value
        self.taskView.setFixedSize(QSize(int(self.windowSizeX / 4), 25))
        # sets a fixed size (1/4th the window width, 25 px tall)
        self.taskView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to the center
        self.mainLayout.addWidget(self.taskView, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

    ### Browser ###

        self.browserProfile = QWebEngineProfile(self.profileName, self)
        # sets the browser profile to the given profile (default is Default)
        self.browserProfile.setCachePath(os.path.join(self.profilePath, self.profileName))
        # sets the cache path (<drive>:/<installation>/Data/Profile/<profileName>/)
        self.browserPage = QWebEnginePage(self.browserProfile, self.browserView)
        # creates the engine page with the profile and view parameters
        self.browserView.setPage(self.browserPage)
        # sets the page to use the given properties
        self.browserView.setFixedSize(self.windowSizeX - 20, self.windowSizeY - 45)
        # caps the browser to be half the window size

        self.settings = self.browserProfile.settings()
        # manages the browser settings
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        # ensures local storage is enabled 
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        # ensures plugins are allowed to function
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # ensures javascript is enabled

        self.mainLayout.addWidget(self.browserView, 1, 0, 1, 1)
        # adds the browser to the layout
        self.browserView.setUrl(QUrl(self.defaultURL))
        # sets "default" url to open (twitch.tv)

        if not browserOnly:
        # if the browser-only mode isn't enabled
            self.browserView.loadFinished.connect(self.extractAuthToken)
            # calls the auth grab when the page is done loading
        else:
        # if the browser-only mode *is* enabled
            self.browserWindow(False)
            # calls the browser window with False (forces full window size and shows it)
        self.browserShow.connect(self.browserWindow)
        # calls browserWindow when the status is determined
        self.authValid.connect(self.pwpgd)
        # calls the delay function when the authvalid is set to True
        self.taskText.connect(self.manageTooltip)
        # calls manageTooltip when the task text changes

### Browser Window UI ###

    def browserWindow(self, status: bool):
        """A function to determine if the browser view should appear or not"""
        if status and not browserOnly:
        # if the status is True (meaning the auth token is all good and the browser isn't needed)
            self.browserView.hide()
            # hides the whole browser view
            self.setMinimumSize(500, 300)
            self.resize(500, 300)
            # the window size
        else:
        # if the status is False (auth token not valid, need to log in or something)
            self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
            # resizes the window to "normal" size
            self.browserView.show()
            # shows the browser view
            self.forceBrowserUI = True
            # sets the boolean to True, so the browser doesn't go away

        try:
        # tries to show window (just in case it gets mad it's already visible)
            self.show()
            # shows the window (regardless of status)
        except:
        # if it can't show the window (probably already open)
            None
            # does nothing

### Pre-Window -> Point Grabber Delay ###

    def pwpgd(self, ok: bool):
        """A small function to slow down the UI swap"""
        QTimer.singleShot(2000, self.uiStyle)
        # waits 2 seconds, then calls the UIstyle update

### Headless UI ###

    def headless(self):
        """A function to add the headless UI layout requirements"""
        self.leftSpacer = QSpacerItem(100, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.rightSpacer = QSpacerItem(100, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.topSpacer = QSpacerItem(10, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.bottomSpacer = QSpacerItem(10, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # adds a ton of spacers to keep the progress bar and label in the center (ideally)

        self.progressBar = QProgressBar()
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
        self.progressBar.setFixedSize(QSize(300, 25))
        # sets the progress bar's size, so that the spacers don't do weird stuff

        self.channelLabel = QLabel()
        # adds a label for the channel's info text
        if enablePoints and not enableStreaks:
        # if the point grabbing is enabled, streaks disabled
            self.channelLabel.setText("Starting point grabber...")
            # sets initial text
        elif not enablePoints and enableStreaks:
        # if the point grabbing is disabled, streaks enabled
            self.channelLabel.setText("Starting streak grabber...")
            # sets initial text
        else:
        # something else?
            self.channelLabel.setText("Starting grabber...")
            # sets initial text
        self.channelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.channelLabel.setFixedSize(QSize(300, 30))
        # sets fixed size
        self.channelLabel.setWordWrap(True)
        # allows the text to wrap, if it's too long

        self.totalLabel = QLabel()
        # total label (total found points)
        self.totalLabel.setText("Nothing found yet")
        # sets initial text
        self.totalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.currentLabel = QLabel()
        self.currentLabel.setText(f"0 / {self.channelLength}")
        # sets initial progress
        self.currentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.mainLayout.addItem(self.leftSpacer, 1, 0)
        self.mainLayout.addItem(self.rightSpacer, 1, 2)
        self.mainLayout.addItem(self.topSpacer, 0, 1)
        self.mainLayout.addItem(self.bottomSpacer, 5, 1)
        self.mainLayout.addWidget(self.progressBar, 1, 1)
        self.mainLayout.addWidget(self.channelLabel, 2, 1)
        self.mainLayout.addWidget(self.totalLabel, 3, 1)
        self.mainLayout.addWidget(self.currentLabel, 4, 1)
        # adds all the items to the layout

    def manageTooltip(self, tooltip: str):
        """A function to manage the text above the browser view before it goes away"""
        self.taskView.setText(tooltip)
        # sets the text to the passed string

    def handleProgress(self, progressDict: dict):
        """A function to manage the progress bar and channel name"""

        dictType = progressDict["type"]
        # the type of dictionary sent (full or single)

        if dictType == "full":
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
            expiryDate = progressDict["expiresAt"]
            # grabs all the relevant information from the passed dictionary

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
                else:
                # if the streak is 0
                    streakString = f"no active streak"
                    # forms a none-streak string

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
                        if expiryDate == "nah":
                        # if the expiry date is set to "nah" (not expiring)
                            self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}")
                            # sets the text to match
                        else:
                        # if there's an expiry date
                            self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nStreak expiring at {expiryDate}!")
                            # sets warning
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
                    if streak == 0:
                    # if the streak is 0
                        self.channelLabel.setText(f"{channel} has no active streak!")
                        # no streak text
                    elif streak < 100 and (str(streak).startswith("8") or streak == 18 or streak == 11):
                    # if streak is <100, and one of: the first number of streak is an 8 (eighty-X or just 8) or it's 11 or 18
                        if expiryDate == "nah":
                        # no expiry date
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!")
                            # sets the text to match (it has "an" as prefix, not "a")
                        else:
                        # if there's a date
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!\nStreak expires at {expiryDate}!")
                            # sets the text to match (it has "an" as prefix, not "a")
                    else:
                        if expiryDate == "nah":
                        # no expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!")
                            # sets the text to match
                        else:
                        # yes expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!\nStreak expires at {expiryDate}!")
                            # sets text with streak warning

            self.currentLabel.setText(f"{(index + 1)} / {self.channelLength}")
            # sets the current channel index string
        
        else:
        # if the dictionary is a single channel
            channel = progressDict["channel"]
            # the channel name (str)
            points = progressDict["points"]
            # point count (int)
            error = progressDict["error"]
            # boolean for whether an error occurred
            streak = progressDict["streak"]
            # the current channel's streak
            # grabs all the relevant information from the passed dictionary

            pointString = f"{points:,} points"
            # formats the number to use formatting (no decimals, thousand comma)

            if error:
            # if there's an error reported
                self.channelLabel.setText(f"Error with {channel}, couldn't get points")
                # sets an error text
            else:
            # no error ->
                self.channelLabel.setText(f"{pointString} and a streak of {streak} found for {channel}")
                # sets the text to match

            self.progressBar.setValue(100)
            # sets the progress bar value

    def progressDone(self, errors: int, streak: int, expiryList: list=None):
        """A function to change the headless UI into completion mode"""
        preFinalText = self.totalLabel.text()
        # gets the text from the label
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
            expiryString = f"Channels with expiring streaks: {", ".join(expiryList)}"
            # turns the list into a string

        if errors > 0:
        # if there was at least one error
            finalString = (
                        f"All channels scoured - stats have been saved to CSV!\n\n"
                        f"TEPG was unable to store points for {errors} out of {len(self.channels)} channels\n\n"
                        f"{expiryString}\n\n"
                        f"Feel free to exit, thank you for using TEPG <3\n"
                        )
            # forms final string with error count
        else:
        # if there were no errors
            finalString = (
                        f"All channels scoured - stats have been saved to CSV!\n\n"
                        f"{expiryString}\n\n"
                        f"Feel free to exit, thank you for using TEPG <3\n"
                        )
            # forms final string with no errors
        self.channelLabel.setText(finalString)
        # final UI update with the formed string
        self.currentLabel.hide()
        # hides the index number

### Window Size Manager ###

    def sizeCalculator(self, X: int = None, Y: int = None) -> None:
        """A function to calculate the window sizes based on monitor or resize"""
        if X and X > 500:
        # if X is set and is >500 pixels
            self.windowSizeX = X
            # uses the given X size as the window size
        else:
        # if X isn't given or is very small
            self.windowSizeX = int(app.primaryScreen().size().width() / 1.5)

        if Y and Y > 350:
        # if Y is set and is >350 pixels
            self.windowSizeY = Y
            # uses the given Y size as the window size
        else:
        # if Y isn't given or is very small
            self.windowSizeY = int(app.primaryScreen().size().height() / 1.5)
            # base window sizes (~66% of the main monitor's width and height)

### UI Style Picker ###

    def uiStyle(self):
        """Function to change the UI when called for"""

        self.taskView.hide()
        # hides the task viewer
        self.browserView.hide()
        # hides the browser view
        self.headless()
        # adds the headless UI widgets to layout
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers everything to middle
        self.setMinimumSize(500, 300)
        self.resize(500, 300)
        # the window size

        QTimer.singleShot(3000, self.startPointWorker)
        # calls the point manager to start getting points

### Auth Token Grabber ###

    def extractAuthToken(self, ok: bool):
        """Function to get the auth token from storage"""

        if not self.forceBrowserUI:
        # if the force browser boolean isn't true (only true if already ran once)
            self.browserShow.emit(True)
            # tells the browser to hide, but show the UI

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

        storedCookies.cookieAdded.connect(cookieParser)
        # when a cookie gets added, calls the cookieParser
        storedCookies.loadAllCookies()
        # starts loading the cookies in local storage

        QTimer.singleShot(5000, self.authValidCheck)
        # waits 5 seconds, then calls the valid checker

### Auth Validity Check ###

    def authValidCheck(self):
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
                self.taskText.emit("Auth token successfully validated, starting headless TEPG...")
                # user update
                self.authValid.emit(True)
                # sets the pyqt signal to true
            else:
            # if the result is False (failure)
                raise Exception
                # forces an error
        except:
        # if the channel check fails
            self.taskText.emit("Token could not be validated, ensure you're logged in to Twitch")
            # changes UI text to error
            self.browserShow.emit(False)
            # tells browserShow to show the window

### Channel Lister ###

    def getChannelList(self) -> list:
        """The function to grab the list of channels"""
        self.channels = []
        # clears the list

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

        return self.channels
        # returns the list of channels to caller

### Worker Starter ###

    def startPointWorker(self):
    # a starter for the point worker

        self.thread = QThread()
        # creates a new thread
        self.worker = PointWorker(self.state, self.channels, self.csvPath)
        # creates a worker with the state, channel list and csv path

        self.worker.moveToThread(self.thread)
        # moves the worker to its own thread

        self.thread.started.connect(self.worker.run)
        # thread start connects to worker run

        self.worker.progress.connect(self.handleProgress)
        # connects the worker progress to handleProgress (when there's a progress update -> updates headless UI)
        self.worker.finished.connect(self.progressDone)
        # connects to the progressDone function (when everything is done -> final UI update -> quit)

        self.thread.start()
        # starts thread



### Point Grabber ###

def pointGrabber(state, channel: str) -> dict:
    """The function that grabs the channel points via GraphQL"""
    global clientID, reqSession

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": f"{clientID}",
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type
    
    payload = {
    # forms a payload from the required information
        "operationName": "ChannelPointsContext",
        "variables": {
            "channelLogin": channel
            # which channel to "login" to
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": "7fe050e3761eb2cf258d70ee1a21cbd76fa8cf3d7e7b12fc437e7029d446b5e3",
                "version": 1
                # this hash is found in devTools console, (search for balance -> GQL with "ChannelPointsContext" operation)
            }
        }
    }

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json

    try:
    # tries to read the received data file
        if data and data["data"]:
        # checks if the data package is valid and that there's a header for "data"
            points = data["data"]["community"]["channel"]["self"]["communityPoints"]
            # stores the location of the points in the data json
            try:
                return {"success": True, "error": "None", "points": points["balance"]}
                # returns a dictionary with success

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "No data rece"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure


### Streak Grabber ###

def streakGrabber(state, channel: str, channelID:int = None) -> dict:
    """The function that grabs streak information"""
    global clientID, reqSession

    rURL = "https://gql.twitch.tv/gql"
    # the endpoint to make requests to

    authToken = state.authToken
    # gets the authorisation token from the app state variable

    headers = {
            "Client-Id": f"{clientID}",
            "Authorization": f"OAuth {authToken}",
    }
    # forms the headers used to dictate the data request type
    
    if channelID == None:
    # if no channelID is passed
        idPayload = {
        # forms a payload just for the ID
            "operationName": "ChannelPollContext_GetViewablePoll",
            # this was the first operation I found that has a return for the ID without requesting with the ID
            "variables": {
                "login": channel,
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": "e83188a3836c636393df3191665e543a03733d7c51d3ade3d85e42aa46c2bf55",
                    # the hash for the operation, may change
                    "version": 1
                }
            }
        }

        idRequest = reqSession.post(rURL, json = idPayload, headers = headers)
        # makes request to get the 
        idData = idRequest.json()
        # stores the resulting data json

        try:
        # attempts to access the returned json
            if idData and idData["data"]:
            # if there's a return package and the package has "data"
                channelID = idData["data"]["channel"]["id"]
                # grabs the channel ID from the returned data package
            else:
                return {"success": False, "error": "ChannelID not found"}
                # returns failure dict
        except:
        # if it can't access/fails at 
            return {"success": False, "error": "ChannelID failure"}
            # returns a failure dict

    channelID = str(channelID)
    # stringifies the channelID
    
    if channelID != None:
    # if the channelID is now not None
        payload = {
        # forms a payload from the required information
            "operationName": "RewardList",
            "variables": {
                "channelID": channelID
                # which channel to "login" to
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": "0b1471876d7647993731b9e3c6a13bf304c67fb31d07f06a945d42286ee377c4",
                    "version": 1
                    # this hash is found in devTools console, (search for watch streak -> GQL with "RewardList" operation)
                }
            }
        }

        request = reqSession.post(rURL, json = payload, headers = headers)
        # forms a data request
        data = request.json()
        # stores the resulting data json

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





### Authorisation Token "Storage" ###



class AppState:
    """A class to store the authorisation token"""
    def __init__(self):
        self.authToken = None
        # simply stores the auth token here, so that both the main window and the point worker classes can call the point/streak grabbers with the same token





### Channel/Point Manager ###





class PointWorker(QObject):
    # signals to communicate with UI
    progress = pyqtSignal(dict)
    # stores the percentage, channel name and points inside a pyqt singal, to update UI
    finished = pyqtSignal(int, int, list)
    # gets set when done

    def __init__(self, state, channels, csvPath):
        super().__init__()
        self.state = state
        # stores the appstate (gets pushed to pointGrabber, has token)
        self.channels = channels
        # stores channels passed
        self.csvPath = csvPath
        # stores the csv path
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
                    else:
                    # if the point entry success is False (something went wrong)
                        foundPoints = 0
                        # stores 0
                        errorBool = True
                        # sets the error bool to true (will tell the UI to display error text)
                        self.errorCount = (self.errorCount + 1)
                        # on error, adds an error to counter

                    self.totalPoints = (self.totalPoints + foundPoints)
                    # adds the channel's points to the total amount
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
                        # sleeps for a second (avoids limiting)

                    if activeOnly:
                    # if the boolean for the "active streaks only" is true, won't check *all* channels
                        if channel in streakMap:
                        # if the channel is in the streak map
                            streak = streakGrabber(self.state, channel, int(streakMap[channel]))
                            # calls the streak grabber with the channel ID (doesn't need to make a second request in this case)
                        else:
                        # if the channel *isn't* in the map
                            streak = {"success": False, "error": "No active streak stored"}
                            # forms a custom dictionary to pass to csv
                    else:
                    # if the boolean isn't active only, goes through all
                        if channel in streakMap:
                        # if the channel is in the streak map
                            streak = streakGrabber(self.state, channel, int(streakMap[channel]))
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
                            self.expiringList.append({channel: streak.get("expires", "Soon")})
                            # adds the expiring channel's expiry date to a list to display at the end
                        else:
                        # if there's no date (not expiring)
                            expiring = False
                            # sets the flag to False so it doesn't get set

                        if streakNum > 1 and channel not in streakMap and autoAddStreaks:
                        # if there's a streak present and the channel isn't stored yet, plus the config option to add them to the streak map is on
                            streakMap[channel] = int(streak["channelID"])
                            # stores the channel with its ID
                        elif streakNum == 0 and channel in streakMap and autoRemoveStreaks:
                        # if there's no streak, the channel is in the map and the option to remove stales is on
                            streakMap.pop(channel, None)
                            # removes the entry for that channel
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
                        "streak": streakNum
                    }
                    # stores the points and streak in the channel's csv entry

                if expiring:
                # if there's an expiration date
                    self.progressDict = {
                        "type": "full",
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
                        "type": "full",
                        "channel": channel,
                        "index": num,
                        "pointsOn": enablePoints,
                        "points": foundPoints,
                        "error": errorBool,
                        "total": self.totalPoints,
                        "streaksOn": enableStreaks,
                        "streak": streakNum,
                        "expiresAt": "nah"
                    }
                    # forms a progress dictionary to pass

                self.progress.emit(self.progressDict)
                # sends a progress update to the headless UI updater

                QThread.msleep(1500)
                # waits 1.5s/channel

            with open(streakMapPath, "w") as strk:
            # opens the streak config location
                json.dump(streakMap, strk, indent=3)
                # dumps the map into file
            
            self.csvWriter(csvEntries, self.errorCount, self.maxStreak, self.expiringList)
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
            else:
            # if the point entry success is False (something went wrong)
                foundPoints = 0
                # stores 0
                errorBool = True
                # sets the error bool to true (will tell the UI to display error text)
                self.errorCount = (self.errorCount + 1)
                # on error, adds an error to counter

            self.totalPoints = foundPoints
            # total is the channel's total

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

            csvEntries[channel] = {
                "points": foundPoints,
                "streak": streakNum,
                "error": errorBool,
                "reason": f"{points["error"]}, {streak["error"]}"
            }
            # forms the csvEntry for the channel

            self.progressDict = {
                "type": "single",
                "channel": channel,
                "index": num,
                "pointsOn": enablePoints,
                "points": foundPoints,
                "error": errorBool,
                "total": self.totalPoints,
                "streaksOn": enableStreaks,
                "streak": 0 
            }
            # forms a progress dictionary to pass

            self.progress.emit(self.progressDict)
            # sends a progress update to the headless UI updater

    ### CSV Writer ###

    def csvWriter(self, csvEntries: dict, errors: int, maxStreak: int, expiryList: list=None):
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

        dataframe.to_csv(self.csvPath, index=False)
        # pushes everything to the csv file

        if not expiryList:
        # if the expiry list isn't defined (not passed)
            expiryList = []
            # makes an empty list

        self.finished.emit(errors, maxStreak, expiryList)
        # once done, sends a signal to the finished pyqt signal with the error count, highest streak and expiration list
            




### Main Window Startup ###



if canRun:
# if the permission slip is signed, runs the main window
    app = QApplication(sys.argv)
    # base app instance (passes command line arguments)
    appState = AppState()
    # creates an app state instance to store some variables
    window = tepgWindow(appState)
    # creates a window
    app.exec()
    # exceutes the app task (runs the QApplication)