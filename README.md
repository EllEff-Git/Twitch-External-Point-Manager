## Twitch External Point Manager *(TEPM)* 
### A Python program to view and manage channel points for any and all channels desired.

<br>

### Current features: 
- Get channel point balance, streaks or both for any single or list of channels (includes channels where otherwise disabled)
- View and place predictions
- Predictions feature a configurable default bet, a max bet, several keybinds and more detailed stats
- Stores prediction results to file, displays them in 3 separate chart forms (bar chart for gains, line chart for per-channel historical balance, pie chart for Win/Loss ratio and total stats)
- Automatic betting via configurable outcome selection (independent of prediction view, place bets in 2 places at once!)


### "Planned" features: (concept exists, definitely possible - figuring out how/if there's use)
- A further detail view of predictions (more in-depth point tracking, top predictors... basically everything Twitch gives in GQL)
- A mod view to manage predictions (start, lock, pay out and delete predictions for a channel with moderator status)

<br>

## Download
### [Download latest](https://github.com/EllEff-Git/Twitch-External-Point-Manager/releases/latest/download/TEPM.zip)

<br>

## Basic Info

#### Runs through the Twitch GraphQL to grab points, streaks and to handle predictions <br>

#### Login is handled by a QWebEngine (a built-in browser that's used to store the login locally) <br>

#### All the channel points information is pushed into a CSV file for easy exporting for a more "user-friendly" viewing experience

#### Streak information is saved into a json file to keep track of their 'activity' and to store the channel IDs to reduce requests later on

#### Predictions are stored into a json file, where they are automatically graphed from with the history view

<br>

## Preview

*Please note some of these pictures may be from earlier/test builds, final appearance depends on version!* <br/>

Prediction View: <br/>
![Imgur Image](https://i.imgur.com/okapqsp.png)

Prediction History: <br/>
![Imgur Image](https://i.imgur.com/1KSV8oL.png)

Auto-Bet View: <br/>
![Imgur Image](https://i.imgur.com/j4Fd9h4.png)

Point/Streak View: <br/>
![Imgur Image](https://i.imgur.com/GslP0sR.png)

<br>

## So, why?

- Very first world problem, but I just really hate the default Twitch prediction screen/chat view
##### Especially with the new UI "updates", I can't see my points when I try to bet, and occasionally the predictions don't even load right away (if at all...) <br>

- Predicting with TEPM is not only more detailed, but is also faster and isn't really subject to having the predictions not appear
##### Since this program only targets specific network requests, and skips things like loading the stream itself, it can load the requested information quicker - swapping between streams in the prediction view is considerably faster than native Twitch <br>

- Accessing any view with this program doesn't count as presence in the stream, so you can keep earning points elsewhere
##### Very good for Drops, too, since presence in multiple streams can mess with Drops progression (the browser view *may* count as presence, since it does load the full view, but streams are unrendered, so I'm unsure. Wouldn't recommend sitting there, regardless) <br>

- Mainly, though, if you're like me and enjoy endless numbers wherever possible, why not?
##### *Do note that since this program does not count as "presence in chat", you won't earn any points or drops leaving this on!*

<br>

## How to use?

#### 0. Download the latest release .zip and unzip it to a location of your choosing

#### 1. Start the program to create all necessary files
* The first time, it'll prompt you for configuration options, after that you can manually access these at will

#### 2. Pick a task
* If you're ever confused, try hovering over things - I've tried making everything as easy to understand as possible, but sometimes it's hard to get my point across, so there's a lot of hover tooltips with more info

#### 3. Login to Twitch inside the browser view
* Login isn't sent anywhere, only stored locally, data is only ever passed between you and Twitch :)

#### 4. Explore other tasks!
* If you want to check channel points/streaks, you'll need to add the channel(s) into the Channel List.txt file (1x per line, no special characters, commas, nothing (it's not case sensitive, but make sure you nail the underscores and such))
* Just save the file and select any of the point/streak options
* You can predict without any file modification, just write a streamer's name and hit enter to be greeted with a prediction view!

<br>

<br>

## Issues, feedback, suggestions?

#### Send me a DM on Discord (LilPiffer) or make a GitHub issue :)