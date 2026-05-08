## Twitch External Point Manager *(TEPM)* 
### A lightweight Python program to view and manage channel points for any and all channels desired.


### Runs through the Twitch GraphQL to grab the points balance, streaks and to even handle predictions <br>


#### Login is handled by a QWebEngineView (a built-in browser that's used to store the login locally) <br>
##### This way there's no need to re-authenticate every time, rather, Twitch handles the authentication itself


#### All the information is pushed into a CSV file for easy exporting for a more "user-friendly" viewing experience

<br>

### So, why?

#### Very first world problem, but I just really hate the default Twitch prediction screen/chat view
#### This program can also show channel points on channels where they're otherwise disabled
#### Mainly, though, if you're like me and enjoy endless numbers, why not?

<br>

### How to use?

#### 1. Run the program once to create all necessary files and folders
#### 2. When prompted, enter your Twitch Client ID
* This can be found by:
    * -> Browser console (F12 or right click -> "inspect") 
    * -> "Network" tab
    * -> type "GQL" in the filter field
    * -> Click any request 
    * -> "Headers"
    * Find "Client-Id" and copy it
#### 3. Login to Twitch inside the built-in browser view

#### 4. Select a task to perform
* If you want to check channel points, you'll need to first add the channels into the Channel List.txt file (1x per line, no special characters)
* After that, save the text file and restart TEPM
#### 5. That's it. There's a small config to tweak things, but otherwise it's just that simple.