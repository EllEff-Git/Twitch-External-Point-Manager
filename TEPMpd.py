import sys, os, threading, json, datetime
# Required system management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)

import atexit

atexit.register(lambda: print("PROCESS EXITING"))

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
    iconPath = os.path.join(directory, "icons", "tepmpdIcon.png")
    # reassigns the path variables accordingly



class asyncDetailsWindow(QMainWindow):
    """A TEPM helper window to display further prediction details"""

    def __init__(self):
        super().__init__()



    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM (P)rediction (D)etails"
        # stores the program name

        self.running = True
        # runs

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(700, 900))
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



    ### Prediction Overhead ###

        self.overheadLayout = QGridLayout()
        """A layout to host the prediction basic information"""
        
        self.predictChannelLabel = QLabel("This is the prediction channel")
        """Name of the channel"""

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


        self.overheadLayout.addWidget(self.predictChannelLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.overheadLayout.addWidget(self.predictInfoLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the channel name and prediction name to the layout

        self.mainLayout.addLayout(self.overheadLayout, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the overhead to the very top center
    


    ### Prediction Details ###

        self.detailsLayout = QGridLayout()
        """A layout to host the prediction details"""
        self.mainLayout.addLayout(self.detailsLayout, 1, 1, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the details in the middle of the screen (spans across 1-3 rows)

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

        self.detailsLayout.addWidget(self.predictStatusLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds status label to the 2nd nested layout (under the points)
        self.detailsLayout.addWidget(self.predictDetailLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds details label to the 2nd nested layout (under the prediction name)
        self.detailsLayout.addWidget(self.predictPoolLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds pool label to the 2nd nested layout (under the timer)
        self.detailsLayout.addWidget(self.predictTimerLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds timer label to the 2nd nested layout (under the details)
        self.detailsLayout.addWidget(self.predictResultLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds result label to the 2nd nested layout (under the pool)
        self.detailsLayout.addWidget(self.predictTaskLabel, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds task label to the 2nd nested layout (under the result)


    ### Prediction Outcome Layouts ###

        self.predictOutcomesLeft = QGridLayout()
        """A layout to host the left (1,3,5,7,9) outcomes"""

        self.predictOutcomesRight = QGridLayout()
        """A layout to host the right (2,4,6,8,10) outcomes"""

        self.mainLayout.addLayout(self.predictOutcomesLeft, 1, 0, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addLayout(self.predictOutcomesRight, 1, 2, 5, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds the outcomes to the left and right side of row 1



### Left Predicts (Odds) ###

    ### Predict Outcome 1 ###

        self.predictOutcome1 = QWidget()
        """A QWidget to hold the option 1 elements"""
        self.predictOutcome1Layout = QVBoxLayout()
        """A vertical layout to hold option 1 elements"""
        self.predictOutcome1.setLayout(self.predictOutcome1Layout)
        # sets layout
        self.predictOutcome1.setObjectName("Prediction Outcome 1")
        # object name to differentiate this from the other buttons (used for missing data)

        self.predictPayout1 = QLabel("0x")
        """Prediction option 1 payout multiplier label"""
        self.predictPayout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictPayout1.setToolTip("Prediction outcome multiplier")
        # top label 1

        self.predictOption1 = QPushButton(" ")
        """Prediction option 1 button"""
        self.predictOption1.setToolTip("Outcome 1")
        self.predictOption1.setEnabled(False)
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

        self.predictOutcomesLeft.addWidget(self.predictOutcome1, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption3.setEnabled(False)
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

        self.predictOutcomesLeft.addWidget(self.predictOutcome3, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption5.setEnabled(False)
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

        self.predictOutcomesLeft.addWidget(self.predictOutcome5, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption7.setEnabled(False)
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

        self.predictOutcomesLeft.addWidget(self.predictOutcome7, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption9.setEnabled(False)
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

        self.predictOutcomesLeft.addWidget(self.predictOutcome9, 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the overall widget to the layout



### Right Predicts (Evens) ###

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
        self.predictOption2.setEnabled(False)
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

        self.predictOutcomesRight.addWidget(self.predictOutcome2, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption4.setEnabled(False)
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

        self.predictOutcomesRight.addWidget(self.predictOutcome4, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption6.setEnabled(False)
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

        self.predictOutcomesRight.addWidget(self.predictOutcome6, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption8.setEnabled(False)
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

        self.predictOutcomesRight.addWidget(self.predictOutcome8, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.predictOption10.setEnabled(False)
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

        self.predictOutcomesRight.addWidget(self.predictOutcome10, 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
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



### Queue Poll ###

    def inputPoll(self):
        """The function that keeps polling the standard input for a dictionary"""
        while self.running:
        # while the program is running

            item = sys.stdin.read()
            # goes through the standard in and reads the sent dictionary
            if not item:
            # if there's nothing
                break
                # breaks the loop
            
            predictionDict = json.loads(item)
            # jsonifies the dictionary 

            print("found dict in pd")

            self.predictUpdateUI(predictionDict)
            # calls the prediction UI with the dictionary to update



### Prediction UI Update ###

    def predictUpdateUI(self, prediction: dict):
        """Function to update UI based on prediction/balance data"""

        totalPoints = 0
        # starts total point counter at 0

        if prediction["success"]:
        # if it was a success

            eventType = prediction["type"]
            # grabs the event type (active, locked, resolved)

            caseName = prediction.get("caseName", False)
            # grabs the case sensitive name, if it's available

            self.predictChannelLabel.setText(caseName)
            # updates the channel label

            title = prediction["title"]
            # grabs the prediction title
            outcomes = prediction["outcomes"]
            # grabs the list of outcomes
            creator = prediction["creator"]
            # grabs the creator name
            timestamp = prediction["timestamp"]
            # grabs the timestamp

            for x in range(len(outcomes)):
            # goes through each outcome again (needs to do it 2x because first need the total points for labeling)
                optionPoints = outcomes[x]["totalPoints"]
                # gets the points given to the option
                totalPoints += int(optionPoints)
                # adds the points to the total

            buttonCount = 0
            # starts a counter for buttons

            for x in range (len(outcomes)):
            # goes through each option
                optionName = outcomes[x]["title"]
                # gets the name of the option
                optionID = outcomes[x]["id"]
                # gets the outcome ID

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
                optionString = f"{optionPoints:,.0f} points\n({pointShare:.1f}%)\n{optionUsers:,.0f} users"
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

                buttonCount += 1
                # adds 1

            self.predictPoolLabel.setText(f"Total pool: {totalPoints:,.0f} points\n")
            # sets the total pool label
        
            if eventType == "active":
            # if the prediction is active
                self.predictLabelUpdater("Open Prediction:", f"{title}", f"{creator}, started {timestamp}", "green")
                # calls the updater to change UI
                self.predictResultLabel.setText(" ")
                # clears the result field

            else:
            # prediction isn't active (locked/resolved)

                if eventType == "locked":
                # if the prediction is locked
                    self.predictLabelUpdater("Closed Prediction:", f"{title}", f"{creator}, closed {timestamp}", "orange")
                    # calls the updater to change UI
                    self.predictResultLabel.setText(" ")
                    # clears the result field

                else:
                # prediction is resolved (paid out)
                    self.predictLabelUpdater("Paid Out Prediction:", f"{title}", f"{creator}, ended {timestamp}", "orange")
                    # calls the updater to change UI

                    winOutcomeDict = prediction["winner"]
                    # gets the winning outcome dictionary, otherwise uses set dictionary
                    winOutcomeID = winOutcomeDict["id"]
                    # grabs the winning ID
                    winOutcomeTitle = winOutcomeDict["title"]
                    # grabs the winning title

                    if winOutcomeID == "refund":
                    # if outcome is a refund
                        self.predictResultLabel.setText(f"Prediction was refunded!")
                        # text if prediction was refunded
                    else:
                    # if the outcome is anything else
                        self.predictResultLabel.setText(f"Winning outcome: {winOutcomeTitle}!")
                        # text if user did not bet

        else:
        # if it wasn't a success
            self.predictLabelUpdater("No prediction", " ", " ", "Red")
            # sets empty labels
            self.predictPoints1.setText("0 points\n(100%)\n0 users")
            # sets placeholder pool label
            self.predictionUserInform(f"Failed to get prediction details for {caseName}!")
            # changes the text to inform



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
        self.predictInformTimer.start(7500)
        # sets the timer to last 7.5 seconds



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



### Quit ###

    def closeEvent(self, event):
        """pyQt method to trigger a stop when exiting"""
        self.running = False
        # stops run

        displayWindowApp.quit()
        # quits the app

        event.accept()
        # accepts the exit event from Windows



### Starter Startup ###


displayWindowApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
displayWindow = asyncDetailsWindow()
# creates a window reference

inputThread = threading.Thread(target=displayWindow.inputPoll, args=(), daemon=True)
# makes a thread for the inputPoll to sit in
inputThread.start()
# starts the thread

displayWindowApp.exec()
# exceutes the app task (runs the QApplication)