#!/usr/bin/env python

# This script is used to build a SVG from a csv list of twitch usernames.
# The svg will be a square of size x,y, and the names will be placed
# sequntially row by row, illustrated as below.
# 
# |----------------x
# |creatin msvosch x
# |jon stranger    x
# |verylongnameeee x
# |----------------x
#
# csv must have username. Color, nickname, and role are optional.
# If no color set, the color of the name is defaulted to black.
# Colors can be given as a name or as a hex code. If given as a name, they must be a amongst the
# 140 supported by browsers. If not recognized, the color is defaulted to blakc.
# Nickname takes presedence over username if added.
# Roles supported are mod and vip. Usernames with mod get the mod sword beside their name,
# while usernames with vip get the vip diamond.
# 
# The font-family has to be monospaced, i.e. where alle characters
# have the same length.
#
# Script saves the files with a timestamp on the format yyyy-mm-dd-hr-mm-ss. 

import math
import csv
from datetime import datetime
from xml.etree import ElementTree as et

#Helper classes

## Class for visual representation of a viewer's name in a list.

class Viewer:
        def __init__(self, displayName, color, role):
                self.displayName = displayName.upper()
                self.color = color
                self.role = role
                self.x = 0
                self.y = 0

## Class to more easily increase the size of the produced SVG.
                
        def __init__(self, fontSize, charLength, charheightOffset, charLengthOffset, svgWidth):
            self.fontSize = fontSize
            self.charLength = charLength
            self.charHeightOffset = charheightOffset
            self.charLenghtOffset = charLengthOffset
            self.svgWidth = svgWidth
            self.roleIconWidth = 12
            self.roleIconHeight = 10

        def multiply(self, number):
            self.fontSize *= number
            self.charLength *= number
            self.charHeightOffset *= number
            self.charLenghtOffset *= number
            self.svgWidth *= number
            self.roleIconWidth *= number 
            self.roleIconHeight *= number


# Importing the list of viewers
            
viewers=[]

with open('viewers.csv', newline="") as csvfile:
        viewer_list = csv.reader(csvfile, delimiter=',', quotechar='|')
        for name, color, nickname, role in viewer_list:
            if name != "":
                viewers.append(Viewer(nickname.strip() if nickname != "" else name.strip()
                                      , color.strip()
                                      , role.strip().lower()))

# Base sizes of elements and SVG.

baseFontSize = 16
baseFontCharLength = 10
baseCharHeightOffset = baseFontSize + math.floor((baseFontSize / 10))
baseCharLengthOffset = 0
baseImageWidth = 800
svgHeight = 0 #svgHeight is determined by the amount of names. 

# Resize svg


# Calculate coordinates for names. Will not let names overflow the width of the svg.
# Also sorts list name, so spaces at the end of a line will be filled by the first possible name that is short enough.

sorted_list = []
temp_remove_array=[]
temp_max_x = size.svgWidth
temp_x = 0

while len(viewers) > 0:
    for j in range(0, len(viewers)):
            if temp_max_x == 0:
                break

            temp_viewer = viewers[j]
            calulatedPixelLengthName = math.ceil(len(temp_viewer.displayName) * size.charLength) + size.charLenghtOffset
            if temp_viewer.role == "vip" or temp_viewer.role == "mod":
                  calulatedPixelLengthName += size.roleIconWidth
            
            if calulatedPixelLengthName <= temp_max_x:
                temp_viewer.x = temp_x
                temp_viewer.y = svgHeight
                temp_x = temp_x + calulatedPixelLengthName

                sorted_list.append(temp_viewer)
                temp_remove_array.append(j)

                temp_max_x = temp_max_x - calulatedPixelLengthName

    temp_remove_array_copy = temp_remove_array.copy()
    temp_remove_array_copy.reverse()

    for viewer_list_index in temp_remove_array_copy:
        viewers.pop(viewer_list_index)

    temp_remove_array.clear()
    temp_max_x = size.svgWidth
    temp_x = 0
    svgHeight += size.charHeightOffset


# Build svg.
    
svg = et.Element('svg', width=str(size.svgWidth), height=str(svgHeight + 10), version='1.1', xmlns='http://www.w3.org/2000/svg', viewBox=f'0 -{size.fontSize} {size.svgWidth} {svgHeight}')


## Place names in svg based on coordinates.

for viewer in sorted_list:
      viewer_x_position = viewer.x
      if viewer.role.lower() == "vip":
            svg.append(et.Element('image', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(size.roleIconWidth), height=str(size.roleIconHeight), href="badges/diamond.svg"))
            viewer_x_position += size.roleIconWidth
      if viewer.role.lower() == "mod":
            svg.append(et.Element('image', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(size.roleIconWidth), height=str(size.roleIconHeight), href="badges/sword.svg"))
            viewer_x_position += size.roleIconWidth
      text.text = viewer.displayName
      svg.append(text)

currentDateTime = datetime.now().strftime("-%Y%m%d-%H%M%S")

f = open(f"sample{currentDateTime}.svg", "wb")
f.write(et.tostring(svg))
f.close()