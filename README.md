## Twitch Exact Point Grab *(TEPG)* 
### A lightweight Python program to get your current channel points for any and all channels desired.


#### Runs through the Twitch GraphQL to grab the points balance <br>
##### Uses the same method to (optionally) get streaks



#### Login is handled by a QWebEngineView (a built-in browser that's used to store the login information in storage) <br>
##### This way there's no need to re-authenticate every time, rather, Twitch handles the authentication itself



#### All the information is pushed into a CSV file for easy exporting for a more "user-friendly" viewing experience

<br>

### So, why?

#### Well, for one, this can show channel points on channels where it's visually disabled
#### Mainly, though, if you're like me and have a love for numbers, why not?

<br>

### How to use?

#### Run the program once to create all necessary files and folders
#### When prompted, enter your Twitch Client ID
* This can be found by:
    * -> Browser console (F12 or right click -> "inspect") 
    * -> "Network" tab
    * -> type "GQL" in the filter field
    * -> Click any request 
    * -> "Headers"
    * Find "Client-Id" and copy the long string
#### Login to Twitch in the built-in browser view
#### Close TEPG
#### Add desired channels into the Channel List.txt file (one per line, not case sensitive, must match name grammatically)
#### Configure via the starter UI that pops up every run
##### Can be used to disable streak-checking and can be set to automatically capture >1 streaks to the streak list for later checking