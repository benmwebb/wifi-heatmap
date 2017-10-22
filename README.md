This is a very basic tool for collecting samples of wifi signal strength
in an area such as a house, and then making simple heatmap plots. I wrote it
for my own use to place wifi access points in my house; it's here in the hope
that somebody else will find it useful.

# Operating system

This software currently works only on a Mac, but could probably be made to
work on other operating systems by replacing the `AirportQuery` class with
an equivalent that calls a suitable wifi-querying command line tool.

# Dependencies

You'll need Python 3, Qt 5, scipy, matplotlib. One way to get these is to
install [brew](https://brew.sh) then `brew install python3 pyqt` and
`pip3 install matplotlib`.

# Installation

No installation is necessary - just run the `wifi-heatmap.py` program directly -
but you can certainly copy it into `/usr/bin` or similar.

# Usage

 - Use "File/Open Floor Plan..." to load a plan of the area you want to survey,
   which can be a hand-drawn image (to scale is best), or (ideally) blueprints
   or architect's plans. Most common image formats will work, although you
   may want to rescale the image to a manageable size). 
 - Click on the floor plan corresponding to where you physically are in your
   house. This will sample all of the wifi networks (this will take a few
   seconds) and record them on the plan. Walk around the house and take a number
   of such samples.
 - Use "View/Show Heatmap", and select the wifi network you're interested in,
   to get a heatmap of the signal strength over the entire floor area.
 - You can also save the current survey to a simple CSV file.

# Issues

 - Only single surveys are currently supported. If you want to survey a new
   area, restart the program and load in a new floor plan.
 - No undo (although you can edit the CSV file to remove one or more points).
