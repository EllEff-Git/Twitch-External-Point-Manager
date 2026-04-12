import os, sys, requests, datetime, json, time
# Required program management
import pandas as pnd
# Soft required for CSV management (not required, but improves formatting)
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWidgets import *
# PyQt is the application/window framework (UI for the whole app)


tepgVer = "0.4.12.2246"
"""TEPG program version (Y.MM.DD.HHMM)"""


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    """The base directory of the program, where tepg.exe resides"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    """The base directory of the program, where tepg.exe resides"""


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


if not os.path.exists(profilePath):
# checks if the profile folder path is(n't) valid yet
    print("No Profile folder found, creating one!")
    # user inform
    os.mkdir(profilePath)
    # makes a directory at the given path


if not os.path.exists(textPath):
# checks if the channel list.txt file exists yet
    print("No Channel List text file found, creating one!")
    # user inform
    with open(textPath, "w") as clnt:
    # opens the text path location (makes a new file)
        clnt.write("Twitch")
        # writes just Twitch as the only channel


def folders(path):
    """Function to check subfolder existence"""
    for folder in os.listdir(path):
        # goes through each folder in the given path
        if os.path.isdir(os.path.join(path, folder)):
            # if the directory is real
            yield os.path.join(path, folder)
            # joins and goes to next


subfolders = list(folders(profilePath))
# stores the subfolders of the profile path (installation/Profile/)


if subfolders and len(subfolders) == 1:
    # checks if there's a subfolder inside the Profile (whether an actual user profile exists or not)
    profileFolder = subfolders[0]
    # grabs the only subfolder
    head, tail = os.path.split(profileFolder)
    # splits the path of the folder into head (everything before last /) and tail (the last part)
    profileName = tail
    # sets the profile name to match the folder name
elif len(subfolders) > 1:
    # if there's more than 1 profile folder
    print("Found multiple folders inside the TEPG/Profile/ folder - ensure only one user profile folder is present and retry")
    time.sleep(300)
    # waits 5 min (ensure user sees)
    raise SystemExit
    # exit
else:
    # if there's no profile subfolder yet
    chooseUser = input("No profile configured, please enter a new profile name: ")
    # prompts user to pick a name
    if not chooseUser: # need to also make it check for stuff like it's only A-Z/a-z I think? I guess it could also have numbers? Anything the folder can conform to, I think?
    # if user fails to give one
        print("No valid name given, setting profile to default")
        # user inform
        profileName = "Default"
        # sets to Default
    else:
    # if user provides a name
        print(f"Setting profile name to {chooseUser}")
        # user inform
        profileName = chooseUser
        # stores the profile name as the chosen name


if os.path.exists(clientIDPath):
# if the client ID file exists
    with open(clientIDPath, "r") as clnt:
    # opens the client id text file
        clientIDraw = clnt.readline()
        # reads the line
        trash, clientID = clientIDraw.split("= ")
        # splits by = sign
        clientID = clientID.strip()
        # ensures no whitespace
else:
# if the file doesn't exist
    clientID = input("Please enter a Twitch Client ID: ")
    # takes the client ID from user input
    with open(clientIDPath, "w") as clnt:
    # opens the client ID location (makes a new file)
        clnt.write(f"Client ID = {clientID}")
        # writes the client ID string to file


if os.path.exists(streakMapPath):
# if the client ID file exists
    with open(streakMapPath, "r") as strk:
    # opens the client id text file
        streakMap = json.load(strk)
        # loads the json map into variable
    enableStreaks = streakMap["enableStreaks"]
    # grabs the boolean from the map
else:
# if the file doesn't exist
    streakMap = {
        "enableStreaks": False,
        "exampleChannel": "exampleChannelID"
    }
    # creates a default map
    enableStreaks = False
    # sets the boolean to false
    with open(streakMapPath, "w") as strk:
    # opens the client ID location (makes a new file)
        json.dump(streakMap, strk, indent=3)
        # dumps the map into file


reqSession = requests.Session()
"""A request session that stores cached request information"""


os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = f"--user-data-dir={profilePath} --profile-directory={profileName} --enable-widevine --enable-gpu --enable-hls --disable-webgpu"
# environment flags for the chromium webengine (directory stuff, ensures hardware acceleration is on)



class tepgWindow(QMainWindow):
    """The application window class"""

    authValid = pyqtSignal(bool)
    # creates a bool signal to check if the authentication code is ready
    taskText = pyqtSignal(str)
    # creates a string signal to set the task view to

    def __init__(self, state):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

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
        self.channels = self.getChannelList()
        # stores the channels
        self.channelLength = len(self.channels)
        # stores the length of the channels list

        self.authToken = None
        # the auth token

        self.mainIcon = "icon.png"
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

        self.taskView = QLineEdit()
        # creates a line edit text field for the task progress
        self.taskView.setReadOnly(True)
        # sets to read only (user can't write)
        self.taskView.setText("Opening browser view...")
        # initial value
        self.taskView.setFixedSize(QSize(int(self.windowSizeX / 4), 25))
        # sets a fixed size (1/4th the window width, 25 px tall)
        self.taskView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns to the center
        self.mainLayout.addWidget(self.taskView, 0,0,1,1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

    ### Browser ###

        self.browserProfile = QWebEngineProfile(self.profileName, self)
        # sets the browser profile to the given profile (default is Default)
        self.browserProfile.setCachePath(os.path.join(self.profilePath, self.profileName))
        # sets the cache path ()
        self.browserPage = QWebEnginePage(self.browserProfile, self.browserView)
        # browserProfile.setPersistentStoragePath("S:/Profile/Local State")
        self.browserView.setPage(self.browserPage)
        # sets the page to use the given properties
        self.browserView.setFixedSize(self.windowSizeX - 20, self.windowSizeY - 45)
        # caps the browser to be half the window size

        self.settings = self.browserProfile.settings()
        # manages the browser settings
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        # ensures local storage is enabled 
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        # allows plugins to function
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # ensures javascript is enabled

        self.mainLayout.addWidget(self.browserView, 1, 0, 1, 1)
        # adds the browser to the layout
        self.browserView.setUrl(QUrl(self.defaultURL))
        # sets "default" url to open (twitch.tv)

        self.browserView.loadFinished.connect(self.extractAuthToken)
        # calls the auth grab when the page is done loading
        self.authValid.connect(self.uiStyle)
        # calls uistyle when the authvalid is set to True
        self.taskText.connect(self.manageTooltip)
        # calls manageTooltip when the task text changes


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
        self.channelLabel.setText("Starting point grabber...")
        # sets initial text
        self.channelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.totalLabel = QLabel()
        self.totalLabel.setText("No points found yet")
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

        channel = progressDict["channel"]
        # the channel name (str)
        index = progressDict["index"]
        # the channel's position in the list (0:X)
        points = progressDict["points"]
        # point count (int)
        error = progressDict["error"]
        # boolean for whether an error occurred
        total = progressDict["total"]
        # the total points so far
        streaks = progressDict["streaks"]
        # whether this channel's streak is enabled
        streak = progressDict["streak"]
        # the current channel's streak
        # grabs all the relevant information from the passed dictionary

        percentage = int(((index + 1) / self.channelLength ) * 100)
        # calculates the current percentage (index+1 out of the total = 0-1 * 100 = percentage)

        self.progressBar.setValue(percentage)
        # sets the progress bar value

        pointString = f"{points:,} points"
        # formats the number to use formatting (no decimals, thousand comma)

        totalString = f"Points across channels: {total:,}"
        # formats the total number

        if error:
        # if there's an error reported
            self.channelLabel.setText(f"Error with {channel}, couldn't get points")
            # sets an error text
        else:
            if streaks:
            # if the streaks are enabled for this channel
                self.channelLabel.setText(f"{pointString} and a streak of {streak} found for {channel}")
                # sets the text to match
            else:
                self.channelLabel.setText(f"{pointString} found for {channel}!")
                # sets the text to match

        self.totalLabel.setText(f"{totalString}")
        # sets the total string to match

        self.currentLabel.setText(f"{(index + 1)} / {self.channelLength}")
        # sets the current channel index string

    def progressDone(self, errors: int, streak: int):
        """A function to change the headless UI into completion mode"""
        preFinalText = self.totalLabel.text()
        # gets the text from the label 
        if enableStreaks:
        # if streaks are enabled
            self.totalLabel.setText(f"{preFinalText} - highest streak: {streak}")
            # makes the total label state the max streak as well
        self.channelLabel.setText(f"All channels scoured - points have been saved to CSV!\n\nTEPG was unable to store points for {errors} out of {len(self.channels)} channels\n\nFeel free to exit, thank you for using TEPG <3\n")
        # final UI update
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

    def uiStyle(self, auth: bool):
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

    def extractAuthToken(self, done=None):
        """Function to get the auth token from storage"""

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
                None
        except:
        # if the channel check fails
            None


    ### Channel Lister ###

    def getChannelList(self) -> list:
        """The function to grab the list of channels"""
        self.channels = []
        # clears the list

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
                return {"success": True, "points": points["balance"]}
                # returns a dictionary with success

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "User likely banned"}
            # returns a dictionary with failure

    except Exception as dtErr:
    # saves the error as d(a)t(a)Err(or)
        return {"success": False, "error": f"{str(dtErr)}"}
        # returns a dictionary with failure


### Streak Grabber ###

def streakGrabber(state, channel: str, channelID: str):
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
    
    payload = {
    # forms a payload from the required information
        "operationName": "RewardList",
        "variables": {
            "channelLogin": channel,
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
            try:
                return {"success": True, "streak": streak["value"]}
                # returns a dictionary with success

            except Exception as twErr:
            # saves the error as tw(itch)Err(or)
                return {"success": False, "error": f"{str(twErr)}"}
                # returns a dictionary with failure
        else:
        # if the data package isn't valid and/or there's no data header
            return {"success": False, "error": "User likely banned"}
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



### Channel/Point Manager ###

class PointWorker(QObject):
    # signals to communicate with UI
    progress = pyqtSignal(dict)
    # stores the percentage, channel name and points inside a pyqt singal, to update UI
    finished = pyqtSignal(int, int)
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
        self.enableStreaks = enableStreaks
        # the boolean to determine whether to grab streaks or not

    @pyqtSlot()
    def run(self):
    # runs the point worker

        csvEntries = {}
        # creates a new map to place each channel into

        self.progressDict = {}
        # empty dictionary, filled per loop, sent to UI

        self.totalPoints = 0
        # stores the total amount of points gathered

        self.errorCount = 0
        # starts a counter for errors (how many channels couldn't be saved)

        self.maxStreak = 0
        # starts a maximum streak store

        for num, channel in enumerate(self.channels):
        # goes through each channel in the list (gets channel and index)

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

            self.totalPoints = (self.totalPoints + foundPoints)
            # adds the channel's points to the total amount

            if enableStreaks and channel in streakMap:
            # if the streak-grabbing is enabled

                QThread.msleep(1000)
                # sleeps for a second (avoids limiting)
                
                channelID = int(streakMap[channel])
                # gets the channel ID from the streak map

                streak = streakGrabber(self.state, channel, str(channelID))
                # calls the streak grabber to get the streak

                if streak["success"]:
                # if the streak success entry is true
                    streakNum = int(streak["streak"])
                    # gets the streak
                else:
                # if the streak entry is false
                    streakNum = 0
                    # sets to default of 0

                if streakNum > self.maxStreak:
                # if the current streak is larger than the stored max streak
                    self.maxStreak = streakNum
                    # reassigns the max streak to match

                csvEntries[channel] = {
                    "points": foundPoints,
                    "streak": streakNum
                }
                # stores the points and streak in the channel's csv entry

                self.progressDict = {
                    "channel": channel,
                    "index": num,
                    "points": foundPoints,
                    "error": errorBool,
                    "total": self.totalPoints,
                    "streaks": True,
                    "streak": streakNum 
                }
                # forms a progress dictionary to pass

            else:
            # if the streak-grabbing is disabled
                csvEntries[channel] = {
                    "points": foundPoints,
                    "streak": 0
                }
                # stores the points in the channel's csv entry

                self.progressDict = {
                    "channel": channel,
                    "index": num,
                    "points": foundPoints,
                    "error": errorBool,
                    "total": self.totalPoints,
                    "streaks": False,
                    "streak": 0 
                }
                # forms a progress dictionary to pass

            self.progress.emit(self.progressDict)
            # sends the progress update to the headless UI updater

            QThread.msleep(1500)
            # waits 1.5s/channel
        
        self.csvWriter(csvEntries, self.errorCount, self.maxStreak)
        # calls the csvWriter with the formed map (dictionary) and the number of errors (gets passed to finished UI)


    ### CSV Writer ###

    def csvWriter(self, csvEntries: dict, errors: int, streak: int):
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
                "Points": int(values["points"]),
                # stores the points
                "Streak": int(values["streak"]),
                # stores the streak
                "Timestamp": timestamp
                # stores the timestamp (can be used to calculate points/timeframe later)
            })
            # adds the given parameters to a new row

        dataframe = pnd.DataFrame(rows)
        # forms a dataframe from the formed rows

        dataframe.to_csv(self.csvPath, index=False)
        # pushes everything to the csv file
        
        self.finished.emit(errors, streak)
        # once done, sends a signal to the finished pyqt signal with the error count
            


### Startup ###

app = QApplication(sys.argv)
# base app instance (passes command line arguments)
appState = AppState()
# creates an app state instance to store some variables
window = tepgWindow(appState)
# creates a window
app.exec()
# exceutes the app task (runs the QApplication)