import sys, os, json, zoneinfo, datetime
# Required system management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)
import pandas as Pandas
# Required for dataframe construction from JSON
import matplotlib.dates as MDates
from matplotlib.ticker import StrMethodFormatter
import matplotlib.pyplot as Plot
# Required for chart visuals
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# Required for charting



directory = None
"""The base directory of the program, where TEPMhist.exe resides"""
iconPath = None
"""The path of the app icon png"""

Plot.rcParams["font.family"] = ["Segoe UI Emoji", "DejaVu Sans"]
# updates the plotting parameters to use a different font (since a lot of predictions use emoji, which aren't supported by the default font)



if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "tepmhistIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "..", "icons", "tepmhistIcon.png")
    # reassigns the path variables accordingly



class asyncHistWindow(QMainWindow):
    """A TEPM history window to display a prediction history chart page"""

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"TEPM Hist"
        # stores the program name

        self.historyPath = os.path.join(directory, "..", "Prediction History.json")
        # forms the history file path

        self.localTZ = datetime.datetime.now().astimezone().tzinfo
        # gets local timezone

        self.activeChart = 1
        """Active chart state, used to track which chart is visible"""
        self.currentChannel = None
        """The current channel selected for the PPC chart"""
        self.storedChannels = []
        """The full list of channels stored in the json file"""
        self.caseChannels = {}
        """A map of channels with their case-insensitive spellings"""
        self.channelPointMap = {}
        """A map of channels with their points and point save times"""
        self.chartViewDots = 25
        """How many chart data points (dots) are visible at once"""
        self.chartView = 0
        """What index of chart view the current view is on (starts at 0)"""

        self.running = True
        # runs

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(1300, 925))
        # the window size

    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setContentsMargins(15, 30, 15, 30)
        # sets margins around layout

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.setCentralWidget(self.container)
        # sets the main widget to display

    ### Status Label ###

        self.statusLabel = QLabel()
        # a label to display current status in
        self.statusLabel.setMinimumSize(300, 60)
        # minimum size
        self.statusLabel.setStyleSheet("""
            QLabel {
                color: yellow;
                font-style: italic;
                font-size: 15px;
            }
        """)
        # status label
        self.mainLayout.addWidget(self.statusLabel, 0, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout, top center (spans both middle columns)

    ### Swap Button ###

        self.swapButton = QPushButton("Swap Chart")
        # a button to swap between the charts
        self.swapButton.setToolTip("Swap the active chart between points and W/L stats\nHold Shift while clicking to go back")
        # tooltip
        self.swapButton.clicked.connect(lambda: self.chartSwapper("Swap"))
        # connects the button to the function
        self.swapButton.setMinimumSize(150, 40)
        # min size
        self.mainLayout.addWidget(self.swapButton, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds to layout (bottom row, left side)

    ### Left / Right Buttons ###

        self.leftButton = QPushButton("<")
        # a button to flip the active chart to the left
        self.leftButton.setToolTip("Move the chart view to the left")
        # tooltip
        self.leftButton.setFixedSize(20, 50)
        # sets button size
        self.leftButton.clicked.connect(lambda: self.chartMover(-1))
        # connects the left button to the moving function with -1 (<-)

        self.rightButton = QPushButton(">")
        # a button to flip the active chart to the right
        self.rightButton.setToolTip("Move the chart view to the right")
        # tooltip
        self.rightButton.setFixedSize(20, 50)
        # sets button size
        self.rightButton.clicked.connect(lambda: self.chartMover(1))
        # connects the left button to the moving function with +1 (->)

        self.mainLayout.addWidget(self.leftButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.rightButton, 2, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the buttons to the layout

    ### Current Channel ###

        self.currentChannelLine = QLineEdit()
        # an entry line to change the selected channel
        self.currentChannelLine.setPlaceholderText("Current Channel")
        # background text
        self.currentChannelLine.setToolTip("Change the currently inspected channel (for points over time)\nUses auto-filling, if nothing shows up, there's no recorded data for that channel (yet)")
        # tooltip
        self.currentChannelLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns the text inside to center
        self.currentChannelLine.setMinimumSize(150, 40)
        # min size
        self.mainLayout.addWidget(self.currentChannelLine, 3, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds to layout (bottom row, right side)

        self.channelModel = QStringListModel()
        # a list model to update the channelCompleter's list

        self.channelCompleter = QCompleter(self.channelModel)
        # an auto-fill from all the channels stored in .json
        self.channelCompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # makes it not case-sensitive
        self.currentChannelLine.setCompleter(self.channelCompleter)
        # makes the current channel edit line use the completer

        self.currentChannelLine.returnPressed.connect(lambda: self.channelToPPC(self.currentChannelLine.text().strip()))
        # connects pressing enter (return) to the points per channel pre-chart function, passes the current channel

    ### Figure / Canvas ###

        self.chartFigure = Figure(figsize=(19, 8))
        # the figure (width, height)

        self.chartCanvas = FigureCanvas(self.chartFigure)
        # the canvas (the actual chart)
        self.chartCanvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # allows the chart to expand if it has space

        self.mainLayout.addWidget(self.chartCanvas, 2, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the canvas to the layout (between the status and swap button/channel select)

        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        # allows the row and columns the chart sits in to stretch

    ### Startup ###

        self.historyLoader()
        # calls the history loader to get the prediction data
        self.channelPointGain()
        # calls the point gain function to form a map of each channel's point growth
        self.pointsCharter()
        # calls the points charter to form the initial chart



### User Inform ###

    def userStatusInform(self, text:str):
        """Function to display a user inform message for a short duration"""
        self.statusLabel.setText(text)
        # sets the called text inform
        self.predictInformTimer = QTimer()
        # makes a QTimer
        self.predictInformTimer.timeout.connect(lambda: self.statusLabel.setText(" "))
        # when the timer is up, resets the text
        self.predictInformTimer.setSingleShot(True)
        # only runs once
        self.predictInformTimer.start(5000)
        # sets the timer to last 5 seconds



### JSON File Loader ###

    def historyLoader(self):
        """Loads the Prediction History.json file"""

        with open(self.historyPath, "r", encoding="utf-8") as prdH:
        # opens the prediction history file
            self.historyData = json.load(prdH)
            # loads the prediction history into a variable

        self.historyDataFrame = Pandas.DataFrame([
            {
                "channel": entry.get("channel"),
                "title": entry.get("title"),
                "timestamp": entry.get("timestamp"),
                "winner": entry.get("winner"),
                "balance": entry.get("balance"),
                "bet": entry.get("bet", None),
                "gain": entry.get("gain", None),
                "W/L": entry.get("W/L", None)
            }
            for entry in self.historyData.values()
        ])
        # goes through the data dictionary, grabs the entry values for each prediction event (last 3 can be empty, if no vote was entered)

        self.historyDataFrame["timestamp"] = Pandas.to_datetime(self.historyDataFrame["timestamp"], utc=True)
        # refactors all the timestamps to actual datetime objects (so they can be detected as such)
        self.historyDataFrame["plotStamp"] = (self.historyDataFrame["timestamp"].dt.tz_convert(self.localTZ).dt.tz_localize(None))
        # stores a second timestamp entry with local timezone applied and removes local tag

        self.winLoss = self.historyDataFrame[self.historyDataFrame["W/L"].isin(["Win", "Loss"])]
        # only stores the W/L values if the values are either Win or Loss

        self.pointGains = self.historyDataFrame.dropna(subset=["gain"])
        # drops the entries where "gain" isn't present (user didn't vote)

        self.channelsPoints = self.historyDataFrame.dropna(subset=["balance"])
        # drops the entries where "balance" isn't present (shouldn't drop anything)

        self.storedChannels = self.historyDataFrame["channel"].dropna().unique().tolist()
        # takes *all* stored channels in the json, drops empty values, only takes uniques -> forms a list
        self.channelModel.setStringList(self.storedChannels)
        # makes the model list use the formed list of channels
        self.currentChannel = self.storedChannels[0]
        # gets the first channel stored, to have *a* value

        self.caseChannels = {channel.lower(): channel for channel in self.storedChannels}
        # stores a map of all channels with their lowercase counterparts (so that input can be case-insensitive, but still show right name)



### Channel Points Gain ###

    def channelPointGain(self):
        """Builds a map of channels with their points at stored dates"""

        for channel, group in self.channelsPoints.groupby("channel"):
        # goes through every channel in the channel points list

            group = group.sort_values("plotStamp")
            # sorts by timestamp (to ensure chronological order, should already be this way)
 
            timestamps = group["plotStamp"].tolist()
            # turns the timestamps into a list
            points = group["balance"].tolist()
            # turns the points into a list

            self.channelPointMap[channel] = {
                "timestamps": timestamps,
                "points": points
            }
            # makes an entry for every channel in the list of channels with the list of timestamps and corresponding balance (points)



### Point Gain Charter ###

    def pointsCharter(self):
        """Function to draw the point gain/loss bar chart"""

        self.chartFigure.clear()
        # clears the existing figure (if any)
        self.chartFigure.patch.set_facecolor("#1E1E1E")
        # sets the background color for the figure

        ax = self.chartFigure.add_subplot(111)
        # adds a subplot (axes), 111 = 1 row, 1 column, 1st subplot
        ax.set_facecolor("#1E1E1E")
        # sets the background color for the axes

        startDots = self.chartView
        endDots = (self.chartView + self.chartViewDots)
        # calculates the new start and end points 

        if self.pointGains.empty:
        # if the gain entries don't exist (no data)
            ax.text(0.5, 0.5, "No valid point gain data", color="white", ha="center", va="center", fontsize=14)
            # forms a text instead
            ax.axis("off")
            # disables the X and Y axis grids
        else:
        # if data exists
            pointData = self.chartDotsCount(self.pointGains)
            # calls the chart dot counter to tell the chart what data points to select

            colors = ["#00751F" if gain >= 0 else "#630700" for gain in pointData["gain"]]
            # selects colors (green if the gain is positive, red if negative)

            pointData.plot(kind="bar", y="gain", x="title", ax=ax, legend=False, color=colors)
            # makes a bar chart with gain in Y-axis and the prediction titles in X-axis (hides legend)

            ax.tick_params(axis="x", colors="white", rotation=15)
            # sets the X-axis ticks/text to white and slants them at 15deg
            ax.tick_params(axis="y", colors="white")
            # sets the Y-axis ticks/text to white

            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
            # formats the Y-axis points to use thousand-separation (1,000)
            ax.tick_params(axis="y", colors="white")
            # makes the Y-axis ticks white

            ax.set_ylabel("Points Trend", color="white")
            # sets the Y-axis label
            ax.set_xlabel("Prediction", color="white")
            # sets the X-axis label

            for xPoint, yPoint in enumerate(pointData["gain"]):
            # goes through every gain data point
                pointOffset = 14 if yPoint >= 0 else -13
                # offsets the points on the bars by +14 if the gain's positive, -13 if the gain is negative
                ax.annotate(f"{yPoint:,.0f}", xy=(xPoint, yPoint), xytext=(0, pointOffset), textcoords=("offset points"), color="white", fontsize=10, ha="center", va="top")
                # adds a little vertical offset to the points, formats them into thousand-separated values (1,000)

            ax.grid(True, color="gray", linestyle="--", alpha=0.3)
            # adds a semi-transparent grid

        ax.set_title(f"Points Gained/Lost via Predictions (across all channels)\n(Data: {startDots} -> {endDots})", color="white")
        # sets the chart title

        self.chartCanvas.draw()
        # draws the canvas



### W/L Stats Charter ###

    def statsCharter(self):
        """Function to draw the user W/L ratio pie chart"""

        self.chartFigure.clear()
        # clears the existing figure
        self.chartFigure.patch.set_facecolor("#1E1E1E")
        # sets the background color for the figure
        
        ax = self.chartFigure.add_subplot(111)
        # adds a subplot (axes), 111 = 1 row, 1 column, 1st subplot
        ax.set_facecolor("#1E1E1E")
        # sets the background color for the axes

        if self.winLoss.empty:
        # if the win/loss entries don't exist (no data)
            ax.text(0.5, 0.5, "No valid Win/Loss data", color="white", ha="center", va="center", fontsize=14)
            # forms a text instead
        else:
        # if the data exists
            wlCount = self.winLoss["W/L"].value_counts()
            # gets to total Win/Loss value counts (how many of each there are)
            totalWL = wlCount.sum()
            # adds up the wins and losses for the total
            colors = ["#00751F" if state == "Win" else "#630700" for state in wlCount.index]
            # selects colors (green if the state is a win, red if loss)
            ax.pie(wlCount, labels=wlCount.index, 
                   autopct=lambda pct: f"{int(round(pct / 100 * totalWL))} ({pct:.1f}%)", 
                   colors=colors, startangle=90, textprops={"color":"white"})
            # makes a pie chart with the Win/Loss counts, using the Win and Loss as labels, adds the percentage of each with ".1f" (1 decimal) accuracy

        ax.set_title("Prediction Win / Loss History", color="white")
        # sets the chart title
        ax.axis("off")
        # disables the X and Y axis grids

        self.chartCanvas.draw()
        # draws the canvas



### Channel Entry -> PPC Chart ###

    def channelToPPC(self, channel:str):
        """Function used to check status of channel before calling PPC charter"""

        if not channel.strip().lower() in self.caseChannels:
        # if the channel isn't stored in the map of case-insensitive channels 
            self.userStatusInform(f"{channel} isn't present in the history file!")
            # user inform
            return
            # stop

        self.pointsPerChannel(channel)
        # calls the PPC charter



### Points Gain Per Channel ###

    def pointsPerChannel(self, channel:str):
        """Function to draw the user point gain per channel line chart"""

        caseChannel = self.caseChannels[channel.strip().lower()]
        # gets the case-sensitive (real) channel name
        self.currentChannelLine.setText("")
        # clears the channel entry text

        self.currentChannel = caseChannel
        # sets the points per channel channel

        self.chartFigure.clear()
        # clears the existing figure
        self.chartFigure.patch.set_facecolor("#1E1E1E")
        # sets the background color for the figure
        
        ax = self.chartFigure.add_subplot(111)
        # adds a subplot (axes), 111 = 1 row, 1 column, 1st subplot
        ax.set_facecolor("#1E1E1E")
        # sets the background color for the axes

        channelTimestamps = MDates.date2num(self.channelPointMap[caseChannel]["timestamps"])
        # gets the list of timestamps for the channel
        channelPoints = self.channelPointMap[caseChannel]["points"]
        # gets the list of points/balance for the channel

        plotStartDot = self.chartView
        # gets the current start point for the chart
        plotEndDot = (self.chartView + self.chartViewDots)
        # calculates the end point

        ax.plot(channelTimestamps[plotStartDot:plotEndDot], channelPoints[plotStartDot:plotEndDot], marker="o", color="#00687A", linewidth=2)
        # plots the chart with the timestamps and points
        
        for xPoint, yPoint in zip(channelTimestamps[plotStartDot:plotEndDot], channelPoints[plotStartDot:plotEndDot]):
        # goes through every X and Y axis data point
            ax.annotate(f"{yPoint:,.0f}", xy=(xPoint, yPoint), xytext=(0, 16), textcoords=("offset points"), color="white", fontsize=10, ha="center", va="top")
            # adds a little vertical offset to the points, formats them into thousand-separated values (1,000)

        ax.set_title(f"Points over time for {caseChannel}\nUse the channel swapping here!\n(Data: {plotStartDot} -> {plotEndDot})", color="white")
        # sets title
        ax.set_ylabel("Points", color="white")
        # adds Y-axis label

        ax.xaxis.set_major_formatter(MDates.DateFormatter("%b %d %H:%M"))
        # formats the X-axis timestamps to human readable format (Month XX HH:MM)
        ax.tick_params(axis="x", rotation=15, colors="white")
        # makes the X-axis ticks slanted and white

        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        # formats the Y-axis points to use thousand-separation (1,000)
        ax.tick_params(axis="y", colors="white")
        # makes the Y-axis ticks white

        ax.grid(True, color="gray", linestyle="--", alpha=0.3)
        # adds a semi-transparent grid

        self.chartCanvas.draw()
        # draws the chart
    


### Swap Charts ###

    def chartSwapper(self, action:str):
        """Function to swap between charts"""

        self.modifiers = QApplication.keyboardModifiers()
        # gets keyboard modifiers
        self.reverseSwap = self.modifiers & Qt.KeyboardModifier.ShiftModifier
        # reverses chart swapping if Shift is held down when pressing

        if action == "Swap":
        # actual swap, not just re-calling draw
            if self.reverseSwap:
            # if shift is held
                self.activeChart -= 1
                # removes 1 from the active
            else:
            # if shift isn't held
                self.activeChart += 1
                # adds 1 instead

            self.activeChart %= 3
            # wraps back to 0 if it hits 3
            self.chartView = 0
            # resets the chart view to 0

        if self.activeChart == 0:
        # if the active chart is 0
            self.statsCharter()
            # calls the W/L stats charter

        elif self.activeChart == 1:
        # if the active chart is 1
            self.pointsCharter()
            # calls the point gain charter

        elif self.activeChart == 2:
        # if the active chart is 2
            self.pointsPerChannel(self.currentChannel)
            # calls the points per channel charter with the active channel



### Chart Dots Counter ###

    def chartDotsCount(self, dataFrame: Pandas.DataFrame):
        """Function to calculate the pages available for a given dataframe"""
  
        chartEndPoint = self.chartView + self.chartViewDots
        # adds up the current view position and the total dots per page to get where the view should end
        return dataFrame.iloc[self.chartView:chartEndPoint]
        # returns the position the dataframe should display data to



### Chart Moving L -> R -> ###

    def chartMover(self, direction: int):
        """Function to move the chart(s) left to right to display more data"""

        newChartView = self.chartView + (direction * self.chartViewDots)
        # gets the new view dots position (eg. view = 0 -> 0 + (1 * 25) = 25)
        maxChartView = max(0, len(self.pointGains) - self.chartViewDots)
        # gets the max starting point (doesn't let it go below 0)
        self.chartView = max(0, min(newChartView, maxChartView))
        # sets the new starting point (caps it between 0 and the max dots (25))
        self.chartSwapper("A")
        # refreshes charts (bypasses the swapping)



### Quit ###

    def closeEvent(self, event):
        """pyQt method to trigger a stop when exiting"""
        self.running = False
        # stops run

        histWindowApp.quit()
        # quits the app

        event.accept()
        # accepts the exit event from Windows



### Starter Startup ###

histWindowApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
displayWindow = asyncHistWindow()
# creates a window reference

histWindowApp.exec()
# exceutes the app task (runs the QApplication)