## Twitch External Point Manager *(TEPM)* 
### A Python program to view and manage channel points for any and all channels desired.

<br>

### Current features: 
- Get channel point balance, streaks or both for any channel (or a list of channels)
- View prediction details for a single channel
- Place bets on predictions 
- Predictions feature a configurable default bet, max bet, keybinds and more detailed stats than Twitch

### Planned features:
- A further detail view of predictions (more in-depth point tracking, top predictors, spread visualisation)
- Saving own bet data to file (to see trends of win/loss / point accumulation over time)
- A mod view to manage predictions (start, lock, pay out and delete)

<br>

## Download
### [Download latest](https://github.com/EllEff-Git/Twitch-External-Point-Manager/releases/latest/download/TEPM.zip)

<br>

## Basic Info

#### Runs through the Twitch GraphQL to grab the points balance, streaks and to even handle predictions <br>

#### Login is handled by a QWebEngineView (a built-in browser that's used to store the login locally) <br>

#### All the point/streak information is pushed into a CSV file for easy exporting for a more "user-friendly" viewing experience

<br>

## So, why?

- Very first world problem, but I just really hate the default Twitch prediction screen/chat view
##### Especially with the new UI updates, I can't see my points when I try to bet and sometimes the predictions don't even load right away... <br>

- Predicting with TEPM is not only more detailed, but is also faster and isn't subject to having the predictions not appear <br>

- This program can also show channel points on channels where they're otherwise disabled <br>

- Participating in predictions with this program doesn't count as presence in the stream, so you can keep earning points elsewhere
##### Very good for Drops, too, since presence in multiple streams can mess with Drops progression <br>

- Mainly, though, if you're like me and enjoy endless numbers wherever possible, why not?
##### *Do note that since this program does not count as "presence in chat", you won't earn any points or drops leaving this on!*

<br>

## How to use?

#### 1. Start the program to create all necessary files and folders

#### 2. Pick a task

#### 3. Login to Twitch inside the browser view

#### 4. Explore other tasks!
* If you want to check channel points, you'll need to add the channel(s) into the Channel List.txt file (1x per line, no special characters, commas, nothing (it's not case sensitive, but make sure you nail the underscores and such))
* Just save the file and select any of the point/streak options
* You can predict without any file modification, just write a streamer's name and hit enter to be greeted with a prediction view!
#### 5. That's it. There's a small config to tweak things, but otherwise it's just that simple.

<br>

<br>

## Issues, feedback, suggestions?

#### Send me a DM on Discord or make a GitHub issue :)
##### You can find my Discord by going to [My Website](https://elleffnotelf.com/guides/discord-spotify-integration/) and scrolling all the way to the bottom