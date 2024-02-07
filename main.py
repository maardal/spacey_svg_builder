#!/usr/bin/env python

# This script is used to build a SVG from a csv list of names.
# The svg will be a square of size x,y, and the names will be placed
# sequntially row by row.
# 
# |----------------x
# |creatin msvosch x
# |jon stranger    x
# |verylongnameeee x
# |----------------x
# 
# The font-family has to be monospaced, i.e. where alle characters
# have the same length.

import math
import csv
from xml.etree import ElementTree as et

#Helper classes
#Class for visual representation of a viewer's name in a list
class Viewer:
        def __init__(self, name, color, role):
                self.name = name.upper()
                self.color = color
                self.role = role
                self.x = 0
                self.y = 0

#Class to more easily increase the size of the produced SVG.
class Size:     
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


#variables for setting the size of elements and SVG.
baseFontSize = 16
baseFontCharLength = 10
baseCharHeightOffset = baseFontSize + math.floor((baseFontSize / 10))
baseCharLengthOffset = 0
baseImageWidth = 800
svgHeight = 0 #svgHeight is determined by the amount of names. 

size = Size(baseFontSize, baseFontCharLength, baseCharHeightOffset, baseCharLengthOffset, baseImageWidth)
size.multiply(2)


# importing the list of viewers
viewers=[]

with open('viewers.csv', newline="") as csvfile:
        viewer_list = csv.reader(csvfile, delimiter=',', quotechar='|')
        for name, color, nickname, role in viewer_list:
            if name != "":
                viewers.append(Viewer(nickname.strip() if nickname != "" else name.strip()
                                      , color.strip()
                                      , role.strip().lower()))


""" 
    We want the names to fill a row as best possible, without overflowing
    the max width of the svg. If a name will overflow the max width we
    will not add that to the list of sorted viewers, but rather hold off
    and check if the next names fit. 

    the loop adds a x value and a y value to a viewer. x relates to a
    names starting position in the svg in the horizontal direction.
    y is the end position in the vertical direction.
"""

sorted_list = []
temp_remove_array=[]
temp_max_x = size.svgWidth
temp_x = 0

while len(viewers) > 0:
    for j in range(0, len(viewers)):
            if temp_max_x == 0:
                break

            temp_viewer = viewers[j]
            calulatedNamePixelLength = math.ceil(len(temp_viewer.name) * size.charLength) + size.charLenghtOffset
            if temp_viewer.role == "vip" or temp_viewer.role == "mod":
                  calulatedNamePixelLength += size.roleIconWidth
            
            if calulatedNamePixelLength <= temp_max_x:
                temp_viewer.x = temp_x
                temp_viewer.y = svgHeight
                temp_x = temp_x + calulatedNamePixelLength

                sorted_list.append(temp_viewer)
                temp_remove_array.append(j)

                temp_max_x = temp_max_x - calulatedNamePixelLength

    temp_remove_array_copy = temp_remove_array.copy()
    temp_remove_array_copy.reverse()

    for viewer_list_index in temp_remove_array_copy:
        viewers.pop(viewer_list_index)

    temp_remove_array.clear()
    temp_max_x = size.svgWidth
    temp_x = 0
    svgHeight += size.charHeightOffset

# build the svg.
svg = et.Element('svg', width=str(size.svgWidth), height=str(svgHeight + 10), version='1.1', xmlns='http://www.w3.org/2000/svg', viewBox=f'0 -{size.fontSize} {size.svgWidth} {svgHeight}')


for viewer in sorted_list:
      viewer_x_position = viewer.x
      if viewer.role.lower() == "vip":
            svg.append(et.Element('image', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(size.roleIconWidth), height=str(size.roleIconHeight), href="badges/diamond.svg"))
            viewer_x_position += size.roleIconWidth
      if viewer.role.lower() == "mod":
            svg.append(et.Element('image', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(size.roleIconWidth), height=str(size.roleIconHeight), href="badges/sword.svg"))
            viewer_x_position += size.roleIconWidth
      text = et.Element("text", x=str(viewer_x_position), y=str(viewer.y), fill=str(viewer.color), style=f'font-family:Consolas; font-size:{size.fontSize}px')
      text.text = viewer.name
      svg.append(text)

#open file and save
f = open("sample.svg", "wb")
f.write(et.tostring(svg))
f.close()