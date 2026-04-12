Twitch Exact Point Grab (TEPG) is a tool to get your current channel points for any and all channels desired.

Runs through the Twitch GraphQL to grab the points balance.
Uses the same method to optionally get streak counts.

Login is handled by a QWebEngineView (a built-in browser that's used to store the login information in storage)
This way there's no need to re-authenticate every time, rather, Twitch handles the authentication itself

All the information is pushed into a CSV file for easy exporting for a more "user-friendly" viewing experience



So, why?

Well, for one, this can show channel points on channels where it's visually disabled
Mainly, though, if you're like me and have a love for numbers, why not?