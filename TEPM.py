import os, sys, requests, datetime, json, re, threading, time, subprocess, queue
# Required program management
import pandas as pnd
# Soft required for CSV management (not required, but improves formatting)
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



tepmVer = "0.5.8.2320"
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
hashFilePath = os.path.join(directory, "Data", "hashes.json")
"""The hash container file"""
detailWindowPath = os.path.join(directory, "Data", "TEPMpd.exe")
"""The prediction detail window executable path"""
detailWindowDir = os.path.join(directory, "Data")
"""The prediction detail directory to pass (inside Data)"""



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
hashMap = {}
"""The map that holds all the hashes and related information"""
excludedEntries = ["enableErrorsInCSV", "autoAddStreaks", "autoRemoveStreaks", "exampleChannel"]
"""A list of entries that shouldn't count for the streak list"""
overrideChannel = None
"""The single channel name, if using single channel"""
predictChannel = None
"""The channel to predict on, if using"""
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



class starterWindow(QWidget):
    """A class for the first window that pops up"""

    labelSwap = pyqtSignal(str)
    # a pyQt signal to swap the label
    ready = pyqtSignal()
    # a pyQt signal to indicate readiness state

    def __init__(self):
        super().__init__()



    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.version = tepmVer
        # stores the version in self

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM Starter v{self.version}"
        # stores the program name

        self.windowSizeX = max(900, int(app.primaryScreen().size().width() / 3))
        self.windowSizeY = max(600, int(app.primaryScreen().size().height() / 3))
        # base window sizes (min between 900 pixels and ~33% of the main monitor's width and height)

        self.optionReturn = False
        # boolean to store whether user has visited options or not (changes visuals)



    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size



    ### UI Elements ###

        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(0)
        # removes spacing

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 100)
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
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 1)
        self.mainLayout.setColumnStretch(4, 0)
        # allows columns 1, 2 and 3 (center) to stretch
        self.mainLayout.setRowStretch(2, 1)
        # allows row 2 (center) to stretch

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("TEPM starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(False)
        # makes the text wrap if it's too big
        self.mainLabel.setMaximumSize(300, 100)
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

        self.setLayout(self.mainLayout)
        # sets the container to fill the window
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
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
            self.labelSwap.emit("Found multiple folders inside the TEPM/Profile/ folder!\nPlease ensure only one user profile folder is present and retry")
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
                    if clientID == "":
                    # if the clientID is empty after stripping (not set)
                        clientIDFail = True
                        # sets the fail to True
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
            self.hashLoader()
            # moves to the hash loader right away



### Client ID "Validation" ###

    def clientIDVerify(self):
        """Function that ensures the client ID is 'valid' (fits regEx criteria)"""
        tempID = self.userInputField.text()
        # stores the ID
        
        if bool(re.fullmatch(r"[A-Za-z0-9]{30}", tempID)):
        # if the ID matches regular expression with length = 30 and normal letters/numbers, it's more than likely valid
            self.clientIDinvalidText.deleteLater()
            # fully deletes the ID invalid text field
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

        self.hashLoader()
        # calls the hashloader to grab the GQL hashes



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
                    self.configWindow()
                    # calls the config window to proceed
            except:
            # if it can't load it properly
                self.labelSwap.emit("Could not open the hash file, please ensure it's valid.\nTry downloading a new one from GitHub")
                # user inform
                QTimer.singleShot(2500, self.stopper)
                # calls the stop function after a couple seconds
        else:
        # if the hash file doesn't exist
            self.labelSwap.emit("No hashes.json file found, please download a new one from GitHub.")
            # user inform
            QTimer.singleShot(2500, self.stopper)
            # calls the stop function after a couple seconds



### Configuration Window ###

    def configWindow(self):
        """Function to show the configuration window"""
        global streakMap, enableErrorLog, autoAddStreaks, autoRemoveStreaks
        # global -> local

        self.configLayout = QGridLayout()
        # creates a layout just for the config file

        self.mainLayout.addLayout(self.configLayout, 2, 1, 2, 3)
        # adds the config layout to the center of the doc (spans from 2x1 to 3x3)

        self.labelSwap.emit("Reading config...")
        # user inform

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
                self.taskChooserConfig()
                # calls the next stage
            except:
            # if the value grab fails
                self.labelSwap.emit("Error reading the config file, please re-configure")
                # user inform
                QTimer.singleShot(3000, self.prepConfig)
                # calls the modifyConfig after a couple seconds

        else:
        # if the file doesn't exist
            self.prepConfig()
            # calls the modifyConfig to set options



### Configuration Selection ###

    def prepConfig(self):
        """Function to prepare for the configuration modification"""

        self.labelSwap.emit("Select the options to use, please")
        # changes the main label
        
        self.autoAddStreaksCheckbox = QCheckBox("Auto-add streaks")
        # adds a checkbox for autoAddStreaks
        self.autoRemoveStreaksCheckbox = QCheckBox("Auto-remove streaks")
        # adds a checkbox for autoRemoveStreaks
        self.enableCSVErrorsCheckbox = QCheckBox("Store errors")
        # adds a checkbox for enableErrorLog

        self.autoAddStreakText = QLabel("Automatically add active streaks to list")
        self.autoAddStreakText.setToolTip("Active streak means any streak higher than 1")
        self.autoRemoveStreaksText = QLabel("Automatically remove stale streaks")
        self.autoRemoveStreaksText.setToolTip("Removes streaks that have been broken (0 streak)")
        self.enableCSVErrorsText = QLabel("Whether to add any point grab errors into CSV")
        self.enableCSVErrorsText.setToolTip("Add any potential error reasons into the CSV with data")
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

        if self.optionReturn:
        # if user returns from options screen
            self.modifyConfig()
            # calls it immediately
        else:
        # if it's the first time
            self.optionReturn = True
            # sets the boolean to True so it gets caught
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
        
        if self.optionReturn:
        # if the boolean is true
            self.taskChooserConfig()
            # calls the task chooser immediately
        else:
            QTimer.singleShot(3000, self.taskChooserConfig)
            # runs the task chooser config



### Task Selection ###

    def taskChooserConfig(self):
        """Function to select which tasks the program should perform"""

        self.labelSwap.emit("Please select a task to perform:")
        # swaps main label

        self.taskLayout = QGridLayout()
        # creates a new layout for the tasks to use
        self.taskLayout.setColumnMinimumWidth(0, 300)
        # forces the column 0 to stay at 300px (no movement)
        self.taskLayout.setVerticalSpacing(25)
        # sets spacing between buttons

        self.mainLayout.addLayout(self.taskLayout, 2, 1, 2, 3)
        # adds the config layout to the center of the doc (spans from 2x1 to 3x3)

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
        self.skipToBrowser.setToolTip("Bypass processing and enter the browser\nThis is only really needed for debug")
        # tooltips

        self.pointGrabTask.setMinimumSize(250, 40)
        self.streakGrabTask.setMinimumSize(250, 40)
        self.singleGrabTask.setMinimumSize(250, 40)
        self.predictionTask.setMinimumSize(250, 40)
        self.skipToBrowser.setMinimumSize(250, 40)
        # sets the sizes of the buttons

        self.taskLayout.addWidget(self.pointGrabTask, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.streakGrabTask, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.singleGrabTask, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.predictionTask, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.taskLayout.addWidget(self.skipToBrowser, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the buttons to layout

        self.optionsButton = QPushButton("Options")
        # adds options button
        self.optionsButton.setToolTip("Open the options/config view")
        # tooltip
        self.optionsButton.setMaximumSize(75, 40)
        # sets size
        self.optionsButton.clicked.connect(self.options)
        # connects the options button to the options function

        self.mainLayout.addWidget(self.optionsButton, 4, 4, alignment=Qt.AlignmentFlag.AlignRight)
        # adds the button to the right bottom corner

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
        self.taskLayout.addItem(self.taskLayoutBotSpacer, 6, 0)
        # adds the spacers to layout (above and below selections, to squish them a bit

        self.pointGrabTask.clicked.connect(lambda: self.taskChooser("Channel Points", 1))
        self.streakGrabTask.clicked.connect(lambda: self.taskChooser("Channel Streaks", 2))
        self.singleGrabTask.clicked.connect(lambda: self.taskChooser("Single Channel", 3))
        self.predictionTask.clicked.connect(lambda: self.taskChooser("Prediction", 4))
        self.skipToBrowser.clicked.connect(lambda: self.taskChooser("Skip to Browser", 5))
        # calls the task chooser to further check the task(s)



### Options Screen ###

    def options(self):
        """Function that enters the options screen"""

        try:
        # tries to delete previous elements
            self.optionsButton.deleteLater()
            self.pointGrabTask.deleteLater()
            self.streakGrabTask.deleteLater()
            self.singleGrabTask.deleteLater()
            self.predictionTask.deleteLater()
            self.skipToBrowser.deleteLater()
            # removes/deletes the previous elements
        except:
        # if the deletion fails (shouldn't, but better than crashing)
            None
            # does nothing

        self.prepConfig()
        # calls prepConfig to open that screen



### Subtask Selection -> Task Run ###

    def taskChooser(self, task: str, taskNum: int):
        """Function to set the tasks to run based on chosen task(s)"""
        global browserOnly
        # global -> local
        try:
        # tries to delete previous elements
            self.optionsButton.deleteLater()
            self.pointGrabTask.deleteLater()
            self.streakGrabTask.deleteLater()
            self.singleGrabTask.deleteLater()
            self.predictionTask.deleteLater()
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
        self.taskChooseBackButton.setToolTip("Go back to selection menu")
        # tooltip
        self.taskChooseBackButton.setMinimumSize(250, 40)
        # sets minimum size
        self.taskChooseBackButton.clicked.connect(self.returnToConfigChooser)
        # calls the chooser config caller with 1 step (goes back to task selection)

        self.taskPointsAndStreaksButton = QPushButton("All Points and Streaks")
        # pre-creates a button for both streaks and points
        self.taskPointsAndStreaksButton.setToolTip("Get both channel points and streaks\nof the channels in the channel list file")
        # tooltip
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

        self.taskSingleChannelName = QLineEdit()
        # a user input field for the channel name
        self.taskSingleChannelName.setPlaceholderText("Channel name")
        # adds a placeholder (background) text
        self.taskSingleChannelName.setToolTip("Write a channel to perform task on")
        # tooltip
        self.taskSingleChannelName.setMinimumSize(250, 40)
        # sets minimum size
        self.taskSingleChannelName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns the text to center

        self.taskSingleSubmitButton = QPushButton("Submit")
        # submit button to enter channel
        self.taskSingleSubmitButton.setToolTip("Confirm selection")
        # tooltip
        self.taskSingleSubmitButton.setMinimumSize(250, 40)
        # sets minimum size

        if taskNum == 1:
        # task 1 is channel points
            self.labelSwap.emit(f"Select a {task} subtask:")
            # swap label
            
            self.allPointsButton = QPushButton("All Points")
            # all points button
            self.allPointsButton.setToolTip("Get all channel points for channels in the channel list file")
            # tooltip
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
            self.allStreaksButton.setToolTip("Get all streaks for channels in the channel list file")
            # tooltip
            self.allStreaksButton.setMinimumSize(250, 40)
            # sets minimum size

            self.activeStreaksButton = QPushButton("Active Streaks")
            # all streaks button
            self.activeStreaksButton.setToolTip("Get streaks marked as active (>1) from the channel points file")
            # tooltip
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

            self.subtaskLayout.addWidget(self.taskSingleChannelName, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the channel name input field
            self.subtaskLayout.addWidget(self.taskSingleSubmitButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the submit channel button
            self.subtaskLayout.addItem(self.taskChooseBackSpacer, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button spacer
            self.subtaskLayout.addWidget(self.taskChooseBackButton, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button

            self.taskSingleSubmitButton.clicked.connect(lambda: self.taskRunner(3, 0, self.taskSingleChannelName.text().strip()))
            # runs the task with command 3 and the channel name field's text

        elif taskNum == 4:
        # if it's 4 (prediction manager)
            self.labelSwap.emit("Please enter a channel:")
            # user inform

            self.subtaskLayout.addWidget(self.taskSingleChannelName, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the channel name input field
            self.subtaskLayout.addWidget(self.taskSingleSubmitButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the submit channel button
            self.subtaskLayout.addItem(self.taskChooseBackSpacer, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the spacer
            self.subtaskLayout.addWidget(self.taskChooseBackButton, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the back button

            self.taskSingleSubmitButton.clicked.connect(lambda: self.taskRunner(4, 0, self.taskSingleChannelName.text().strip()))
            # runs the task with command 4 and the channel name field's text

        elif taskNum == 5:
        # if it's 5 (skips to browser for login management)
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
        global overrideChannel, canRun, activeOnly, enableStreaks, enablePoints, predictChannel
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
            if overrideChannel == "" or not overrideChannel:
            # if none is set
                self.labelSwap.emit("No channel set! Please set one first")
                # user inform
                QTimer.singleShot(1250, self.taskChooser("Single Channel", 3))
                # re-runs the same window command

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

        else:
        # anything not 1-4 falls here
            None
            # doesn't change anything

        self.labelSwap.emit(f"Starting the main TEPM program...\n\nThis window will close and a new one will open...{bonusString}")
        # swaps the label once more

        if canRun:
        # if the canRun is already set to True (returning from main)
            QTimer.singleShot(750, self.stopper)
            # shorter delay
        else:
        # if it's not True yet (program start)
            canRun = True
            # signs the "permission slip" for main window
            QTimer.singleShot(2000, self.stopper)
            # quits the starter application window with a small delay

        



### Stopper ###

    def stopper(self):
        """Function to call when a stop is needed (with a delay)"""
        self.hide()
        # just closes the window]
        self.ready.emit()
        # sends a signal to the pyQt signal to let the main window know it's ready
        mainWindow.show()
        # opens the main window


### Main App Window ###



class tepmWindow(QWidget):
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
        self.version = tepmVer
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
        self.programName = f"Twitch External Point Manager v{self.version}"
        # stores the program name
        self.pid = os.getpid()
        # gets the current process' ID

        self.browserView = QWebEngineView(self)
        # adds a new webengine view

        self.predictChannelPoints = 0
        """Variable to store the predict channel's point balance"""
        self.displayWindowBool = False
        """Whether the details window should be alive"""
        self.modWindowBool = False
        """Whether the mod window should be alive"""
        self.previousEventState = None
        """Variable to store the previous event info"""
        self.doneLoading = False
        """Boolean to check if browser is done loading"""



    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(800, 900))
        # the window size



    ### Main Window Layout ###

        self.mainLayout = QGridLayout()
        # creates a layout
        self.mainLayout.setSpacing(25)
        # sets spacing between elements (vertical and horizontal)
        self.setLayout(self.mainLayout)
        # sets the layout



    ### Task View Grid ###

        self.taskGrid = QGridLayout()
        # a layout for the tasks to fit into
        self.mainLayout.addLayout(self.taskGrid, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the grid to the top middle



    ### Tooltip / Task View ###

        self.taskView = QLabel()
        # creates a line edit text field for the task progress
        self.taskView.setText("Opening browser view...")
        # initial value
        self.taskView.setToolTip("Current operation")
        # tooltip
        self.taskView.setFixedSize(QSize(350, 40))
        # sets a fixed size to prevent being cut off
        self.taskView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to the center
        self.taskGrid.addWidget(self.taskView, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout



    ### Retry Token Button ###

        self.refreshTokenButton = QPushButton("Refresh Token")
        # a button to try to refresh the token
        self.refreshTokenButton.setFixedSize(125, 25)
        # sets a size
        self.refreshTokenButton.setToolTip("Press to re-validate token")
        # tooltip
        self.taskGrid.addWidget(self.refreshTokenButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the right side of the taskView
        self.refreshTokenButton.hide()
        # hides it by default



    ### Browser ###

        self.browserProfile = QWebEngineProfile(self.profileName, self)
        # sets the browser profile to the given profile (default is Default)
        self.browserProfile.setCachePath(os.path.join(self.profilePath, self.profileName))
        # sets the cache path (<drive>:/<installation>/Data/Profile/<profileName>/)
        self.browserPage = QWebEnginePage(self.browserProfile, self.browserView)
        # creates the engine page with the profile and view parameters
        self.browserView.setPage(self.browserPage)
        # sets the page to use the given properties
        self.browserView.setFixedSize(780, 450)
        # caps the browser size

        self.settings = self.browserProfile.settings()
        # manages the browser settings
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        # ensures local storage is enabled 
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        # ensures plugins are allowed to function
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # ensures javascript is enabled

        self.mainLayout.addWidget(self.browserView, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the browser to the layout
        self.browserView.setUrl(QUrl(self.defaultURL))
        # sets "default" url to open (twitch.tv)

        if not browserOnly:
        # if the browser-only mode isn't enabled
            startWindow.ready.connect(self.extractAuthToken)
            # calls the auth grab when the page is done loading
        else:
        # if the browser-only mode *is* enabled
            self.browserWindow(False)
            # calls the browser window with False (forces full window size and shows it)

        self.browserPage.loadFinished.connect(lambda: setattr(self, "doneLoading", True))
        # once the browser is done loading, sets the boolean to true, allowing progress later on
        self.browserShow.connect(self.browserWindow)
        # calls browserWindow when the status is determined
        self.authValid.connect(self.pwpgd)
        # calls the delay function when the authvalid is set to True
        self.taskText.connect(self.manageTooltip)
        # calls manageTooltip when the task text changes
        self.refreshTokenButton.clicked.connect(self.authValidCheck)
        # calls the auth valid function when pressing the refresh button
        


    ### Predict UI ###

        self.predictLayout = QGridLayout()
        """A layout for the predictions"""
        self.mainLayout.addLayout(self.predictLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout

        self.predictionID = {}
        """Map to enter the prediction ID information into"""


    ### Predict Details ###

        self.predictInfoLayout = QGridLayout()
        """Anested layout that hosts basic information about the prediction(s)"""
        self.predictInfoLayout.setSpacing(35)
        # adds a little more spacing
        self.predictLayout.addLayout(self.predictInfoLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # top middle

        self.predictDetailLayout = QGridLayout()
        """A further nested layout that hosts prediction specifics (status, name, creation, pool, outcome, task)"""
        self.predictDetailLayout.setVerticalSpacing(25)
        # adds a little more vertical space
        self.predictInfoLayout.addLayout(self.predictDetailLayout, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # under the basic info, above the buttons

        self.predictChannelLabel = QLabel()
        """A label that holds the current channel name"""
        self.predictChannelLabel.setToolTip("Currently selected channel")
        # tooltip
        self.predictChannelLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 24px;
            }
        """)
        self.predictInfoLayout.addWidget(self.predictChannelLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the layout (top middle)

        self.predictPointLabel = QLabel()
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
        self.predictPointLabel.hide()
        # hides by default


        self.predictStatusLabel = QLabel()
        """A label that holds the prediction status (active, locked, paid out, refunded)"""
        self.predictStatusLabel.setToolTip("Prediction status")
        # tooltip
        self.predictStatusLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
            }
        """)
        # style sheet
        self.predictStatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.predictInfoLabel = QLabel()
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

        self.predictDetailLabel = QLabel()
        """A label that holds the prediction details (creator, timestamp)"""
        self.predictDetailLabel.setToolTip("Prediction details")
        # tooltip
        self.predictDetailLabel.setStyleSheet("""
            QLabel {
                font-style: italic;
                font-size: 12px;
            }
        """)
        # style sheet
        self.predictDetailLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.predictDetailLabel.hide()
        # hides by default

        self.predictTimerLabel = QLabel("00:00")
        """A label that holds the prediction timer (if active)"""
        self.predictTimerLabel.setToolTip("Prediction timer")
        # tooltip
        self.predictTimerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.predictTimerLabel.hide()
        # hides by default
        

        self.predictPoolLabel = QLabel()
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
        self.predictPoolLabel.hide()
        # hides by default

        self.predictResultLabel = QLabel("Winner!")
        """A label that holds the result (if resolved)"""
        self.predictResultLabel.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-style: italic;
                font-size: 15px;
            }
        """)
        # style sheet
        self.predictResultLabel.setToolTip("Prediction Outcome")
        # tooltip
        self.predictResultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.predictResultLabel.hide()
        # hides by default

        self.predictTaskLabel = QLabel("Current Task")
        """A label that holds the current task op"""
        self.predictTaskLabel.setStyleSheet("""
            QLabel {
                color: yellow;
                font-style: italic;
                font-size: 13px;
            }
        """)
        self.predictTaskLabel.setToolTip("Program status inform")
        # tooltip
        self.predictTaskLabel.setMinimumSize(300, 50)
        # min size
        self.predictTaskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.predictTaskLabel.hide()
        # hides by default

        self.predictInfoLayout.addWidget(self.predictPointLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the 1st nested layout (middle middle)
        self.predictInfoLayout.addWidget(self.predictTaskLabel, 3, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds task label between the prediction details layout and the outcome layout (details and buttons)

        self.predictDetailLayout.addWidget(self.predictStatusLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds status label to the 2nd nested layout (under the points)
        self.predictDetailLayout.addWidget(self.predictInfoLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds basic info label to the 2nd nested layout (under the status)
        self.predictDetailLayout.addWidget(self.predictDetailLabel, 2, 0, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop))
        # adds details label to the 2nd nested layout (under the prediction name)
        self.predictDetailLayout.addWidget(self.predictTimerLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds timer label to the 2nd nested layout (under the details)
        self.predictDetailLayout.addWidget(self.predictPoolLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds pool label to the 2nd nested layout (under the timer)
        self.predictDetailLayout.addWidget(self.predictResultLabel, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds result label to the 2nd nested layout (under the pool)




    ### Predict Button/Point Layout ###

        self.predictOutcomeLayout = QGridLayout()
        """A nested layout that hosts the bet selectors and point totals"""
        self.predictOutcomeLayout.setVerticalSpacing(15)
        # sets lower spacing
        self.predictInfoLayout.addLayout(self.predictOutcomeLayout, 4, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the info layout (under the labels)



    ### Predict Outcome Selections ###

        self.predictOption1 = QPushButton()
        self.predictOption1.setCheckable(True)
        self.predictOption1.setMinimumSize(90, 40)
        self.predictOption1.setToolTip("Outcome 1")
        # option 1

        self.predictOption2 = QPushButton()
        self.predictOption2.setCheckable(True)
        self.predictOption2.setMinimumSize(90, 40)
        self.predictOption2.setToolTip("Outcome 2")
        # option 2

        self.predictOption3 = QPushButton()
        self.predictOption3.setCheckable(True)
        self.predictOption3.setMinimumSize(90, 40)
        self.predictOption3.setToolTip("Outcome 3")
        # option 3

        self.predictOption4 = QPushButton()
        self.predictOption4.setCheckable(True)
        self.predictOption4.setMinimumSize(90, 40)
        self.predictOption4.setToolTip("Outcome 4")
        # option 4

        self.predictOption5 = QPushButton()
        self.predictOption5.setCheckable(True)
        self.predictOption5.setMinimumSize(90, 40)
        self.predictOption5.setToolTip("Outcome 5")
        # option 5

        self.predictOutcomeLayout.addWidget(self.predictOption1, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictOption2, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictOption3, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictOption4, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictOption5, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

        self.predictOption1.hide()
        self.predictOption2.hide()
        self.predictOption3.hide()
        self.predictOption4.hide()
        self.predictOption5.hide()
        # hides options by default

        self.predictOptions = [self.predictOption1, self.predictOption2, self.predictOption3, self.predictOption4, self.predictOption5]
        # list of predict option buttons

        self.predictOption1.clicked.connect(lambda: self.predictButtonManager(1, "Init"))
        self.predictOption2.clicked.connect(lambda: self.predictButtonManager(2, "Init"))
        self.predictOption3.clicked.connect(lambda: self.predictButtonManager(3, "Init"))
        self.predictOption4.clicked.connect(lambda: self.predictButtonManager(4, "Init"))
        self.predictOption5.clicked.connect(lambda: self.predictButtonManager(5, "Init"))
        # connects the buttons to the manager with their ints



    ### Predict Outcome Labels ###

        self.predictPoints1 = QLabel("0")
        self.predictPoints1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints1.setToolTip("Prediction outcome details")
        # label 1
        self.predictPoints2 = QLabel("0")
        self.predictPoints2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints2.setToolTip("Prediction outcome details")
        # label 2
        self.predictPoints3 = QLabel("0")
        self.predictPoints3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints3.setToolTip("Prediction outcome details")
        # label 3
        self.predictPoints4 = QLabel("0")
        self.predictPoints4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints4.setToolTip("Prediction outcome details")
        # label 4
        self.predictPoints5 = QLabel("0")
        self.predictPoints5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPoints5.setToolTip("Prediction outcome details")
        # label 5
        
        self.predictOutcomeLayout.addWidget(self.predictPoints1, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictPoints2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictPoints3, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictPoints4, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictOutcomeLayout.addWidget(self.predictPoints5, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

        self.predictPoints1.hide()
        self.predictPoints2.hide()
        self.predictPoints3.hide()
        self.predictPoints4.hide()
        self.predictPoints5.hide()
        # hides points by default

        self.predictPoints = [self.predictPoints1, self.predictPoints2, self.predictPoints3, self.predictPoints4, self.predictPoints5]
        # list of predict point labels

    

    ### Predict Actions ###

        self.predictSuperLayout = QGridLayout()
        """Layout that holds prediction elements (mod/details)"""
        self.predictLayout.addLayout(self.predictSuperLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout under the info/details layout

        self.predictBetLayout = QGridLayout()
        """Layout that holds the betting elements (amount + bet buttons)"""
        self.predictSuperLayout.addLayout(self.predictBetLayout, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds into the super layout in the middle (col 1)

        self.predictBetSpacer = QSpacerItem(200, 35)
        """Spacer that pushes the bet buttons down"""

        self.predictAmountLine = QLineEdit()
        """Way to customise the bet amount (int entry)"""
        self.predictAmountLine.setToolTip("How many channel points to bet")
        # tooltip
        self.predictAmountLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to the center
        self.predictAmountLine.setPlaceholderText("Bet Amount (max: 250,000)")
        # sets background text
        self.predictAmountLine.setInputMask("000000")
        # sets an input mask to only accept 6 digits (max bet of 250000), automatically caps at 250k
        self.predictAmountLine.setMinimumSize(200, 40)
        # min size
        self.predictAmountLine.textChanged.connect(self.betMasker)
        # connects writing to this to the bet masking function

        self.predictBetButton = QPushButton("Bet")
        """Confirm bet button"""
        self.predictBetButton.setToolTip("Confirm bet amount")
        # tooltip
        self.predictBetButton.setMinimumSize(50, 40)
        # min size

        self.maxBetButton = QPushButton("Max")
        """Button to bet max amount"""
        self.maxBetButton.setToolTip("Set max bet (requires confirmation)")
        # tooltip
        self.maxBetButton.setMinimumSize(50, 40)
        # min size

        self.modButton = QPushButton("Mod View")
        """Button to open mod view"""
        self.modButton.setToolTip("Open moderator view tab")
        # tooltip
        self.modButton.setMinimumSize(60, 40)
        # min size

        self.detailsButton = QPushButton("Details")
        """Button to display further information about the bet"""
        self.detailsButton.setToolTip("Display more information about the prediction")
        # tooltip
        self.detailsButton.setMinimumSize(60, 40)
        # min size
        self.detailsButton.hide()
        # hides by default

        self.predictSuperLayout.addItem(self.predictBetSpacer, 0, 1)
        self.predictBetLayout.addWidget(self.predictAmountLine, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictBetLayout.addWidget(self.maxBetButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictBetLayout.addWidget(self.predictBetButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictSuperLayout.addWidget(self.modButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictSuperLayout.addWidget(self.detailsButton, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # the bet line and buttons go below the details

        self.predictBetButton.clicked.connect(lambda: self.predictUI("Bet"))
        # connects the bet button to the ui bet
        self.maxBetButton.clicked.connect(lambda: self.betMasker("Max"))
        # connects the max bet button to the bet masking function
        self.modButton.clicked.connect(self.modCheck)
        # connects the mod button to the mod check
        self.detailsButton.clicked.connect(self.predictionWinStart)
        # connects the detail button to the ui window
        
        self.predictAmountLine.hide()
        self.predictBetButton.hide()
        self.modButton.hide()
        self.maxBetButton.hide()
        # hides all elements by default



    ### Channel Swap ###

        self.predictChannelLayout = QGridLayout()
        """Layout that holds the channel swapping elements"""
        self.predictLayout.addLayout(self.predictChannelLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout under the bet layout

        self.predictChannelLine = QLineEdit()
        """Change the channel (text entry)"""
        self.predictChannelLine.setToolTip("Enter another streamer here and press Change to move to their stream")
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
        self.predictChannelSwapButton.setMinimumSize(50, 40)
        # min size

        self.predictChannelLayout.addWidget(self.predictChannelLine, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.predictChannelLayout.addWidget(self.predictChannelSwapButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout (under the bets)

        self.predictChannelSwapButton.clicked.connect(lambda: self.predictUI("Swap"))
        # connects the swap button to the ui swap 

        self.predictChannelLine.hide()
        self.predictChannelSwapButton.hide()
        # hides elements by default



    ### Exit UI ###

        self.stopLayout = QGridLayout()
        # a layout for the end buttons 
        self.stopLayout.setSpacing(30)
        # 30 px gaps
        self.mainLayout.addLayout(self.stopLayout, 5, 0)
        # adds the layout at the very bottom location
        
        self.menuButton = QPushButton("Menu")
        # button to return to the menu
        self.menuButton.setToolTip("Return to the main menu\nCloses this window to reopen the starter")
        # tooltip
        self.menuButton.setMinimumSize(125, 50)
        # size
        self.menuButton.hide()
        # hides by default

        self.exitButton = QPushButton("Exit")
        # button to quit
        self.exitButton.setToolTip("Quit the application")
        # tooltip
        self.exitButton.setMinimumSize(125, 50)
        # size
        self.exitButton.hide()
        # hides by default

        self.stopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.stopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds all the items to the layout

        self.menuButton.clicked.connect(lambda: self.backToTheLobby("Menu"))
        # connects to the menu
        self.exitButton.clicked.connect(self.backToTheLobby)
        # connects to the exit function



    ### Prediction Element Lists ###

        self.activePredictionElements = [self.predictTimerLabel]
        # a list of elements exclusive to the active prediction style
        self.lockedPredictionElements = []
        # a list of elements exclusive to the locked prediction style
        self.resolvedPredictionElements = [self.predictResultLabel]
        # a list of elements exclusive to the resolved prediction style



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
            self.setMinimumSize(QSize(750, 450))
            # resizes the window to "normal" size
            self.browserView.show()
            # shows the browser view
            self.forceBrowserUI = True
            # sets the boolean to True, so the browser doesn't go away



### Pre-Window -> Point Grabber Delay ###



    def pwpgd(self, ok: bool):
        """A small function to slow down the UI swap"""
        QTimer.singleShot(2000, self.uiStyle)
        # waits 2 seconds, then calls the UIstyle update



### Headless UI ###



    def headless(self):
        """A function to add the headless UI layout requirements"""
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
        self.progressBar.hide()
        # hides the progress bar by default

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
        elif predictChannel:
        # if there's a predict channel set
            self.channelLabel.setText("Starting prediction manager...")
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

        if predictChannel:
        # if a predict channel is set
            self.totalLabel.hide()
            self.currentLabel.hide()
            # hides both labels (unused)

        self.mainLayout.addItem(self.topSpacer, 0, 1)
        self.mainLayout.addItem(self.bottomSpacer, 5, 1)
        self.mainLayout.addWidget(self.progressBar, 1, 1)
        self.mainLayout.addWidget(self.channelLabel, 2, 1)
        self.mainLayout.addWidget(self.totalLabel, 3, 1)
        self.mainLayout.addWidget(self.currentLabel, 4, 1)
        # adds all the items to the layout



### Tooltip ###



    def manageTooltip(self, tooltip: str):
        """A function to manage the text above the browser view before it goes away"""
        self.taskView.setText(tooltip)
        # sets the text to the passed string



### Progress Handler ###



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
                            else:
                            # 7 > streak > 3
                                streakPoints = (streak - 3) * 350
                                # calculates the amount over 3
                                streakPoints += 1050
                                # adds the first 3 days worth
                        elif streak == 7:
                        # streak is exactly 7
                            streakPoints == (1050 + 2250)
                            # adds up the points earned in the first 7 days (1050 + (5 * 450))
                        else:
                        # 10 > streak > 7
                            streakPoints = ((streak - 7) * 450)
                            # calculates the amount over 7
                            streakPoints += (1050 + 2250)
                            # adds the first 7 days worth
                    elif streak == 10:
                    # if the streak is exactly 10
                        streakPoints = (1050 + 2250 + 1800)
                        # adds up the points earned from first 10 days
                    else:
                    # streak is > 10
                        streakPoints = (1050 + 2250 + 1800)
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
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nThis streak is worth {streakPoints} points")
                                # sets the text to match
                            else:
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}")
                        else:
                        # if there's an expiry date
                            if streak > 0:
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}\nThis streak is worth {streakPoints} points\nStreak expiring at {expiryDate}!")
                                # sets warning
                            else:
                                self.channelLabel.setText(f"{pointString}{midString} {streakString} found for {channel}")
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
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!\nThis streak is worth {streakPoints} points!\n{streakVerbose}")
                            # sets the text to match (it has "an" as prefix, not "a")
                        else:
                        # if there's a date
                            self.channelLabel.setText(f"{channel} has an {streak} day streak!\nThis streak is worth {streakPoints} points!\n{streakVerbose}\nStreak expires at {expiryDate}!")
                            # sets the text to match (it has "an" as prefix, not "a")
                    else:
                        if not expiryDate:
                        # no expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!\nThis streak is worth {streakPoints} points!\n{streakVerbose}")
                            # sets the text to match
                        else:
                        # yes expiry date
                            self.channelLabel.setText(f"{channel} has a {streak} day streak!\nThis streak is worth {streakPoints} points!\n{streakVerbose}\nStreak expires at {expiryDate}!")
                            # sets text with streak warning

            self.currentLabel.setText(f"{(index + 1)} / {self.channelLength}")
            # sets the current channel index string
        
        elif dictType == "single":
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

        elif dictType == "predict":
        # if the dictionary is about predictions
            self.channelLabel.setText("")
            # sets the text to match



### Progress Done ###



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
        # if it's passed and isn't empty
            for x in range (len(expiryList)):
            # goes through all the elements
                if not expiryList[x]:
                # if the value is False
                    expiryList.pop(x)
                    # deletes it
                
            expiryString = f"Channels with expiring streaks: {", ".join(expiryList)}"
            # turns the list into a string

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
        self.channelLabel.setText(finalString)
        # final UI update with the formed string
        self.currentLabel.deleteLater()
        # deletes the index label
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
            startWindow.show()
            # shows the starter window
            mainWindow.hide()
            # hides the main window
        else:
            app.exit()
            # closes the app



### UI Style Picker ###



    def uiStyle(self):
        """Function to change the UI when called for"""

        self.taskView.hide()
        # hides the task viewer
        self.refreshTokenButton.hide()
        # hides the refresh button
        self.browserView.hide()
        # hides the browser view

        if predictChannel:
        # if the prediction channel is set

            self.setMinimumSize(850, 800)
            self.resize(850, 800)
            # the window size

            self.predictUI("Init")
            # initialises the predict UI

        else:
        # if the prediction channel isn't set
            self.headless()
            # adds the headless UI widgets to layout

            self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # centers everything to middle
            self.setMinimumSize(500, 300)
            self.resize(500, 300)
            # the window size

            QTimer.singleShot(3000, self.startPointWorker)
            # calls the point manager to start getting points



### Prediction UI ###



    def predictUI(self, action:str = None):
        """Function that handles prediction UI changes"""
        global predictChannel
        # global -> local

        selectedOption = None
        # defaults selected option as none

        totalPoints = 0
        # starts total point counter at 0

        if action == "Init":
        # init action
            self.predictAmountLine.show()
            self.predictBetButton.show()
            self.predictChannelLine.show()
            self.predictChannelSwapButton.show()
            self.maxBetButton.show()
            self.modButton.show()
            self.detailsButton.show()
            self.predictChannelLabel.show()
            self.predictPointLabel.show()
            self.predictInfoLabel.show()
            self.predictDetailLabel.show()
            self.predictPoolLabel.show()
            self.predictStatusLabel.show()
            self.predictTaskLabel.show()
            # enables all the buttons

            channelPoints = pointGrabber(self.state, predictChannel)
            # grabs the channel points 

            if channelPoints["success"]:
            # if the return is a success
                self.predictChannelPoints = int(channelPoints["points"])
                # stores the channel's points in the self variable
                self.predictTaskLabel.setText("Found points!")
                # user inform status
                predictChannel = channelPoints["caseName"]
                # grabs the caSe sEnsItiVE name at the same time, replaces global var 
                self.predictChannelLabel.setText(predictChannel)
                # sets the text of the channel label to match channel
                self.predictChannelLabel.show()
                # enables the label
                self.predictPointLabel.setText(f"Balance: {self.predictChannelPoints:,.0f} points")
                # update the point counter
                self.predictPointLabel.show()
                # enables the point balance label

                self.eop()
                # end of program, enables menu button and exit

                # predictionThread.start()
                # starts the predict refresh thread loop

            else:
            # if the return isn't a success
                self.predictTaskLabel.setText(f"Couldn't get points!\nCheck the streamer's status and try again")
                # user inform
                self.predictChannelLabel.setText(predictChannel)
                # sets the label to match the name
                self.predictChannelLabel.show()
                # enables the label


        elif action == "Bet":
        # if the action is to bet
            for option in self.predictOptions:
            # goes through list of options
                if option.isChecked():
                # if the button is selected
                    selectedOption = option
                    # sets that button as selected

            bet = int(self.predictChannelLine.text().strip())
            # grabs the bet integer from the current bet line

            if not selectedOption or not bet:
            # if either option is not set
                self.predictTaskLabel.setText("Bet not set or outcome not selected, please try again!")
                # sets error text

            else:
            # if both are set successfully
                try:
                    eventID = self.predictionID["eventID"]
                    # grabs the event ID from the map
                    outcomeID = self.predictionID[selectedOption]
                    # grabs the outcome ID linked to that option
                except:
                    outcomeID = None
                    # sets to none

                if not outcomeID == None:
                # if outcomeID is defined (didn't fail, was set correctly)

                    betInfo = sendPredict(self.state, bet, eventID, outcomeID)
                    # calls the prediction sender with the state, the bet amount and the prediction details

                    if betInfo["success"]:
                    # if the return is a success
                        self.predictChannelLine.setText("")
                        # clears the predict channel text
                        self.predictTaskLabel.setText(f"Successfully bet {bet} on {selectedOption}!\nMay the odds be ever in your favor!")
                        # sets info text
                    
                    else:
                    # if the return isn't a success
                        err = betInfo["error"]
                        # grabs the error message from the return
                        self.predictTaskLabel.setText(f"Failed to send bet! Error: {err}")
                        # updates user on error
                else:
                # if it wasn't defined (either didn't get set properly or failed to grab)
                    self.predictTaskLabel.setText(f"Failed to send bet due to internal error!")
                    # user inform
            
        elif action == "Swap":
        # if user pressed swap button
            newChannel = self.predictChannelLine.text().strip()
            # temp var for channel
            if not newChannel or newChannel == "":
            # if the channel is empty
                self.predictTaskLabel.setText("No streamer set, please enter one to change streams")
                # user inform
            else:
                predictChannel = newChannel
                # grabs the name of the channel from the line, changes global var to match

                channelPoints = pointGrabber(self.state, predictChannel)
                # grabs the channel points 

                if channelPoints["success"]:
                # if the return is a success
                    self.predictChannelPoints = int(channelPoints["points"])
                    # stores the channel's points in the self variable
                    self.predictTaskLabel.setText("Found points!")
                    # user inform status
                    self.predictChannelLabel.setText(predictChannel)
                    # sets the text of the channel label to match channel
                    self.predictChannelLabel.show()
                    # enables the label
                    self.predictPointLabel.setText(f"Balance: {self.predictChannelPoints} points")
                    # update the point counter
                else:
                # if the return isn't a success
                    self.predictTaskLabel.setText(f"Couldn't get points!\nCheck the streamer's status and try again")
                    # user inform
                    self.predictChannelLabel.setText(predictChannel)
                    # sets the label to match the name
                    
                    self.predictPointLabel.hide()
                    # hides the balance button


        predictionDict = predictGrabber(self.state, predictChannel)
        # calls the predict grabber and stores the return

        for x in self.predictOptions:
        # goes through all the prediction option buttons
            try:
                x.hide()
                # tries to hide it
            except:
                None
                # does nothing if it can't (already hidden)
        for x in self.predictPoints:
        # goes through all the point labels
            try:
                x.hide()
                # tries to hide 
            except:
                None
                # does nothing if it can't (already hidden)

        if predictionDict["success"]:
        # if it was a success
            activePrediction = predictionDict["active"]
            # stores the active prediction
            lockedPrediction = predictionDict["locked"]
            # stores the locked prediction
            resolvedPredictions = predictionDict["resolved"]
            # stores the resolved prediction
            self.predictTaskLabel.setText("Found prediction!")
            # sets task text to match

            if action == "Refresh":
                print("refresh")

            if len(activePrediction) > 0:
            # if the active predict list has more than 0 elements
                truePrediction = activePrediction[0]
                # grabs the 0th element from the list (now a dictionary)
                truePrediction["type"] = "active"
                # sets the type to active
                eventID = truePrediction["id"]
                # grabs the event ID from the prediction dictionary

                self.predictionID = {}
                # clears the map on success
                self.predictionID["eventID"] = eventID
                # sets the event ID in the map

            elif len(lockedPrediction) > 0:
            # if the locked predict list has more than 0 elements
                truePrediction = lockedPrediction[0]
                # grabs the 0th element from the list (now a dictionary)
                truePrediction["type"] = "locked"
                # sets the type to locked
 
            elif len(resolvedPredictions) > 0:
            # if the resolved (passed) predict list has more than 0 elements

                truePrediction = resolvedPredictions[0]["node"]
                # grabs the 0th element from the list (now a dictionary), grabs the node (information)
                truePrediction["type"] = "resolved"
                # sets the type to resolved

            title = truePrediction["title"]
            # grabs the prediction title
            outcomes = truePrediction["outcomes"]
            # grabs the list of outcomes
            creator = truePrediction["createdBy"]["displayName"]
            # grabs the creator name

            if truePrediction["type"] == "active":
            # if the prediction is active
                rawTimestamp = truePrediction["createdAt"]
                # grabs the raw creation timestamp (YYYY-MM-DDTHH:MM:SS.*ms*Z)
            elif truePrediction["type"] == "locked":
            # if the prediction is locked
                rawTimestamp = truePrediction["lockedAt"]
                # grabs the lock timestamp
            else:
            # if it's resolved
                rawTimestamp = truePrediction["endedAt"]
                # grabs the end stamp

            timestampUTC = datetime.datetime.fromisoformat(rawTimestamp.replace("Z", "+00:00"))
            # formats it to datetime 
            timestampLocal = timestampUTC.astimezone()
            # swaps to current timezone
            predictionStamp = timestampLocal.strftime("%B %d at %I:%M %p").replace(" 0", " ")
            # finalizes it into eg. "April 21 at 11:06 AM" (the example I had)

            for x in range (len(outcomes)):
            # goes through each option
                optionName = outcomes[x]["title"]
                # gets the name of the option
                optionID = outcomes[x]["id"]
                # gets the outcome ID 
                optionPoints = outcomes[x]["totalPoints"]
                # gets the points given to the option
                totalUsers = outcomes[x]["totalUsers"]
                # gets the users that went in on the option

                optionX = self.predictOptions[x]
                # grabs the xth option
                optionX.show()
                # enables the option
                optionX.setText(optionName)
                # sets the option name to match
                if truePrediction["type"] == "active":
                # if the prediction is active
                    optionX.setEnabled(True)
                    # enables the button
                else:
                # if not (locked/resolved)
                    optionX.setEnabled(False)
                    # disables the button

                optionString = f"{optionPoints:,.0f} points\n{totalUsers:,.0f} users"
                # forms a string 

                pointsX = self.predictPoints[x]
                # grabs the xth option
                pointsX.show()
                # enables the label
                pointsX.setText(optionString)
                # sets the label to match

                self.predictionID[optionX] = optionID
                # stores a reference to the outcome ID (named option because there's already an outcomeID var)  by linking it to the buttons
                
                totalPoints += int(optionPoints)
                # adds the points to the total

            totalPoints = f"{totalPoints:,.0f}"
            # formats the string into comma-split form

            if truePrediction["type"] == "active":
            # if the prediction is active
                self.maxBetButton.setEnabled(True)
                self.predictBetButton.setEnabled(True)
                self.predictAmountLine.setEnabled(True)
                # enables the bet-related options
                self.predictStatusLabel.setText("Open Prediction:")
                self.predictInfoLabel.setText(f"{title}")
                self.predictDetailLabel.setText(f"Created by {creator}, started at {predictionStamp}")
                self.predictStatusLabel.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        font-size: 16px;
                        color: green;
                    }
                """)
                # sets the text green
                self.predictPoolLabel.setText(f"Total pool: {totalPoints} points")
                # changes text to indicate status

                self.predictElementHider("Active")
                # calls the element hider to hide locked/resolved UI elements and show active

            else:
            # prediction isn't active (locked/resolved)
                self.maxBetButton.setEnabled(False)
                self.predictBetButton.setEnabled(False)
                self.predictAmountLine.setEnabled(False)
                # disables the bet-related options

                if truePrediction["type"] == "locked":
                # if the prediction is locked
                    self.predictStatusLabel.setText("Closed Prediction:")
                    self.predictInfoLabel.setText(f"{title}")
                    self.predictDetailLabel.setText(f"Created by {creator}, locked at {predictionStamp}")
                    self.predictStatusLabel.setStyleSheet("""
                        QLabel {
                            font-weight: bold;
                            font-size: 16px;
                            color: orange;
                        }
                    """)
                    # sets the text orange
                    self.predictPoolLabel.setText(f"Total pool: {totalPoints} points")
                    # changes text to indicate status

                    self.predictElementHider("Locked")
                    # calls the element hider to hide active/resolved UI elements and show locked

                else:
                # prediction is resolved (paid out)
                    self.predictStatusLabel.setText("Paid Out Prediction:")
                    self.predictInfoLabel.setText(f"{title}")
                    self.predictDetailLabel.setText(f"Created by {creator}, ended at {predictionStamp}")
                    self.predictStatusLabel.setStyleSheet("""
                        QLabel {
                            font-weight: bold;
                            font-size: 16px;
                            color: orange;
                        }
                    """)
                    # sets the text orange
                    self.predictPoolLabel.setText(f"Total pool: {totalPoints} points")
                    # changes text to indicate status

                    winOutcomeDict = truePrediction.get("winningOutcome", {"id":"refund", "title":"one of them"})
                    # gets the winning outcome dictionary, otherwise uses set dictionary
                    winOutcomeID = winOutcomeDict["id"]
                    # grabs the winning ID
                    winOutcomeTitle = winOutcomeDict["title"]
                    # grabs the winning title

                    print(winOutcomeDict)
                    # DEBUG (waiting for a refund dict)

                    self.predictElementHider("Resolved")
                    # calls the element hider to hide active/locked UI elements and show resolved

                    # need to check if user bet on this event
                    if self.predictionID.get("status", False):
                    # if there's a status, means user did bet
                        betStatus = self.predictionID["status"]
                        # grabs the status
                        betAmount = betStatus["bet"]
                        # gets the amount bet
                        betOutcomeID = betStatus["outcome"]
                        # grabs the outcome user voted for 

                        if betOutcomeID == winOutcomeID:
                        # if the stored outcome is the same as the winner
                            self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!\nYou win y points with a bet of {betAmount} points")
                            # text if user bet and won
                        elif winOutcomeID == "refund":
                        # if win outcome is a refund
                            self.predictResultLabel.setText(f"Prediction was refunded!")
                            # text if prediction was refunded
                        else:
                        # if the stored is not the same
                            self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!\nYou unfortunately lost {betAmount} points")
                            # text if user bet and lost
                    else:
                    # no status, no bet
                        self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                        # text if user did not bet

            if self.displayWindowBool:
            # if the display window bool is True (display is on)
                displayQueue.put(truePrediction)
                # puts the prediction dictionary into the queue

            try:
            # if there is no and has been no predict
                predictType = truePrediction.get("type", "none")
                # tries to grab the prediction type
                if predictType == "none":
                # if the type is none (hasn't been set by anything)
                    self.predictInfoLabel.setText("No predictions found, hopefully one opens soon :)")
                    # changes text to indicate status
            except:
            # if the predicttype grab fails (true predict doesn't exist)
                self.predictInfoLabel.setText("No predictions found, hopefully one opens soon :)")
                # sets same status message

        else:
        # if it wasn't a success
            self.predictTaskLabel.setText(f"Failed to get prediction details for {predictChannel}")
            # changes the text to inform



### Predict Element Hider ###



    def predictElementHider(self, style:str):
        """Function to hide specific parts of the prediction UI"""

        if style == "Active":
        # style is "active"
            listA = self.lockedPredictionElements
            listB = self.resolvedPredictionElements
            listC = self.activePredictionElements
            # assigns the keep list to active, other 2 to disable
        elif style == "Locked":
        # style is "locked"
            listA = self.activePredictionElements
            listB = self.resolvedPredictionElements
            listC = self.lockedPredictionElements
            # assigns the keep list to locked, other 2 to disable
        else:
        # style is "resolved"
            listA = self.activePredictionElements
            listB = self.lockedPredictionElements
            listC = self.resolvedPredictionElements
            # assigns the keep list to resolved, other 2 to disable

        for element in listA:
        # goes through the first disabled list
            try:
                element.hide()
                # disables all elements
            except:
                None
        for element in listB:
        # goes through the second disabled list
            try:
                element.hide()
                # disables all elements
            except:
                None
        for element in listC:
        # goes through the keep list
            try:
                element.show()
                # enables all elements
            except:
                None



### Prediction Buttons ###



    def predictButtonManager(self, button: int, action: str):
        """Function to ensure the buttons only have one active at one time"""

        buttonList = self.predictOptions
        # all the buttons

        state = False
        # default state (nothing on)

        for x in range (len(buttonList)):
        # goes through all the buttons
            if buttonList[x].isChecked():
            # checks if any are checked
                state = True
                # sets the bool to True
        
        if state:
        # if "state" is true, something should be on
        
            selectedButton = buttonList[(button - 1)]
            # selects the button from the list (num-1, since list = 0-4, buttons are 1-5)
            if action == "Init":
            # init on prediction find
                selectedButton.setStyleSheet("background-color: #404040;")
                # sets the selected button a lighter color
            elif action == "Winner":
            # if the button is the winning outcome
                selectedButton.setStyleSheet("background-color: green")
                # sets the selected button green
            buttonList.remove(selectedButton)
            # removes the selected button

            for x in range (len(buttonList)):
            # goes through every other button
                if action == "Init":
                # startup
                    buttonList[x].setStyleSheet("background-color: #181818;")
                    # sets the button background darker
                elif action == "Winner":
                # if the action is winner selection
                    buttonList[x].setStyleSheet("background-color: red;")
                    # sets the button red
                buttonList[x].setChecked(False)
                # disables the check status

        else:
        # if "state" is false, everything should be off
            for x in range (len(buttonList)):
            # goes through every other button
                buttonList[x].setStyleSheet("background-color: #181818;")
                # sets the button background darker
                buttonList[x].setChecked(False)
                # disables the check status



### modCheck ###



    def modCheck(self):
        """Checks if user is moderator before allowing mod view open"""
        userData = statusGrabber(self.state, predictChannel)
        # calls status grabber with the state and current channel
        if userData["success"]:
        # operation successful
            if userData["mod"]:
            # if the mod boolean is true
                # self.modWindowStart()
                # calls the window starter
                self.predictTaskLabel.setText("Moderator view is not yet implemented")
                # temp
            else:
            # user is not a mod
                self.predictTaskLabel.setText("No moderator status in this channel, cannot open window")
                # no mod inform
        else:
        # operation not successful
            self.predictTaskLabel.setText("Could not get moderator status, can't open view")
            # user inform



### Bet Masking ###



    def betMasker(self, action: str = None):
        """Function to ensure the bet remains valid"""

        currentBet = int(self.predictAmountLine.text().strip())
        # grabs the bet from the predict amount line
        currentBal = self.predictChannelPoints
        # grabs the balance from the variable

        if action == "Max":
        # if it calls to enter max points
            if currentBal < 250000:
            # if user has < 250k
                self.predictAmountLine.setText(f"{currentBal}")
                # all in
            else:
            # user has > 250k
                self.predictAmountLine.setText("250000")
                # sets Twitch max bet

        else:
        # if it doesn't call for max

            if currentBet > currentBal:
            # if the bet is larger than the current balance
                self.predictTaskLabel.setText("Bet cannot exceed balance!")
                # user inform
                self.predictAmountLine.setText(str(currentBal))
                # enforces the max bet

            if (currentBet > 250000) and (currentBal > 250000):
            # if the bet exceeds 250k (max bet) and the user has 250k
                self.predictTaskLabel.setText("Bets cannot exceed 250,000 points!")
                # user inform
                self.predictAmountLine.setText("250000")
                # sets it to the max cap
            
            if action == "Bet":
            # if the action is to bet
                self.predictUI("Bet")
                # calls the predict function with bet



### Auth Token Grabber ###



    def extractAuthToken(self):
        """Function to get the auth token from storage"""

        if not self.forceBrowserUI:
        # if the force browser boolean isn't true (only true if already ran once)
            self.browserShow.emit(True)
            # tells the browser to hide, but show the UI

        while not self.doneLoading:
        # if the browser isn't done loading yet
            QThread.sleep(1)
            # sleeps for a second to let it load

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
        # typically, if the token is valid, it'll be done by this timer



### Auth Token Validity Check ###



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
                self.taskText.emit("Auth token successfully validated...\nStarting headless TEPM...")
                # user update
                self.authValid.emit(True)
                # sets the pyqt signal to true
            else:
            # if the result is False (failure)
                raise Exception
                # forces an error
        except:
        # if the channel check fails
            self.taskText.emit("Token could not be validated, ensure you're logged in to Twitch\nIf this persists, ensure the hashes in hashes.json are valid")
            # changes UI text to error
            self.browserShow.emit(False)
            # tells browserShow to show the window
            try:
                self.refreshTokenButton.show()
                # shows the refresh button
            except:
                None



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



### Prediction Window Starter ###



    def predictionWinStart(self):
        """Function that starts the prediction window"""

        if not self.displayWindowBool:
        # if the thread isn't alive already
            displayLocalThread.start()
            # starts the communicator thread
            self.displayWindowBool = True
            # sets the bool to True so Window doesn't have to get called
            try:
                self.detailsButton.setEnabled(True)
            except:
                None
        else:
        # if the thread is alive
            self.detailsButton.setEnabled(False)
            # disables the button



### Prediction Detail Window ###



    def predictionDetailWindow(self, displayQueue: any):
        """Function that handles the external window"""

        displayWindowSP = subprocess.Popen([detailWindowPath], cwd=detailWindowDir, stdin=subprocess.PIPE, bufsize=0, creationflags=subprocess.CREATE_NO_WINDOW)
        # opens the prediction display window exe, passes the current working directory and allows input

        def predictionQueue(displayQueue: any):
            """Function to manage the display window input queue"""

            while not displayLocalEvent.is_set():
            # while the event isn't set (no need to quit)
                if displayQueue.empty():
                # if there's nothing in the queue
                    time.sleep(5)
                    # sleeps
                    continue
                    # resets loop

                if displayWindowSP.poll():
                # polls the subprocess, if it's alive it won't return anything, otherwise returns a code
                    self.displayWindowBool = False
                    # sets the bool to false
                    displayLocalEvent.set()
                    # sets the event, so that the thread dies
                
                newDict = displayQueue.get_nowait()
                # if there is something in the queue
                # DEBUG
                print("item in queue: ", newDict, "of type: ", type(newDict))

                dataPacket = json.dumps(newDict).encode("utf-8")
                # converts the dictionary into json
                displayWindowSP.stdin.write(dataPacket)
                # writes the packet to the display window program (sends)
                displayWindowSP.stdin.flush()
                # ensures all messages are sent

        threading.Thread(target = predictionQueue, daemon=True, args=(displayQueue, )).start()
        # makes a thread for the display window queue manager, passes the queue



### Mod Window Starter ###



    def modWindowStart(self):
        """Function that starts the moderator view window"""

        if not self.modWindowBool:
        # if the thread isn't alive already
            modLocalThread.start()
            # starts the communicator thread
            self.modWindowBool = True
            # sets the boolean to true to prevent re-open
            try:
                self.modButton.setEnabled(True)
            except:
                None
        else:
        # if the thread is alive
            self.modButton.setEnabled(False)
            # disables the button



### Mod Detail Window ###



    def modDetailWindow(self, modQueue: any):
        """Function that handles the external window"""

        displayWindowSP = subprocess.Popen([detailWindowPath], cwd=detailWindowDir, stdin=subprocess.PIPE, bufsize=0)#, creationflags=subprocess.CREATE_NO_WINDOW)
        # opens the prediction display window exe, passes the current working directory and allows input

        def moderatorQueue(queue: any):
            """Function to manage the display window input queue"""

            while queue.empty():
            # while there's nothing in the queue
                time.sleep(5)
                # sleeps
            
            newDict = queue.get_nowait()
            # if there is something in the queue
            print(sys.getsizeof(newDict))
            # DEBUG

            dataPacket = json.dumps(newDict).encode("utf-8")
            # converts the dictionary into json
            displayWindowSP.stdin.write(dataPacket)
            # writes the packet to the display window program (sends)
            displayWindowSP.stdin.flush()
            # ensures all messages are sent

        threading.Thread(target = moderatorQueue, daemon=True, args=(modQueue,)).start()
        # makes a thread for the display window queue manager, passes the display window input and the queue



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
            caseName = data["data"]["community"]["displayName"]
            # stores the case sensitive name (visual thing)
            try:
                return {"success": True, "error": "None", "points": points["balance"], "caseName": caseName}
                # returns a dictionary with the formatted name

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
            "operationName": hashMap["Streak Operation"],
            "variables": {
                "channelID": channelID
                # which channel to "login" to
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": hashMap["Streak Hash"],
                    "version": int(hashMap["Streak Version"])
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



### Status Grabber ###



def statusGrabber(state, channel: str) -> dict:
    """The function that checks user status in a channel"""
    
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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json

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



def predictGrabber(state, channel: str) -> dict:
    """The function that handles prediction data"""
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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json

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
                return {"success": True, "error": "None", "allowed": canPredict, "active": activePredicts, "locked": lockedPredicts, "resolved": resolvedPredicts}  
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



def sendPredict(state, bet: int, eventID: str, outcomeID: str) -> dict:
    """Function that makes a bet on given channel"""
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
        "operationName": hashMap["Bet Operation"],
        "variables": {
            "eventID": eventID,
            "outcomeID": outcomeID
        },
        "extensions": {
            "persistedQuery": {
                "sha256Hash": hashMap["Bet Hash"],
                "version": hashMap["Bet Version"]
                # this hash is found in devTools console, (search for GQL with "" operation)
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
            try:
            # tries to get the prediction information from the data
                predictionData = data["data"]["makePrediction"]
                # nested data
                if predictionData["error"] == "null":
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
        # simply stores the auth token here, so that both the main window and the point worker classes can call the point/streak grabbers with the same token



### Point/Streak/Predict Manager ###



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
                        # sleeps for a second (avoids limiting)

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
                            self.expiringList.append({channel: streak.get("expires", "Soon")})
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
                        "expiresAt": False
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
                self.totalPoints = foundPoints
                # total is the channel's total
            else:
            # if the point entry success is False (something went wrong)
                foundPoints = "Not found"
                # stores string
                errorBool = True
                # sets the error bool to true (will tell the UI to display error text)
                self.errorCount = (self.errorCount + 1)
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



### Prediction Refresh Thread ###



def predictionRefresh(event):
    """Function that runs on a loop when predict channel is set"""

    while not refreshEvent.is_set():
    # while the event isn't set
        time.sleep(10)
        # waits 10 seconds
        mainWindow.predictUI()
        # calls the predict UI to refresh data



### Window Startup ###



app = QApplication(sys.argv)
"""The application"""
appState = AppState()
"""App state instance to store some variables"""
startWindow = starterWindow()
"""The starter window"""
mainWindow = tepmWindow(appState)
"""The main window"""

refreshEvent = threading.Event()
"""An event to stop refreshing when needed"""
predictionThread = threading.Thread(target = predictionRefresh, args=(refreshEvent, ), daemon=True)
"""A thread for the prediction refreshing"""

displayQueue = queue.Queue()
"""A queue for display window input"""
displayLocalEvent = threading.Event()
"""A threading event to stop the details thread"""
displayLocalThread = threading.Thread(target = mainWindow.predictionDetailWindow, args=(displayQueue, ), daemon=True)
"""A thread just for the prediction window communicator"""

modQueue = queue.Queue()
"""A queue for moderator window input"""
modEvent = threading.Event()
"""A threading event to stop the mod view thread"""
modLocalThread = threading.Thread(target = lambda: print("mod"), args=(modQueue, modEvent, ), daemon=True)
"""A thread just for the moderator window communicator (doesn't exist yet)"""

### Starter Startup ###

app.exec()
# starts the application