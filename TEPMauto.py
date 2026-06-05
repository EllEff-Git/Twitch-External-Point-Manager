import sys, os, json, threading, psutil, time
# Required system management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)



directory = None
"""The base directory of the program, where TEPMauto.exe resides"""
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



class asyncAutoBetWindow(QMainWindow):
    """A TEPM auto-bet window to configure a channel's auto-betting"""

    textSwapSignal = pyqtSignal(int, str)
    """A pyQt signal to swap the labels"""

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM Auto-Better"
        # stores the program name

        self.running = True
        # runs

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setFixedSize(QSize(500, 700))
        # the window size

    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        # content margins
        self.mainLayout.setColumnMinimumWidth(0, 450)
        # sets the 0th column (only active one) to max size

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.setCentralWidget(self.container)
        # sets the main widget to display

        self.textSwapSignal.connect(self.balanceModifier)
        # connects the text signal to the modifying function

    ### Variables ###

        self.selectedChannel = None
        """Channel to auto-bet on"""
        self.targetOutcomes = []
        """A list of outcomes to target by name"""
        self.betSize = None
        """The size of the bet to place on auto-bet (int/"default")"""
        self.fallbackOutcomeFull = None
        """The fallback outcome to use (1-10, int)"""
        self.fallbackOutcomeMin = None
        """The fallback outcome to use if there's not enough outcomes (1 or 2)"""
        self.confirmPresses = 0
        """Tracker for confirm presses"""
        self.checkCount = 0
        """Tracker for parent process checks"""
        self.gainedPoints = 0
        """Tracker for points gained during auto-bet session"""
        self.predictionsMade = 0
        """Tracker for how many predictions were made"""

    ### Channel ###

        self.channelLayout = QGridLayout()
        """A layout for the channel and its swap button to sit in"""
        self.mainLayout.addLayout(self.channelLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the top of the main layout

        self.channelLabel = QLabel("No channel selected!")
        """The channel label"""
        self.channelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.channelLabel.setStyleSheet("""
            QLabel {
                font-style: italic;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        # stylesheet
        self.channelLabel.setMinimumSize(120, 40)
        # min size
        self.channelLabel.setToolTip("Currently active channel")
        # tooltip

        self.swapChannelButton = QPushButton("Swap Channel")
        """A button to swap the active channel"""
        self.swapChannelButton.setToolTip("Swap streams (opens input)")
        # tooltip
        self.swapChannelButton.setMinimumSize(80, 30)
        # min size

        self.channelLayout.addWidget(self.channelLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.channelLayout.addWidget(self.swapChannelButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to layout

        self.swapChannelButton.clicked.connect(self.swapChannel)
        # connects the button to the function

    ### Status & Details ###

        self.statusDetailLayout = QGridLayout()
        """A layout for the auto-bet detail labels and such"""
        self.statusDetailLayout.setColumnMinimumWidth(0, 400)
        # sets the (only) column to use a min width of 400 (matches the other elements below)
        self.mainLayout.addLayout(self.statusDetailLayout, 2, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the main layout, under the channel label/swap

        self.balanceLabel = QLabel("Balance")
        """Balance label"""
        self.balanceLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.balanceLabel.setStyleSheet("""
            QLabel {
                color: green;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        # stylesheet
        self.balanceLabel.setToolTip("Channel balance")
        # tooltip

        self.statusLabel = QLabel("Disabled")
        """Label to display current status"""
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.statusLabel.setStyleSheet("""
            QLabel {
                color: red;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        # stylesheet
        self.statusLabel.setToolTip("Auto-better status")
        # tooltip

        self.predictionNumLabel = QLabel("Auto-bet on 0 predictions")
        """Label to display current bet count"""
        self.predictionNumLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.gainLabel = QLabel(" ")
        """Label to display current point gains from auto-bets"""
        self.gainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.warningLabel = QLabel(" ")
        """Label to display warning(s) in"""
        self.warningLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.warningLabel.setStyleSheet("""
            QLabel {
                color: yellow;
                font-style: italic;
                font-size: 14px;
            }
        """)
        # stylesheet
        self.warningLabel.setToolTip("Status message")
        # tooltip

        self.statusDetailLayout.addWidget(self.balanceLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusDetailLayout.addWidget(self.statusLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusDetailLayout.addWidget(self.predictionNumLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusDetailLayout.addWidget(self.gainLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusDetailLayout.addWidget(self.warningLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to layout

    ### Fields ###

        self.outcomeTargets = QLineEdit()
        """Line to enter the targetable outcome names"""
        self.outcomeTargets.setMinimumSize(400, 40)
        # min size
        self.outcomeTargets.setPlaceholderText("Win, Loss...")
        # placeholder text
        self.outcomeTargets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.outcomeTargets.setToolTip("Enter any outcomes you'd like to match by name here\nComma-separated, not case-sensitive\n"
                                    "Eg. 'tails', 'heads', 'Win', 'Loss', 'W' 'L', '1', '2'...\n"
                                    "If no exact match is found, tries to find a partial match\n"
                                    "Eg. 'nine' as input, 'nine times' as outcome would be accepted\n"
                                    "Leaving empty requires an extra confirmation")
        # tooltip

        self.outcomeTargetsText = QLabel("Name-matched outcome(s)")
        """Text helper for outcome targets"""
        self.outcomeTargetsText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.betLine = QLineEdit("Default")
        """Line to enter the bet size"""
        self.betLine.setMinimumSize(400, 40)
        # min size
        self.betLine.setPlaceholderText("Default")
        # placeholder text
        self.betLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.betLine.setToolTip(f'Enter the bet size you would like to use\nAccepts any integer (non-decimal number) or "Default"\n"Default" follows the rounding/staged guides, if set in config')
        # tooltip

        self.betLineText = QLabel("The bet size to use")
        """Text helper for bet line"""
        self.betLineText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.fallbackOutcomeFullBox = QComboBox()
        """Combobox to select the outcome to fall back on (1-10)"""
        self.fallbackOutcomeFullBox.setMinimumSize(400, 40)
        # min size
        self.fallbackOutcomeFullBox.setToolTip("Select the outcome to fall back on, in case none of the name-matches are found\n"
        "Leaving this and the next on 'None' will only place bets when a name-match is found")
        # tooltip

        self.fallbackOutcomeFullText = QLabel("Fallback outcome number (1-10)")
        """Text helper for fallback full"""
        self.fallbackOutcomeFullText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.fallbackOutcomeFullBox.insertItem(0, "None")
        self.fallbackOutcomeFullBox.insertItem(1, "Outcome 1")
        self.fallbackOutcomeFullBox.insertItem(2, "Outcome 2")
        self.fallbackOutcomeFullBox.insertItem(3, "Outcome 3")
        self.fallbackOutcomeFullBox.insertItem(4, "Outcome 4")
        self.fallbackOutcomeFullBox.insertItem(5, "Outcome 5")
        self.fallbackOutcomeFullBox.insertItem(6, "Outcome 6")
        self.fallbackOutcomeFullBox.insertItem(7, "Outcome 7")
        self.fallbackOutcomeFullBox.insertItem(8, "Outcome 8")
        self.fallbackOutcomeFullBox.insertItem(9, "Outcome 9")
        self.fallbackOutcomeFullBox.insertItem(10, "Outcome 10")
        # adds all options

        self.fallbackOutcomeMinBox = QComboBox()
        """Combobox to select the outcome to finally fall back on (1-2)"""
        self.fallbackOutcomeMinBox.setMinimumSize(400, 40)
        # min size
        self.fallbackOutcomeMinBox.setToolTip("Select the outcome to fall back on, in case no name matches *and* there's not enough outcomes for the above option")
        # tooltip
        self.fallbackOutcomeMinBox.insertItem(0, "None")
        self.fallbackOutcomeMinBox.insertItem(1, "Outcome 1")
        self.fallbackOutcomeMinBox.insertItem(2, "Outcome 2")
        # adds all options

        self.fallbackOutcomeMinText = QLabel("Fallback outcome number (1-2)")
        """Text helper for fallback final"""
        self.fallbackOutcomeMinText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.mainLayout.addWidget(self.outcomeTargetsText, 4, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.mainLayout.addWidget(self.outcomeTargets, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.betLineText, 6, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.mainLayout.addWidget(self.betLine, 7, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.fallbackOutcomeFullText, 8, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.mainLayout.addWidget(self.fallbackOutcomeFullBox, 9, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.fallbackOutcomeMinText, 10, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.mainLayout.addWidget(self.fallbackOutcomeMinBox, 11, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to layout

    ### Spacer ###

        self.buttonSpacer = QSpacerItem(80, 50)
        """A spacer between the bottom spacers and the other items"""
        self.mainLayout.addItem(self.buttonSpacer, 12, 0)
        # adds to layout

    ### Buttons ###

        self.buttonLayout = QGridLayout()
        """A layout to store the buttons inside of"""
        self.mainLayout.addLayout(self.buttonLayout, 13, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the bottom of the main layout (under all other elements)

        self.confirmButton = QPushButton("Confirm")
        """Button to confirm the auto-bet settings"""
        self.confirmButton.setMinimumSize(80, 40)
        # min size
        self.confirmButton.setToolTip("Confirm options and start auto-better")
        # tooltip

        self.exitButton = QPushButton("Exit")
        """Button to exit the auto-better"""
        self.exitButton.setMinimumSize(80, 40)
        # min size
        self.exitButton.setToolTip("Exit the auto-better window\nStops bets")
        # tooltip

        self.stopButton = QPushButton("Stop")
        """Button to stop the auto-better"""
        self.stopButton.setMinimumSize(80, 40)
        # min size
        self.stopButton.setToolTip("Stop the auto-better\nDoesn't exit this window")
        # tooltip

        self.confirmButton.clicked.connect(self.rulesetSender)
        # connects the confirm button to the ruleset sender
        self.exitButton.clicked.connect(lambda: self.close())
        # connects the exit button to exiting the application
        self.stopButton.clicked.connect(lambda: self.rulesetSender(True, None, False))
        # connects the stop button to the ruleset sender with a True (to send forth a stop signal)

        self.buttonLayout.addWidget(self.stopButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.confirmButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.exitButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to the button layout

        self.setFocus()
        # sets focus to main window, rather than any element
        self.inputThreadManager()
        # runs the input thread function, starting the input poll thread



### Modify Text Fields ###

    def balanceModifier(self, balance:int, pointsName:str):
        """Function to swap the balance label"""
        self.balanceLabel.setText(f"Balance: {balance:,.0f} {pointsName}")
        # sets the balance string



### Input Thread ###

    def inputThreadManager(self):
        """Thread manager for stdin"""
        self.inputThread = threading.Thread(
            # makes a thread just for the input polling
            target=self.inputPoll,
            daemon=True
        )
        self.inputThread.start()
        # starts the thread



### Channel Swap Input ###

    def swapChannel(self):
        """Function to swap the currently selected channel"""
        newChannel, done = QInputDialog.getText(self, "Swap stream", "Set a new stream:")
        # opens an input box for the user to enter a new stream
        if done:
        # if user pressed ok
            if newChannel.strip() != "" and newChannel is not None:
            # if the channel isn't empty
                self.selectedChannel = newChannel.strip()
                # strips the channel
                self.channelLabel.setText(self.selectedChannel)
                # swaps the channel
                self.autoBetUserInform(f"Getting new data for {self.selectedChannel}")
                # user inform
                self.rulesetSender(False, self.selectedChannel, False)
                # calls the ruleset sender to send the new channel to TEPM
            else:
            # is empty
                self.autoBetUserInform("Can't select an empty stream!")
                # user inform



### Inform Function ###

    def autoBetUserInform(self, text:str):
        """Function to display a user inform message for a short duration"""
        self.warningLabel.setText(text)
        # sets the called text inform
        self.autoBetInformTimer = QTimer()
        # makes a QTimer
        self.autoBetInformTimer.timeout.connect(lambda: self.warningLabel.setText(" "))
        # when the timer is up, resets the text (hides)
        self.autoBetInformTimer.setSingleShot(True)
        # only runs once
        self.autoBetInformTimer.start(3500)
        # sets the timer to last 3.5 seconds



### Queue Poll ###

    def inputPoll(self):
        """The function that keeps polling the standard input for a dictionary"""
        while self.running:
        # while the program is running

            line = sys.stdin.readline()
            # grabs a sent message from TEPM
            if not line:
            # if it's not a valid message (empty)
                time.sleep(1)
                # waits a second
                continue
                # doesn't progress loop

            predictionDict = json.loads(line)
            # loads the sent line as a json dictionary

            if predictionDict["type"] == "status":
            # if the type is status (enabled/disabled check)
                status = predictionDict["status"]
                # grabs the status boolean
                self.statusUpdater(status)
                # calls the label updater based on the status boolean

            elif predictionDict["type"] == "exit":
            # if the type is an exit command
                autoBetWindowApp.exit()
                # exits the app

            elif predictionDict["type"] == "bet":
            # if the type is a bet (made a bet)
                self.predictionsMade += 1
                # adds 1 to predictions made
                if self.predictionsMade == 1:
                # if it's at 1 now
                    self.predictionNumLabel.setText(f"Auto-bet on 1 prediction")
                    # changes the label to match
                else:
                    self.predictionNumLabel.setText(f"Auto-bet on {self.predictionsMade} predictions")
                    # changes the label to match

            elif predictionDict["type"] == "payout":
            # if the type is a payout update (win/loss -> gain label)
                gain = int(predictionDict["data"]["gain"])
                # gets the points "gained"
                bet = int(predictionDict["data"]["bet"])
                # gets the points bet
                total = (gain - bet)
                # gets the total difference (points won, or how many points were lost if gain is 0)
                self.gainedPoints += total
                # adds to the running total
                self.predictionNumLabel.setText(f"Points gained from auto-bet: {self.gainedPoints:,.0f}")
                # changes the label to match formatted total

            elif predictionDict["type"] == "balance":
            # if the type is a balance update
                balance = predictionDict["balance"]
                # gets the passed balance
                pointsName = predictionDict["pointsName"]
                # gets the name of the points
                self.textSwapSignal.emit(balance, pointsName)
                # sends a signal to swap the balance and name of the points

            elif predictionDict["type"] == "channel":
            # if the type is channel 
                channel = predictionDict["channel"].strip()
                # gets the passed channel
                if channel and self.selectedChannel != channel:
                # if the selected channel doesn't match the current one in this view (and it's defined)
                    self.selectedChannel = channel
                    # sets it to match
                    self.channelLabel.setText(self.selectedChannel)
                    # sets the text label to match



### Parent Status Check ###

    def parentCheck(self):
        """Function to check if the parent (TEPM) is still alive"""
        return psutil.pid_exists(tepmPID)
        # checks if the PID exists for the parent process



### Status Updater ###

    def statusUpdater(self, status:bool):
        """Function that updates the status label based on the current status"""
        if status:
        # if the status is True (active)
            statusColor = "green"
            # sets the color to green
            self.statusLabel.setText("Enabled")
            # sets the label to match
        else:
        # status is False (off)
            statusColor = "red"
            # sets the color to red
            self.statusLabel.setText("Disabled")
            # sets the label to match

        self.statusLabel.setStyleSheet("""
            QLabel {{
                color: {statusColor};
                font-weight: bold;
                font-size: 14px;
            }}
        """.format(statusColor = statusColor))
        # stylesheet     



### Override Empty Outcome Targets ###

    def overrideTargets(self):
        """The function that ensures user wants to start the auto-better with no targets"""

        if self.confirmPresses >= 1:
        # if the confirm presses is already at 1 (or somehow higher)
            if self.doublePressTimer:
            # if the timer is defined
                self.doublePressTimer = None
                # deletes it 
            self.rulesetSender(False, None, True)
            # calls the ruleset finder with a True flag to override
            self.confirmPresses == 0
            # sets the presses to 0
        else:
        # otherwise (it's at 0)
            self.confirmPresses = 1
            # sets it to 1
            self.doublePressTimer = QTimer()
            # makes a timer
            self.doublePressTimer.timeout.connect(lambda: setattr(self, "confirmPresses", 0))
            # sets the confirm presses to 0 if the timer expires first
            self.autoBetUserInform("Click Confirm again within 5 seconds to\nignore name-matching and start auto-better")
            # user inform
            self.doublePressTimer.setSingleShot(True)
            # only runs once
            self.doublePressTimer.start(5000)
            # starts with 5000 ms (5s)



### Send Ruleset Dictionary ###

    def rulesetSender(self, stopCalled:bool=False, channelSwap:str=None, targetOverride:bool=False):
        """The function that sends the confirmed ruleset to the main program"""

        outputDict = {"stop": stopCalled}
        # dictionary to store all the requirements in

        if stopCalled:
        # if the boolean is set to True, meaning the button was used to stop the auto-better
            outputDict["type"] = "stop"
            # stop type dictionary
        else:
        # not a stop command (confirm)
            if channelSwap:
            # if there's a channel (to swap) defined
                outputDict["newChannel"] = channelSwap
                # adds a new channel entry
                outputDict["type"] = "swap"
                # swap type
            else:
                outputDict["newChannel"] = None
                # sets empty entry instead

                outputDict["channel"] = self.selectedChannel
                # gets the selected channel name (just a precaution thing to ensure the views are matched up)

                betSize = self.betLine.text().strip()
                # gets the bet size from the line edit
                try:
                # tries to...
                    betSize = int(betSize)
                    # convert the betsize to integer
                except:
                # if it can't
                    pass
                if type(betSize) != int:
                # if it didn't get turned into an integer
                    if betSize.lower() != "default":
                    # if the text doesn't match default either
                        self.autoBetUserInform("No (valid) bet amount defined!")
                        # user inform
                        return
                        # stops
                    else:
                    # if the text *does* match default
                        betSize = "Default"
                        # ensures consistent format, uses Default
                outputDict["betSize"] = betSize
                # stores it in the output dictionary

                if not targetOverride:
                # no overriding, checking target outcomes
                    outcomeText = self.outcomeTargets.text().strip()
                    # strips the outcome target line entry
                    if outcomeText and outcomeText != "":
                    # if it's valid text
                        try:
                            self.targetOutcomes = self.outcomeTargets.text().strip().split(",")
                            # turns the outcome field into a comma-separated list
                            outputDict["targetOutcomes"] = self.targetOutcomes
                            # adds the target outcomes to list
                        except Exception as tErr:
                            self.autoBetUserInform(f"Failed to parse outcome name-match(es)!\nError: {tErr}")
                            # user inform
                            return
                            # stops
                    else:
                    # empty
                        self.overrideTargets()
                        # calls the override 
                        return
                        # stops
                else:
                # if the function is called with target overrides, it's already ran once and is now being told to ignore the outcomes
                    self.autoBetUserInform("Ignoring outcome name-matching...")
                    # user inform
                    outputDict["targetOutcomes"] = []
                    # uses an empty map instead

                try:
                # tries to...
                    selectedFallback = self.fallbackOutcomeFullBox.currentIndex()
                    selectedSecondFallback = self.fallbackOutcomeMinBox.currentIndex()
                    # grabs both fallback indices (if they're not set to anything it may break)
                except:
                # if fails...
                    selectedFallback = 0
                    selectedSecondFallback = 0
                    # defaults to 0 (None)

                if selectedFallback == 0:
                # if it's 0
                    selectedFallback = None
                    # sets to actual None, not a string
                if selectedSecondFallback == 0:
                # if the secondary is 0
                    selectedSecondFallback = None
                    # sets to actual None, not a string

                outputDict["fallbackOutcomeFull"] = selectedFallback
                outputDict["fallbackOutcomeMin"] = selectedSecondFallback
                # adds to dictionary

                outputDict["type"] = "rules"
                # rule-set type

        print(json.dumps(outputDict), flush=True)
        # sends the dictionary as a "print" (stdout)



### Quit ###

    def closeEvent(self, event):
        """pyQt method to trigger a stop when exiting"""
        self.running = False
        # stops run

        self.close()
        # quits the app

        event.accept()
        # accepts the exit event from Windows



### Starter Startup ###

autoBetWindowApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
displayWindow = asyncAutoBetWindow()
# creates a window reference
tepmPID = int(sys.argv[1])
# grabs the parent process' (TEPM) PID 

sys.exit(autoBetWindowApp.exec())
# exceutes the app task (runs the QApplication)