# i3 Colour Changer
The i3 Colour changer applet was created after frustration with editing i3 config files. Copying and pasting hex color codes are annoying and remembering where to put them is a chore. In i3 Colour changer you can load you existing config file and edit the colours to you liking. Hit apply to try out new changes without having to swap config files and click save once you are happy with the result (your actual config won't change until you do).
## Features
1. Easy colour selections for *all* colours in the i3 config, including i3bar
2. Try out changes before saving your config
3. Open other config files and try them out to see if you like them
4. Save colour configs to snippets which can be shared and applied by others without having to tamper with their other settings

## Dependencies
This program is written in Python 3 by using the wxPython Phoenix project for GUI. Other packages which must be installed includes:
1. colour
2. i3ipc
3. math
4. os