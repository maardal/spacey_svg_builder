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
import sys
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
                
class Size:
        
        iconWidth = 12
        iconHeight = 10

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

try:
    with open('viewers_sheets_data.exe', newline="") as csvfile:
            viewer_list = csv.reader(csvfile, delimiter=',', quotechar='|')
            for name, color, nickname, role in viewer_list:
                if name != "":
                    viewers.append(Viewer(nickname.strip() if nickname != "" else name.strip()
                                          , color.strip()
                                          , role.strip().lower()))
except FileNotFoundError as error:
      print(error.__class__)                    #REMOVE LATER
      print(error)                              #REMOVE LATER
      SystemExit("Please provide a file.")      #CHANGE TO INCLUDE SUPPLIED PATH/FILE NAME
except OSError as error:
      print(error.__class__)
      print(error)
      SystemExit("Could not open and/or read file. File must be csv file in the supported format. See https://github.com/maardal/spacey_svg_builder")
except Exception as execption:
      print(execption.__class__)
      SystemExit("Unexpected error. Report error at https://github.com/maardal/spacey_svg_builder")
finally:
      csvfile.close()

# Base sizes of elements and SVG.

monospacedFont = "Consolas"
baseFontSize = 16
baseFontCharLength = 10
baseCharHeightOffset = baseFontSize + math.floor((baseFontSize / 10))
baseCharLengthOffset = 0
baseImageWidth = 800
svgHeight = 0 #svgHeight is determined by the amount of names. 

# Resize svg

size = Size(baseFontSize, baseFontCharLength, baseCharHeightOffset, baseCharLengthOffset, baseImageWidth)
multiplicationFactor = 2
size.multiply(multiplicationFactor)

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

defs = et.Element('defs')

iconWidth = Size.iconWidth * multiplicationFactor
iconHeight = Size.iconHeight * multiplicationFactor

## vip_badge_coordinates - a diamond          
diamond_left_middle = f'{0} {iconHeight * 0.26}'
diamond_left_top = f'{iconWidth * 0.1875} {0}'
diamond_right_top = f'{iconWidth * 0.8125} {0}'
diamond_right_middle = f'{iconWidth} {iconHeight * 0.26}'
diamond_bottom_tip = f'{iconWidth/2} {iconHeight}'

vip_pattern_definition = et.SubElement(defs, "pattern", id="vip_badge", x="0", y="0", width=str(iconWidth), height=str(iconHeight), patternUnits="objectBoundingBox")
vip_pattern_geometry = et.SubElement(vip_pattern_definition, "polygon", fill="#fb0493", points=f'{diamond_left_middle}, {diamond_left_top}, {diamond_right_top}, {diamond_right_middle}, {diamond_bottom_tip}')

## mod_badge_coordinates - a sword                
grip_bottom_left = f'{0} {iconHeight * 0.875}'
grip_upper_left = f'{iconWidth * 0.125} {iconHeight * 0.6875}'
guard_bottom_left = f'{0} {iconHeight * 0.5625}'
guard_upper_left = f'{iconWidth * 0.125} {iconHeight * 0.4375}'
blade_base_left = f'{iconWidth * 0.275} {iconHeight * 0.55}'
blade_point_left = f'{iconWidth * 0.75} {0}'
blade_point_middle = f'{iconWidth} {0}'
blade_point_right = f'{iconWidth} {iconHeight * 0.25}'
blade_base_right = f'{iconWidth * 0.4375} {iconHeight * 0.6875}'
guard_upper_right = f'{iconWidth * 0.625} {iconHeight * 0.875}'
guard_bottom_right = f'{iconWidth * 0.5} {iconHeight}'
grip_upper_right = f'{iconWidth * 0.275} {iconHeight * 0.875}'
grip_bottom_right = f'{iconWidth * 0.125} {iconHeight}'

mod_pattern_definition = et.SubElement(defs, "pattern", id="mod_badge", x="0", y="0", width=str(iconWidth), height=str(iconHeight), patternUnits="objectBoundingBox")
mod_pattern_geometry = et.SubElement(mod_pattern_definition, "polygon", fill="#14cb04", points=f'{grip_bottom_left}, {grip_upper_left}, {guard_bottom_left}, {guard_upper_left}, {blade_base_left}, {blade_point_left}, {blade_point_middle}, {blade_point_right}, {blade_base_right}, {guard_upper_right}, {guard_bottom_right}, {grip_upper_right}, {grip_bottom_right}')

svg.append(defs)

## Place names in svg based on coordinates.

for viewer in sorted_list:
      viewer_x_position = viewer.x

      if viewer.role.lower() == "vip":
            svg.append(et.Element('rect', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(iconWidth), height=str(iconHeight), fill="url(#vip_badge)"))
            viewer_x_position += size.roleIconWidth

      if viewer.role.lower() == "mod":
            svg.append(et.Element('rect', x=str(viewer_x_position), y=str(viewer.y - 20), width=str(iconWidth), height=str(iconHeight), fill="url(#mod_badge)"))
            viewer_x_position += size.roleIconWidth

      text = et.Element("text", x=str(viewer_x_position), y=str(viewer.y), fill=str(viewer.color), style=f'font-family:{monospacedFont}; font-size:{size.fontSize}px')
      text.text = viewer.displayName
      svg.append(text)

et.indent(svg, '  ')

currentDateTime = datetime.now().strftime("-%Y%m%d-%H%M%S")

f = open(f"sample{currentDateTime}.svg", "wb")
f.write(et.tostring(svg))
f.close()