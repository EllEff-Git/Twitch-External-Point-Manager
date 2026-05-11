import os, sys, requests, datetime, json, subprocess, uuid, threading
# Required program management
import pandas as pnd
# Soft required for CSV management (not required, but improves formatting)
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



tepmVer = "0.5.11.0652"
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
modWindowBool = False
"""Boolean that determines if the mod view window is open or not"""
displayWindowBool = False
"""Boolean that determines if the details view window is open or not"""



reqSession = requests.Session()
"""A request session that stores cached request information"""
rURL = "https://gql.twitch.tv/gql"
"""The Twitch endpoint to make requests to"""

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
    configLoaded = pyqtSignal()
    # a pyQt signal to indicate the config has been loaded successfully
    starterDone = pyqtSignal()
    # a pyQt signal to indicate readiness state

    def __init__(self):
        super().__init__()



    ### Init / Basic ###

        self.version = tepmVer
        # stores the version in self

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM Starter v{self.version}"
        # stores the program name

        self.optionReturn = False
        # boolean to store whether user has visited options or not (changes visuals)



    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(1000, 600)
        # the window size



    ### UI Elements ###

        self.mainLayout = QGridLayout()
        """The main layout that contains every sublayout and widget"""
        self.mainLayout.setSpacing(0)
        # removes spacing
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        # sets content margins

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 100)
        self.mainLayout.setRowMinimumHeight(2, 100)
        self.mainLayout.setRowMinimumHeight(3, 50)
        self.mainLayout.setRowMinimumHeight(4, 50)
        # sets the minimum height for rows

        self.mainLayout.setColumnMinimumWidth(0, 100)
        self.mainLayout.setColumnMinimumWidth(1, 200)
        self.mainLayout.setColumnMinimumWidth(2, 400)
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
        """A label to hold the main information about current process"""
        self.mainLabel.setText("TEPM starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(False)
        # makes the text wrap if it's too big
        self.mainLabel.setMaximumSize(400, 150)
        # tells the label to prefer the main layout's size
        self.mainLayout.addWidget(self.mainLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label to the main layout (should be top, always)



    ### Hideable/Showable Elements ###

        self.userInputField = QLineEdit()
        """A text field entry for anything"""
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
            
        self.chooseUsername = self.userInputField.text().strip()
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

        self.usernameButton.deleteLater()
        # deletes the username button
        self.mainLayout.removeWidget(self.usernameButton)
        # removes the button from the layout
        self.userInputField.hide()
        # hides the input field
        self.userInputField.setText("")
        # empties the text

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
        # if the streak map file exists
            with open(streakMapPath, "r") as strk:
            # opens the streak map json
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
            QTimer.singleShot(2000, self.taskChooserConfig)
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
        self.skipToBrowser.setToolTip("Bypass processing and enter the browser\nUse this if you want to change Twitch account")
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
            self.taskSingleChannelName.returnPressed.connect(lambda: self.taskRunner(3, 0, self.taskSingleChannelName.text().strip()))
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
            self.taskSingleChannelName.returnPressed.connect(lambda: self.taskRunner(4, 0, self.taskSingleChannelName.text().strip()))
            # runs the task with command 4 and the channel name field's text

        elif taskNum == 5:
        # if it's 5 (skips to browser for login management)
            self.labelSwap.emit("Opening browser view...")
            # user inform
            QTimer.singleShot(1500, lambda: self.taskRunner(5))
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
        global overrideChannel, canRun, activeOnly, enableStreaks, enablePoints, predictChannel, browserOnly
        # global -> local


        self.configLoaded.emit()
        # sends signal to inform controller the config is done

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

        elif task == 5:
        # task 5 is browser view
            browserOnly = True
            # sets the global boolean to True (tells the later functions to not run logic)

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
        if not task == 5:
        # if the task isn't to skip to browser
            browserOnly = False
            # sets the boolean (back) to False

        if canRun:
        # if the canRun is already set to True (returning from main)
            QTimer.singleShot(750, self.stopper)
            # quits the starter application window with a small delay
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
        # closes the window
        self.starterDone.emit()
        # sends a signal to the pyQt signal to let the controller / main window know starter is ready



### Return to Menu ###

    def returner(self):
        """Function to call to send back to the start of the start window"""
        self.labelSwap.emit("Reloading start menu...")
        # user infor
        self.returnToConfigChooser()
        # returns to config chooser (goes through this to ensure all elements are gone)



### Main App Window ###

class tepmWindow(QWidget):
    """The application window class"""

    authValid = pyqtSignal(bool)
    # creates a bool signal to check if the authentication code is ready
    taskText = pyqtSignal(str)
    # creates a string signal to set the task view to
    browserShow = pyqtSignal(bool)
    # creates a bool signal to check if the browser window should be shown, or a smaller preloader

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
        self.programName = f"Twitch External Point Manager v{self.version}"
        # stores the program name
        self.pid = os.getpid()
        # gets the current process' ID

        self.browserView = QWebEngineView(self)
        # adds a new webengine view

        self.predictChannelPoints = 0
        """Variable to store the predict channel's point balance"""
        self.detailsWindowBool = False
        """Whether the details window should be alive"""
        self.modWindowBool = False
        """Whether the mod window should be alive"""
        self.doneLoading = False
        """Boolean to check if browser is done loading"""

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
        self.taskView.setText("Loading browser...")
        # initial value
        self.taskView.setToolTip("Current operation")
        # tooltip
        self.taskView.setFixedSize(350, 40)
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
        self.refreshTokenButton.setToolTip("Press to attempt token re-validation")
        # tooltip
        self.taskGrid.addWidget(self.refreshTokenButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the right side of the taskView
        self.refreshTokenButton.hide()
        # hides it by default



    ### Browser ###

        self.browserPage = QWebEnginePage(passedProfile, self.browserView)
        # forms a browser page from the passed profile and the browser view widget

        self.browserView.setPage(self.browserPage)
        # sets the page to use the given properties
        self.browserView.setFixedSize(780, 450)
        # caps the browser size
        self.browserView.hide()
        # hides by default

        self.mainLayout.addWidget(self.browserView, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the browser to the layout
        self.browserView.setUrl(QUrl(self.defaultURL))
        # sets "default" url to open (twitch.tv)

        if not browserOnly:
        # if the browser-only mode isn't enabled
            ctrl.starterWindowDone.connect(self.cssStyleLoader)
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
        ctrl.taskChange.connect(self.taskLabelChanger)
        # connects the controller signal to the task view changer function



    ### Point/Streak Grab UI ###

        self.pointGrabLayout = QGridLayout()
        """A layout that contains the point/streak grab elements"""
        self.mainLayout.addLayout(self.pointGrabLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout
        self.pointGrabLayout.setSpacing(30)
        # sets spacing

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
        self.progressBar.setFixedSize(QSize(300, 25))
        # sets the progress bar's size, so that the spacers don't do weird stuff
        self.progressBar.setToolTip("Current progress")
        # tooltip
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to center
        self.progressBar.hide()
        # hides by default

        self.channelLabel = QLabel()
        # adds a label for the channel's info text
        self.channelLabel.setToolTip("Current task")
        # tooltip
        self.channelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.channelLabel.setFixedSize(QSize(300, 30))
        # sets fixed size
        self.channelLabel.setWordWrap(True)
        # allows the text to wrap, if it's too long
        self.channelLabel.hide()
        # hides by default

        self.totalLabel = QLabel()
        # total label (total found points)
        self.totalLabel.setToolTip("Total point accumulation")
        # tooltip
        self.totalLabel.setText("Nothing found yet")
        # sets initial text
        self.totalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.totalLabel.hide()
        # hides by default

        self.currentLabel = QLabel()
        # index/progress label
        self.currentLabel.setToolTip("Progress")
        # tooltip
        self.currentLabel.setText(f"0 / {self.channelLength}")
        # sets initial progress
        self.currentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.currentLabel.hide()
        # hides by default

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

        self.predictLayout = QGridLayout()
        """A layout for the predictions"""
        self.mainLayout.addLayout(self.predictLayout, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout



    ### Predict Details ###

        self.predictInfoLayout = QGridLayout()
        """A nested layout that hosts basic information about the prediction(s)"""
        self.predictInfoLayout.setSpacing(25)
        # adds a little more spacing
        self.predictLayout.addLayout(self.predictInfoLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # top middle

        self.predictDetailLayout = QGridLayout()
        """A further nested layout that hosts prediction specifics (status, name, creation, pool, outcome, task)"""
        self.predictDetailLayout.setVerticalSpacing(25)
        # adds a little more vertical space
        self.predictInfoLayout.addLayout(self.predictDetailLayout, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # under the basic info, above the buttons

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
        self.predictInfoLayout.addWidget(self.predictChannelLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the layout (top middle)

        self.predictStatusLabel = QLabel(" ")
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
        self.predictPoolLabel.hide()
        # hides by default

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
        self.predictResultLabel.hide()
        # hides by default

        self.predictTaskLabel = QLabel(" ")
        """A label that holds the current task result/string"""
        self.predictTaskLabel.setStyleSheet("""
            QLabel {
                color: yellow;
                font-style: italic;
                font-size: 13px;
            }
        """)
        self.predictTaskLabel.setToolTip("Program status inform")
        # tooltip
        self.predictTaskLabel.setMinimumSize(350, 50)
        # min size
        self.predictTaskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.predictTaskLabel.hide()
        # hides by default

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

        self.predictInfoItems = [self.predictStatusLabel, self.predictInfoLabel, self.predictDetailLabel, self.predictTimerLabel, self.predictPoolLabel]
        """A list of all the prediction-related information labels"""



    ### Predict Button/Point Layout ###

        self.predictOutcomeLayout = QHBoxLayout()
        """A nested layout that hosts the bet selectors and point totals"""
        self.predictOutcomeLayout.setSpacing(15)
        # sets lower spacing
        self.predictOutcomeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns center
        self.predictInfoLayout.addLayout(self.predictOutcomeLayout, 4, 2, alignment=Qt.AlignmentFlag.AlignCenter)
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
            outcome.hide()
            # hides the widget by default

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
        self.predictInfoLayout.addLayout(self.channelPointLayout, 5, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the higher up prediction layout

        self.currentBetLabel = QLabel("Current Bet")
        """A label that holds the current bet amount (total per channel)"""
        self.currentBetLabel.setToolTip("Total bet for this prediction in this channel")
        # tooltip
        self.currentBetLabel.setMinimumSize(350, 50)
        # min size
        self.currentBetLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.currentBetLabel.hide()
        # hides by default
        
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
        self.predictPointLabel.hide()
        # hides by default

        self.channelPointLayout.addWidget(self.predictPointLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds it to the channel point layout (below the bet pools/buttons)
        self.channelPointLayout.addWidget(self.currentBetLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the main info layout below the balance



    ### Predict Actions ###

        self.predictSuperLayout = QGridLayout()
        """Layout that holds prediction elements (mod/details)"""
        self.predictLayout.addLayout(self.predictSuperLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout under the info/details layout

        self.predictBetLayout = QGridLayout()
        """Layout that holds the betting elements (amount + bet buttons)"""
        self.predictSuperLayout.addLayout(self.predictBetLayout, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds into the super layout in the middle (col 1)

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
        self.maxBetButton.setToolTip("Set max bet (requires confirmation)")
        # tooltip
        self.maxBetButton.setMinimumSize(70, 40)
        # min size

        self.modButton = QPushButton("Mod View")
        """Button to open mod view"""
        self.modButton.setToolTip("Open moderator view tab")
        # tooltip
        self.modButton.setMinimumSize(80, 40)
        # min size

        self.detailsButton = QPushButton("Details")
        """Button to display further information about the bet"""
        self.detailsButton.setToolTip("Display more information about the prediction")
        # tooltip
        self.detailsButton.setMinimumSize(80, 40)
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

        self.predictBetButton.clicked.connect(self.predictIntermediary)
        # connects the bet button to the predict intermediary
        self.maxBetButton.clicked.connect(lambda: self.betMasker("Max"))
        # connects the max bet button to the bet masking function
        self.modButton.clicked.connect(self.modCheck)
        # connects the mod button to the mod check
        self.detailsButton.clicked.connect(ctrl.startDetails)
        # connects the detail button to the ui window
        
        self.predictAmountLine.hide()
        self.predictBetButton.hide()
        self.modButton.hide()
        self.maxBetButton.hide()
        # hides all elements by default



    ### Channel Swap ###

        self.predictChannelLayout = QGridLayout()
        """A layout that holds the channel swapping elements (channel entry, change button)"""
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

        self.predictChannelLine.hide()
        self.predictChannelSwapButton.hide()
        # hides elements by default



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
        self.menuButton.hide()
        # hides by default

        self.exitButton = QPushButton("Exit")
        """A button to Exit"""
        self.exitButton.setToolTip("Quit the application")
        # tooltip
        self.exitButton.setMinimumSize(150, 50)
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



    ### Element Lists ###

        self.activePredictionElements = [self.predictTimerLabel]
        """A list of elements exclusive to the active prediction style"""

        self.lockedPredictionElements = []
        """A list of elements exclusive to the locked prediction style"""

        self.resolvedPredictionElements = [self.predictResultLabel]
        """A list of elements exclusive to the resolved prediction style"""

        self.pointItems = [self.progressBar, self.channelLabel, self.totalLabel, self.currentLabel]
        """A list of point grab elements"""

        self.predictItems = [self.predictChannelLabel, self.predictStatusLabel, self.predictInfoLabel,
                            self.predictDetailLabel, self.predictTimerLabel, self.predictPoolLabel,
                            self.predictResultLabel, self.predictTaskLabel, self.currentBetLabel,
                            self.predictPointLabel, self.predictAmountLine, self.predictBetButton,
                            self.maxBetButton, self.modButton, self.detailsButton, self.predictChannelLine,
                            self.predictChannelSwapButton]
        """A list of prediction elements"""



### Browser Window UI ###

    def browserWindow(self, status: bool):
        """A function to determine if the browser view should appear or not"""
        if status and not browserOnly:
        # if the status is True (meaning the auth token is all good and the browser isn't needed)
            self.setMinimumSize(500, 300)
            self.resize(500, 300)
            # the window size
        else:
        # if the status is False (auth token not valid, need to log in or something)
            self.setMinimumSize(800, 500)
            self.resize(800, 500)
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

    def headlessUI(self):
        """A function to add the headless UI layout widgets"""

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

        if predictChannel:
        # if a predict channel is set
            self.progressBar.hide()
            self.totalLabel.hide()
            self.currentLabel.hide()
            # hides both point/streak labels + progress bar

        elif overrideChannel:
        # if the override channel is set (doesn't really need a progress bar, 1/1)
            self.totalLabel.hide()
            self.currentLabel.hide()
            self.progressBar.hide()
            # hides both point/streak labels + progress bar

        elif not predictChannel and not overrideChannel:
        # if predictChannel and override aren't set (must be a list)
            self.progressBar.show()
            self.channelLabel.show()
            self.totalLabel.show()
            self.currentLabel.show()
            # shows the items



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
        # if it's passed and isn't empty
            for x in range (len(expiryList)):
            # goes through all the elements
                if not expiryList[x]:
                # if the value is False
                    expiryList.pop(x)
                    # deletes it
                
            expiryString = f"Channels with expiring streaks: {", ".join(expiryList)}"
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
                finalString = f"{points} points and a streak of {streak} for {overrideChannel}"
                # forms final string
            else:
            # error
                finalString = f"Couldn't get points or streak for {overrideChannel}"
                # forms final string with error

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
            ctrl.pwStopSignal.emit()
            # calls the stopper to stop polling new prediction data
            ctrl.windowSwap("Starter")
            # shows the starter window
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

        try:
        # tries
            self.browserView.hide()
            # hides the browser view
        except:
        # may already be hidden
            pass
            # skip

        if predictChannel:
        # if the prediction channel is set

            self.setMinimumSize(850, 900)
            self.resize(850, 900)
            # the window size

            self.swapMainUI("Predict")
            # swaps the elements

        else:
        # if the prediction channel isn't set

            self.swapMainUI("Points")
            # swaps the elements

            self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # centers everything to middle
            self.setMinimumSize(500, 300)
            self.resize(500, 300)
            # the window size

            QTimer.singleShot(3000, self.startPointWorker)
            # calls the point manager to start getting points



### Swap UI ###

    def swapMainUI(self, action:str):
        """Function that swaps the UI layout between predict and point/streak grab"""

        if action == "Predict":
        # prediction UI activate
            for element in self.pointItems:
                element.hide()
                # hides the point elements
            for element in self.predictItems:
                element.show()
                # shows the prediction base elements
            for element in self.predictPoints:
                element.show()
                # shows the prediction point pools

            try:
                self.pointGrabStopLayout.removeWidget(self.menuButton)
                self.pointGrabStopLayout.removeWidget(self.exitButton)
                # removes the buttons from the point grab layout
                self.stopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
                self.stopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
                # adds them to the stop layout (prediction UI)
            except:
                print("Couldn't swap to predict")

            self.predictUI("Init")
            # calls the prediction UI to start
   
        else:
        # point grab UI activate
            for element in self.predictItems:
                element.hide()
                # hides the prediction base elements
            for element in self.predictPoints:
                element.hide()
                # hides the prediction point pools
            for element in self.predictOutcomeWidgets:
                element.hide()
                # hides the prediction bet options
            for element in self.pointItems:
                element.show()
                # shows the point elements

            try:
                self.stopLayout.removeWidget(self.menuButton)
                self.stopLayout.removeWidget(self.exitButton)
                # removes the buttons from the stop layout (prediction UI)
                self.pointGrabStopLayout.addWidget(self.menuButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
                self.pointGrabStopLayout.addWidget(self.exitButton, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
                # adds them to the point grab layout
            except:
                print("Couldn't swap to points")

            self.headlessUI()
            # calls the headless UI to start



### Prediction UI ###

    def predictUI(self, action:str = None):
        """Function that handles prediction UI changes"""
        global predictChannel
        # global -> local

        if action == "Init":
        # init action
            ctrl.predictWorkerStart()
            # starts the predict/balance refresh thread loop
            self.eop()
            # calls "end of program" to show menu and exit buttons
            
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
                self.predictChannelLine.setText("")
                # resets the text
                ctrl.predictionTimerOverride.emit()
                # sends a signal to override the timer and get a data refresh right away



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

    def predictLabelUpdater(self, statusText: str, infoText: str, detailText: str, color: str, elementType: str):
        """Function to update all prediction-related labels"""

        self.predictStatusLabel.setText(statusText)
        # sets the status label
        self.predictInfoLabel.setText(infoText)
        # sets the info label
        self.predictDetailLabel.setText(f"Created by {detailText}")
        # sets the details label
        self.predictStatusUpdate(color)
        # sets the text color

        for label in self.predictInfoItems:
        # goes through each label in the list of prediction labels
            try:
                label.show()
                # shows it
            except:
                pass
                # skips if can't

        self.predictElementHider(elementType)
        # calls the element hider to hide locked/resolved UI elements and show active



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



### Screen Resize ###

    def screenResize(self, buttonCount: int):
        """Resizes screen based on active # of buttons"""
        
        buttonWidth = 140
        # how wide one button should count as (px)
        newSize = max(900, int(buttonCount * buttonWidth))
        # calculates a new size for the screen width (to fit buttons), picks the larger width from 900 and (x*y)

        self.setMinimumSize(850, newSize)
        self.resize(850, newSize)
        # the window size



### Prediction -> UI Update ###

    def predictUpdateUI(self, prediction: dict):
        """Function to update UI based on prediction/balance data"""
        global predictChannel
        # global -> local

        totalPoints = 0
        # starts total point counter at 0
        shouldUpdate = True
        # boolean for "should the full package be updated"

        if prediction["success"]:
        # if it was a success

            oldID = self.predictionID.get("lastID", None)
            oldType = self.predictionID.get("lastType", None)
            # grabs the old ID and type to compare

            eventID = prediction["id"]
            # grabs the event ID from the prediction dictionary
            eventType = prediction["type"]
            # grabs the event type (active, locked, resolved)

            self.predictChannelPoints = prediction.get("balance", 0)
            # sets the balance to match (default 0 if not found)
            self.predictPointLabel.setText(f"Balance: {self.predictChannelPoints:,.0f} points")
            # update the balance label
            self.predictPointLabel.show()
            # enables the label (if it was hidden)

            if (oldID == eventID) and (oldType == eventType):
            # if the IDs match and the types match (same dictionary)
                shouldUpdate = False
                # changes the boolean to prevent full update
            else:
            # not the same data
                self.predictionID["lastID"] = eventID
                self.predictionID["lastType"] = eventType
                # copies the new values over so they can be compared next time

            if prediction.get("caseName", False):
            # if the case sensitive name is set
                predictChannel = prediction["caseName"]
                # reassigns the predictionChannel to match the case sensitive one
                self.predictChannelLabel.setText(predictChannel)
                # sets the text of the channel label to match channel
                self.predictChannelLabel.show()
                # enables the label (if it was hidden)
            
            if not (predictChannel == self.currentChannel):
            # if the channel being operated on is NOT the current channel stored here
                self.currentChannel = predictChannel
                # updates current channel
                shouldUpdate = True
                # forces full UI update

            timeNow = datetime.datetime.now().astimezone().strftime("%#H:%M:%S")
            # grabs current time and formats it
            self.predictTaskLabel.setText(f"Last update: {timeNow}")
            # sets the task indicator to indicate the task that has been tasked

            listOfElementLists = [self.predictOutcomeWidgets, self.predictInfoItems]
            # list of element lists
            if shouldUpdate:
            # if there's new data (hides these to prevent misleading data (new channel, old data) + to reset button count)
                for elementList in listOfElementLists:
                # goes through each list of elements
                    for item in elementList:
                        # goes through each element in the list
                            try:
                            # tries
                                item.hide()
                                # hides the element
                            except:
                            # on fail
                                pass
                                # does nothing
                
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
            ownVoteWin = prediction["sumWon"]
            # gets the total won points (null until resolved)
            storedVoteDict = self.predictionNumbers.get(eventID, {"bet": 999999})
            # grabs the stored dictionary from prediction numbers (falls back to dict with bet = 999999 if doesn't exist

            if not (ownVoteSum == storedVoteDict["bet"]):
            # if the vote sum doesn't match the previously stored vote
                shouldUpdate = True
                # sets the boolean to True so the UI gets fully updates
                self.predictionNumbers[eventID] = {"bet": ownVoteSum, "option": ownVoteID}
                # stores the bet and voted outcome in the dictionary with the eventID as key

            if not ownVoteID:
            # no vote ID = no bet (it already gets checked in grab to be for *this* event)
                self.currentBetLabel.hide()
                # hides the label
            else:
            # vote ID = vote in this event
                self.currentBetLabel.show()
                # shows the label

            for x in range(len(outcomes)):
            # goes through each outcome again (needs to do it 2x because first need the total points for labeling)
                optionPoints = outcomes[x]["totalPoints"]
                # gets the points given to the option
                totalPoints += int(optionPoints)
                # adds the points to the total

            self.predictionKeys[eventID] = {}
            # creates a keymap for this event (or clears)

            buttonCount = 0
            # starts a counter for buttons

            for x in range (len(outcomes)):
            # goes through each option
                optionName = outcomes[x]["title"]
                # gets the name of the option
                optionID = outcomes[x]["id"]
                # gets the outcome ID

                if ownVoteID == optionID:
                # if the user vote matches this vote
                    self.predictionID[eventID] = {"title": optionName, "id": optionID}
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
                optionString = f"{optionPoints:,.0f} points\n({pointShare:.0f}%)\n{optionUsers:,.0f} users"
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

                self.predictOutcomeWidgets[x].show()
                # enables the xth widget (label + button + label)

                self.predictionKeys[eventID][optionID] = buttonX
                self.predictionKeys[eventID][buttonX] = optionID
                # stores the outcome and button as keys:values for each other

                buttonCount += 1
                # adds 1

            if buttonCount >= 6 and buttonCount != self.currentSize:
            # if there's more than or eq to 6 buttons (7 * 140 > 900, 6 will be the default size)
            # also compares against current size to avoid resizing every time this is ran
                self.currentSize = buttonCount
                # sets the current size
                self.screenResize(buttonCount)
                # calls the resizer with the count, to set a larger screen

            if ownVoteID:
            # if user voted in this event
                voteShare = ((ownVoteSum / totalPoints) * 100)
                # calculates user's share of the total pool in percentages
                self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} points\nYour share: {voteShare:.0f}%")
                # sets text with user share %
            else:
            # user did not vote in this event
                self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} points")
                # sets the total pool label
            
            if shouldUpdate:
            # if the boolean is set to True (means the event status or bet has changed)

                if eventType == "active":
                # if the prediction is active
                    self.maxBetButton.setEnabled(True)
                    self.predictBetButton.setEnabled(True)
                    self.predictAmountLine.setEnabled(True)
                    # enables the bet-related options
                    self.predictLabelUpdater("Open Prediction:", f"{title}", f"{creator}, started {timestamp}", "green", "Active")
                    # calls the updater to change UI

                    if ownVoteID:
                    # if user voted
                        betString = f"Current bet: {ownVoteSum:,.0f} on {self.predictionID[eventID]["title"]}"
                        # forms a string to indicate bet
                        self.betLabelUpdater(betString, "Green")
                        # updates bet label
                        self.currentBetLabel.show()
                        # unhides
                        buttonToSelect = self.predictionKeys[eventID][ownVoteID]
                        # gets the stored option ID's (voted outcome ID) linked button identifier
                        self.predictButtonManager("Lock", buttonToSelect)
                        # calls to lock the option selection buttons
                    else:
                    # user didn't vote yet
                        self.predictButtonManager("Init")
                        # calls for the buttons to get unlocked/reset

                    ctrl.timerSwap.emit(3)
                    # if the event is active, speeds up update timer to get more data quicker

                else:
                # prediction isn't active (locked/resolved)
                    self.maxBetButton.setEnabled(False)
                    self.predictBetButton.setEnabled(False)
                    self.predictAmountLine.setEnabled(False)
                    # disables the bet-related options

                    if eventType == "locked":
                    # if the prediction is locked
                        self.predictLabelUpdater("Closed Prediction:", f"{title}", f"{creator}, closed {timestamp}", "orange", "Locked")
                        # calls the updater to change UI

                        if ownVoteID:
                        # if user voted
                            betWin = ((ownVoteSum * self.predictionKeys[eventID][ownVoteID]) - ownVoteSum)
                            # gets the potential bet win
                            betString = f"You bet {ownVoteSum:,.0f} on {self.predictionID[eventID]["title"]}\n(+{betWin:,.0f} on win)"
                            # forms a string to indicate bet
                            self.betLabelUpdater(betString, "Green")
                            # sets text to match
                            self.currentBetLabel.show()
                            # unhides
                            self.predictButtonManager("Lock", self.predictionKeys[eventID][ownVoteID])
                            # calls to lock the option selection buttons
                        else:
                        # user didn't vote
                            self.predictButtonManager("Lock")
                            # calls to lock everything
                    
                        ctrl.timerSwap.emit(10)
                        # if the event is locked, slows the updater down to ~normal speed

                    else:
                    # prediction is resolved (paid out)
                        self.predictLabelUpdater("Paid Out Prediction:", f"{title}", f"{creator}, ended {timestamp}", "orange", "Resolved")
                        # calls the updater to change UI
                        ctrl.timerSwap.emit(10)
                        # if the event is resolved, slows the updater way down

                        winOutcomeDict = prediction["winner"]
                        # gets the winning outcome dictionary, otherwise uses set dictionary
                        winOutcomeID = winOutcomeDict["id"]
                        # grabs the winning ID
                        winOutcomeTitle = winOutcomeDict["title"]
                        # grabs the winning title

                        print("Winning outcome (wait for refund):", winOutcomeDict)

                        if winOutcomeID == "refund":
                        # if outcome is a refund
                            self.predictResultLabel.setText(f"Prediction was refunded!")
                            # text if prediction was refunded
                            self.betLabelUpdater(" ")
                            # ensures the bet is cleared
                            self.predictButtonManager("Init")
                            # clears the status', unlocks buttons
                        else:
                        # if the outcome is anything else
                            if ownVoteID:
                            # if user voted
                                self.predictButtonManager("Winner", self.predictionKeys[eventID][ownVoteID])
                                # calls the predict button manager with the map[ID] (to get the button object) to highlight the winning button in green

                                if ownVoteID == winOutcomeID:
                                # if the stored outcome is the same as the winner
                                    self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                    # text if user bet and won
                                    newPoints = (ownVoteWin - ownVoteSum)
                                    # gets the amount of points won (gained)
                                    newPointsPercent = ((newPoints / ownVoteSum) * 100)
                                    # gets the percentage of bet that the new points amount to
                                    winString = f"You won {ownVoteWin:,.0f} points with a bet of {ownVoteSum:,.0f} points! (+{(newPoints):,.0f} / {newPointsPercent:.1f}%)"
                                    # forms win string
                                    self.betLabelUpdater(winString, "Green")
                                    # bet label update
                                else:
                                # if the stored is not the same
                                    self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                    # text if user bet and lost
                                    self.betLabelUpdater(f"You lost {ownVoteSum:.0f} points", "Red")
                                    # bet label update
                            else:
                            # no status, no bet
                                self.predictButtonManager("Winner", self.predictionKeys[eventID][winOutcomeID])
                                # calls the predict button manager to highlight winner in green
                                self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                                # text if user did not bet
                                self.betLabelUpdater(" ")
                                # bet label update

            if self.detailsWindowBool:
            # if the display window bool is True (details view is on)
                None
                # self.displayQueue.put(prediction)
                # puts the prediction dictionary into the queue
        
            if self.modWindowBool:
            # if the mod window bool is True (mod view is on)
                None
                # self.modQueue.put(prediction)
                # puts the prediction dictionary into the queue

        else:
        # if it wasn't a success
            self.predictTimerLabel.hide()
            self.currentBetLabel.hide()
            self.predictResultLabel.hide()
            # these should be off 
            self.predictTaskLabel.setText(f"Failed to get prediction details for {predictChannel}!")
            # changes the text to inform



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

        try:
        # tries to get the text
            bet = int(self.predictAmountLine.text().strip())
            # grabs the bet integer from the current bet line
        except:
        # if it fails (empty)
            bet = False
            # sets to false (flags)

        if not selectedButton or not bet:
        # if either option is not set
            self.predictTaskLabel.setText("No bet set or outcome selected, please try again!")
            # sets error text
        else:
        # if both are set successfully
            optionName = selectedButton.text()
            # grabs the text of the button
            try:
                eventID = self.predictionID["lastID"]
                # grabs the event ID from the ID map
                outcomeID = self.predictionKeys[eventID][selectedButton]
                # grabs the outcome ID linked to that option from the key map
            except:
                outcomeID = None
                # sets to none

            currentBet = self.predictionNumbers.get(eventID, {"option": None})["option"]
            # grabs the current voted outcome ID 

            if outcomeID:
            # if outcomeID is defined (didn't fail, was set correctly)
                if currentBet == outcomeID or not currentBet:
                # if there's already a bet with this outcome or no bet set yet
                    ctrl.predictMaker.emit(bet, eventID, outcomeID, optionName)
                    # calls the pyQt signal with the details (bet int, outcomeID)
                else:
                    self.predictTaskLabel.setText("Cannot bet on two outcomes!")
                    # user inform
            else:
            # if it wasn't defined (either didn't get set properly or failed to grab)
                self.predictTaskLabel.setText(f"Failed to send bet due to internal error!")
                # user inform



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

    def predictButtonManager(self, action: str = None, passedButton = None):
        """Function to ensure the buttons only have one active at one time"""

        selectedButton = self.buttonGroup.checkedButton()
        # grabs the button that's checked and sets as selected

        if not selectedButton:
        # if none are checked
            if passedButton:
            # if the button argument is defined
                selectedButton = passedButton
                # sets the selected button from button

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

            elif action == "Init" or action == "Lock":
            # startup / lock
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
                # lock
                    button.setEnabled(False)
                    # buttons turned off when locked (can't change bet once confirmed)



### modCheck ###

    def modCheck(self) -> bool:
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
                return True
                # a mod
            else:
            # user is not a mod
                self.predictTaskLabel.setText("No moderator status in this channel")
                # no mod inform
                return False
                # not a mod
        else:
        # operation not successful
            self.predictTaskLabel.setText("Could not get moderator status, can't open view")
            # user inform
            return False
            # something went wrong, can't auth



### Bet Masking ###

    def betMasker(self, action: str = None):
        """Function to ensure the bet remains valid"""

        try:
        # tries to get the current bet written
            currentBet = int(self.predictAmountLine.text().strip())
            # grabs the bet from the predict amount line
        except:
        # if it fails (is empty)
            currentBet = 0
            # sets to 0

        if currentBet == 0 and action != "Max":
        # if the bet is 0 (not a max bet request)
            self.predictTaskLabel.setText("Cannot bet 0 points")
            # user inform
            return
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
        else:
        # if it doesn't call for max
            if currentBet > currentBal:
            # if the bet is larger than the current balance
                self.predictTaskLabel.setText("Bet cannot exceed balance!")
                # user inform
                self.predictAmountLine.setText(currentBal)
                # enforces the max bet

                if action == "Check":
                # if this is a check request
                    return False
                    # returns False (wasn't valid)

            if action == "Check":
            # if this is a check request
                return True
                # returns True (is valid)



### Style Loader ###

    def cssStyleLoader(self):
        """Function that loads the CSS stylesheet"""

        with open(cssPath, "r") as seess:
        # opens the CSS stylesheet
            self.setStyleSheet(seess.read())
            # sets the stylesheet for the class

        self.extractAuthToken()
        # calls the next stage



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



### Task View Changer ###

    def taskLabelChanger(self, text):
        """Function to change the task view via external signals"""
        self.predictTaskLabel.setText(text)
        self.taskView.setText(text)
        # swaps both predict task and taskView (either one could be up)



### Return to Menu ###

    def returner(self):
        """Function to call to send back to the start of the main window"""
        self.taskView.setText("Reloading main screen...")
        # user inform

        layoutsToClear = [self.mainLayout, self.predictInfoLayout, 
                          self.predictDetailLayout, self.predictOutcomeLayout, 
                          self.predictSuperLayout, self.predictBetLayout, 
                          self.predictLayout, self.stopLayout, 
                          self.predictChannelLayout, self.channelPointLayout]
        # list of layouts to hide items in

        for layout in layoutsToClear:
        # repeats for each layout in the list
            try:
            # tries (may "fail")
                while layout.count():
                # while there's items in the subtask layout
                    item = layout.takeAt(0)
                    # grabs the item at position 0
                    try:
                    # tries to take the widget info (can't if it's an item like spacer)
                        widget = item.widget()
                        # grabs the widget from the item
                        if widget:
                        # if there's a widget set
                            widget.hide()
                            # hides the widget
                    except:
                    # if it can't (already hidden?)
                        pass
            except:
            # fail usually just means an item was deleted unexpectedly (which is fine)
                None
                # does nothing

        self.uiStyle()
        # calls the uistyle function to reset the UI
        self.channels = self.getChannelList()
        # calls the get channel list to update the channels (prediction, override, file...)



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
    global reqSession

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
    global reqSession

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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json

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
            try:
                return {"success": True, "error": "None", "points": points, "caseName": caseName}
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

def streakGrabber(state, channel: str, channelID:int = None) -> dict:
    """The function that grabs streak information"""
    global reqSession

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
    
    global reqSession

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

def grabPrediction(state, channel: str) -> dict:
    """The function that grabs prediction data"""
    global reqSession

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
    global reqSession

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
    global reqSession

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
            # stringifies the channelID

    if channelID != None:
    # if it's now set
        payload = {
        # forms a payload from the required information
            "operationName": hashMap["Prediction Make Operation"],
            "variables": {
                "input": {
                    "title": title,
                    "channelID": channelID,
                    "predictionWindowSeconds": duration,
                    "outcomes": outcomes
                }
            },
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": hashMap["Prediction Make Hash"],
                    "version": hashMap["Prediction Make Version"]
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
    global reqSession

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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json
    print(data)

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
    global reqSession

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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json
    print(data)

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
    global reqSession

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

    request = reqSession.post(rURL, json = payload, headers = headers)
    # forms a data request
    data = request.json()
    # stores the resulting data json
    print(data)

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

            self.csvWriter(csvEntries, self.errorCount, self.maxStreak)
            # calls the csvWriter with the formed map (dictionary) and the number of errors (gets passed to finished UI)

            

### CSV Writer ###

    def csvWriter(self, csvEntries: dict, errors: int, maxStreak: int, expiryList: list=None, singlePoints: int = None):
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
        if not singlePoints:
        # if the singlePoints wasn't passed
            singlePoints = 0
            # sets to 0

        self.pointWorkerDone.emit(errors, maxStreak, expiryList, singlePoints)
        # once done, sends a signal to the finished pyqt signal with the error count, highest streak and expiration list
        self.running = False
        # stops itself



### Prediction Class ###

class predictionWorker(QObject):
    """A class to handle the prediction data grabbing and manipulation"""

    predictionDataSignal = pyqtSignal(dict, dict)
    """A pyQt signal containing new prediction and balance data"""
    predictionGrabStop = pyqtSignal()
    """A pyQt signal to indicate the prediction task should end"""

    def __init__(self, state):
        super().__init__()

        self.state = state
        # stores the appState in self
        self.running = True
        # sets the running status to True
        ctrl.predictMaker.connect(self.predict)
        # connects the predict maker signal to makePrediction function
        ctrl.pwStopSignal.connect(self.stopper)
        # connects the stop signal to the stopper function (stops grabbing predictions)
        ctrl.timerSwap.connect(self.timerChange)
        # connects the timer swap signal to the timer change function
        ctrl.predictionTimerOverride.connect(self.timerOverride)
        # connects the timer override signal to the timer override function
        self.timer = 15
        # a timer stored here that determines how often the refreshes occur
        self.refresh = threading.Event()
        # a threading event to store the timer in



### Run Prediction Worker ###

    def run(self):
        """Function that loops function calls"""
        while self.running:
        # while the running status is True
            self.intermed()
            # keeps calling the intermediary command with a timed cooldown
            self.refresh.wait(timeout=self.timer)
            # waits the timer duration if it's not set before that
            self.refresh.clear()
            # clears the event queue



### Override Timer ###

    def timerOverride(self):
        """Function that sets an event, overriding the current timer"""
        self.refresh.set()
        # sets an event, forcing run() to immediately run intermed, refreshing data faster



### Intermed ###

    def intermed(self) -> pyqtSignal:
        """Intermediary function that merges two data grab function calls"""
        pData = self.getPrediction()
        # calls getPrediction to get new data
        bData = self.getBalance()
        # calls getBalance to get new data
        self.predictionDataSignal.emit(pData, bData)
        # sends the returned dictionary through the pyQt signal



### Timer Change ###

    def timerChange(self, newTime: int):
        """Function that changes the internally stored timer (to speed up or slow down refreshing)"""
        self.timer = newTime
        # swaps the timer to the new time



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



### Stop Prediction Worker ###

    def stopper(self):
        """Function to stop the worker"""
        self.running = False
        # sets running status to False, stops running



### Make Prediction ###

    def predict(self, bet: int, eventID: str, outcomeID: str, selected: str):
        """Function to make a bet"""
  
        betInfo = sendPrediction(self.state, bet, eventID, outcomeID)
        # calls the prediction sender with the state, the bet amount and the prediction details

        if betInfo["success"]:
        # if the return is a success
            ctrl.taskChange.emit(f"Bet {bet} on {selected}\nMay the odds be ever in your favor!")
            # sets info text
            ctrl.mainWindow.predictAmountLine.setText("")
            # clears the text
        else:
        # if the return isn't a success
            err = betInfo["error"]
            # grabs the error message from the return
            ctrl.taskChange.emit(f"Failed to send bet! Error: {err}")
            # updates user on error



### Manage Prediction ###

    def predictionManager(self, action:str, title:str=None, eventID:str=None, outcomeID:str=None, outcomes:list=None, duration:int=None, channelID:int=None):
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
            strDict = startPrediction(self.state, title, duration, outcomes, channelID)
            # calls prediction starter
            if strDict["success"]:
            # if the return has success True
                print("made prediction yippie")
            else:
                print("didn't make prediction saj")

        elif action == "Delete":
        # delete the prediction
            delDict = deletePrediction(self.state, eventID)
            # calls prediction deleter
            if delDict["success"]:
                print("deleted prediction yippie")
            else:
                print("didn't delete, saj")

        elif action == "Payout":
        # pay out an option
            payDict = payoutPrediction(self.state, eventID, outcomeID)
            # calls prediction payout
            if payDict["success"]:
                print("paid out prediction yippie")
            else:
                print("didn't pay out, saj")

        elif action == "Lock":
        # lock/close prediction
            lockDict = lockPrediction(self.state, eventID)
            # calls prediction locker
            if lockDict["success"]:
                print("locked prediction, yippie")
            else:
                print("didn't lock prediction, saj")



### Controller Class ###

class windowController(QObject):
    """A class to handle the cross-class/function communication and startup"""

    starterWindowDone = pyqtSignal()
    """A pyQt signal to signal the starter window is done loading"""
    taskChange = pyqtSignal(str)
    """A pyQt signal to tell the main window to change the current task string"""
    newPData = pyqtSignal(dict)
    """A pyQt signal to send data to prediction UI"""
    pwStopSignal = pyqtSignal()
    """A pyQt signal to tell the prediction worker to stop"""
    predictMaker = pyqtSignal(int, str, str, str)
    """A pyQt signal to form a bet (bet: int, eventID: str, outcomeID: str, name: str)"""
    timerSwap = pyqtSignal(int)
    """A pyQt signal to change the prediction/balance refresh timer"""
    predictionTimerOverride = pyqtSignal()
    """A pyQt signal to set an event and immediately override timer"""


    def __init__(self):
        super().__init__()

        self.state = appState
        # stores the app state "storage"

        self.startWindow = starterWindow()
        # stores the starter window class
        self.startWindow.show()
        # shows the window
        self.mainWindow = None
        # not defined yet

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
    


### Starter ###

    def mainStarter(self):
        """Function to start the main window"""
        self.mainWindow = tepmWindow(self.state, self.browserProfile)
        # stores the main window class
        self.mainWindow.show()
        # shows



### Continuer ###

    def mainContinuer(self):
        """Function to progress the main window"""
        self.starterWindowDone.emit()
        # emits signal to inform mainWindow it's done 
    


### Prediction Worker ###

    def predictWorkerStart(self):
        """Function to start the prediction data grabbing"""
        
        self.predictThread = QThread()
        # makes a thread for the prediction hashing
        self.predictThread.setObjectName("Prediction Thread")
        # object name (debug)
        self.predictWorker = predictionWorker(self.state)
        # assigns prediction worker
        self.predictWorker.moveToThread(self.predictThread)
        # sets the prediction worker to use the formed thread

        self.predictThread.started.connect(self.predictWorker.run)
        # when the thread starts, runs the worker

        self.predictWorker.predictionGrabStop.connect(self.predictThread.quit)
        self.predictWorker.predictionGrabStop.connect(self.predictWorker.deleteLater)
        # when the prediction wants to stop, quits the thread and the worker
        self.predictThread.finished.connect(self.predictThread.deleteLater)
        # when the thread is done (no worker), deletes the thread itself, too

        self.predictWorker.predictionDataSignal.connect(self.predictionDataGrab)
        # when there's new data, connects it to data handler function

        self.predictThread.start()
        # starts the thread



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
            
            if truePrediction:
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
                predictionStamp = timestampLocal.strftime("%B %#d at %#H:%M:%S")
                # finalizes it into legible format

                if balance["success"]:
                # if the balance returned a success dictionary
                    currentBal = balance["points"]
                    # grabs the points
                    caseName = balance["caseName"]
                    # grabs the case sensitive name
                else:
                # if not
                    currentBal = 0
                    # sets the balance to 0
                    caseName = False
                    # sets the case sensitive name to False

                finalPrediction = {
                    "success": True,
                    "type": truePrediction["type"],
                    "id": eventID,
                    "title": title,
                    "outcomes": outcomes,
                    "timestamp": predictionStamp,
                    "creator": creator,
                    "winner": winner,
                    "timer": timer,
                    "localTS": timestampLocal,
                    "balance": currentBal,
                    "caseName": caseName,
                    "votedOutcome": votedOutcome,
                    "votedSum": votedSum,
                    "sumWon": sumWon
                }
                # forms a dictionary with easier-to-access data than the full thing (reduces work for UI)

            else:
            # no prediction data
                finalPrediction = {
                    "success": False
                }
                # fail dictionary

            self.newPData.emit(finalPrediction)
            # sends the dictionary with success state

        else:
        # if it was not a success
            self.newPData.emit({"success": False})
            # sends a dictionary with fail state



### Swap Window ###

    def windowSwap(self, window: str):
        """Function to swap active window"""
        if window == "Starter":
        # calls for starter window to be visible (start -> main -> start)
            self.mainWindow.hide()
            # hides the main window
            self.startWindow.returner()
            # calls the returner function to send back to the start
            self.startWindow.show()
            # shows the starter window
        else:
        # not starter (main -> start -> main)
            self.startWindow.hide()
            # hides the starter window
            self.mainStarter()
            # calls mainStarter to restart the main class
            self.mainWindow.show()
            # shows the main window



### Details View ###

    def startDetails(self):
        """Function to open the details view"""
        ctrl.taskChange.emit("Details view is currently unavailable")
        #predictionWinStart(self.displayLocalThread)
        # starts the window starter



### Mod View ###

    def startModView(self):
        """Function to open the mod view"""
        ctrl.taskChange.emit("Mod view is not yet implemented")
        #modWindowStart(self.modLocalThread)
        # starts the mod view



### Window Startup ###

app = QApplication(sys.argv)
"""The application"""
appState = AppState()
"""App state instance to store some variables"""
ctrl = windowController()
"""The window controller class"""

sys.exit(app.exec())
# starts the application (exits when done)