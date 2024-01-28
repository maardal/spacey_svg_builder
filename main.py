""" 
This script is used to build a SVG from a list of names.
The svg will be a square of size x,y, and the names will be placed
sequntially row by row.

|----------------x
|creatin msvosch x
|jon stranger    x
|verylongnameeee x
|----------------x

The font-family has to be monospaced, i.e. where alle characters
have the same length.
"""
import math
import csv
from xml.etree import ElementTree as et

class Viewer:
        def __init__(self, name, color, role):
                self.name = name.upper()
                self.color = color
                self.role = role
                self.x = 0
                self.y = 0

class Proportions:     
        def __init__(self, fontSize, charLength, charheightOffset, charLengthOffset, svgWidth, svgHeight):
              self.fontSize = fontSize
              self.charLength = charLength
              self.charHeightOffset = charheightOffset
              self.charLenghtOffset = charLengthOffset
              self.svgWidth = svgWidth
              self.svgHeight = svgHeight

        def multiply(self, number):
            self.fontSize *= number
            self.charLength *= number
            self.charHeightOffset *= number
            self.charLenghtOffset *= number
            self.svgWidth *= number
            self.svgHeight *= number


# lists (i just wanted a comment here)
viewers=[]
sorted_list = []

# importing the list of viewers
with open('viewers.csv', newline="") as csvfile:
        temp_viewers = csv.reader(csvfile, delimiter=',', quotechar='|')
        for name, color, role in temp_viewers:
              viewers.append(Viewer(name, color, role))

""" 
    We want the names to fill a row as best possible, without overflowing
    the max width of the svg. If a name will overflow the max width we
    will not add that to the list of sorted viewers, but rather hold off
    and check if the next names fit. 

    the loop adds a x value and a y value to a viewer. x relates to a
    names starting position in the svg in the horizontal direction.
    y is the end position in the vertical direction.
"""

#baseFontCharLength = 2.75
#baseCharHeightOffset = 6
#base sizes - these sizes are 4times(ish) as large as the ones I started with above.
baseFontSize = 24
baseFontCharLength = 11

baseCharHeightOffset = baseFontSize + math.floor((baseFontSize / 4))
baseCharLengthOffset = 28

baseImageWidth = 400
baseImageHeight = 800


proportions = Proportions(baseFontSize, baseFontCharLength, baseCharHeightOffset, baseCharLengthOffset, baseImageWidth, baseImageHeight)
proportions.multiply(4)
print(vars(proportions))

# temp vairables (i just wanted a comment here)
temp_remove_array=[]
temp_max_x = proportions.svgWidth
temp_x = 0


for i in range(0, proportions.svgHeight + 1, proportions.charHeightOffset):
        for j in range(0, len(viewers)):
                if temp_max_x == 0:
                    break

                temp_viewer = viewers[j]
                calulatedNamePixelLength = math.ceil(len(temp_viewer.name) * proportions.charLength) + proportions.charLenghtOffset
                
                if calulatedNamePixelLength <= temp_max_x:
                    temp_viewer.x = temp_x
                    temp_viewer.y = i
                    temp_x = temp_x + calulatedNamePixelLength

                    sorted_list.append(temp_viewer)
                    temp_remove_array.append(j)

                    temp_max_x = temp_max_x - calulatedNamePixelLength

        temp_remove_array_copy = temp_remove_array.copy()
        temp_remove_array_copy.reverse()

        for viewer_list_index in temp_remove_array_copy:
            viewers.pop(viewer_list_index)

        if viewers.count == 0:
            break
        
        temp_remove_array.clear()
        temp_max_x = proportions.svgWidth
        temp_x = 0

for sorted_viewer in sorted_list:
    print(f'name: {sorted_viewer.name},\t\t y: {sorted_viewer.y},\t x: {sorted_viewer.x}, name length: {math.ceil(len(sorted_viewer.name) * proportions.charLength) + proportions.charLenghtOffset}, \t max width: {proportions.svgWidth}')


# build the svg.
names = et.Element('svg', width=str(proportions.svgWidth), height=str(proportions.svgHeight), version='1.1', xmlns='http://www.w3.org/2000/svg', viewBox=f'0 -{proportions.fontSize} {proportions.svgWidth} {proportions.svgHeight}')

for viewer in sorted_list:
      text = et.Element("text", x=str(viewer.x), y=str(viewer.y), fill=str(viewer.color), style=f'font-family:Consolas; font-size:{proportions.fontSize}px')
      text.text = viewer.name
      names.append(text)



#open file and save
f = open("sample.svg", "wb")
f.write(et.tostring(names))
f.close()