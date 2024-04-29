#!/usr/bin/env python

# This script is used to build a SVG from a CSV list of twitch usernames.
# The SVG will be a square of size x,y, and the names will be placed sequntially row by row,
# as illustrated as below.
#
# |----------------x
# |creatin msvosch x
# |jon stranger    x
# |verylongnameeee x
# |----------------x
#
# CSV must have username. Color, nickname, and role are optional.
# If no color set, the color of the name is defaulted to black.
# Colors can be given as a name or as a HEX code. If given as a name, they must be a amongst the
# 140 supported by most browsers. If not recognized, the color is defaulted to black.
# Nickname takes presedence over username if added.
# Roles supported are mod and vip. Usernames with mod get the mod sword beside their name,
# while usernames with vip get the vip diamond.
#
# The font family has to be monospaced, i.e. where alle characters have the same length.
# Defaut font family is "Consolas".
#
# Script saves the files with a timestamp on the format yyyy-mm-dd-hr-mm-ss.

import sys
import csv as csvReader
import math
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as et

# Helper classes.

## Holds the data needed for the visual representation of a viewer's name in the SVG.


class Viewer:
    def __init__(self, displayName, color, role):
        self.displayName = displayName.upper()
        self.color = color
        self.role = role
        self.x = 0
        self.y = 0


## Class to more easily increase the size of the produced SVG.


class ElementSize:

    width = 0
    height = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def multiply(self, number):
        self.width *= number
        self.height *= number


class FontSize:

    fontSize = 0
    charLength = 0
    charHeightOffset = 0

    def __init__(self, fontSize, charLength, charHeightOffset):
        self.fontSize = fontSize
        self.charLength = charLength
        self.charHeightOffset = charHeightOffset

    def multiply(self, number):
        self.fontSize *= number
        self.charLength *= number
        self.charHeightOffset *= number


class Font:

    font = "Consolas"

    def __init__(self, font, fontSize):
        self.font = font
        self.fontSize = fontSize


def set_base_sizes():

    print("Setting base sizes for elements...")

    baseFontSize = 16
    baseFontCharLength = 10
    baseFontCharHeightOffset = baseFontSize + math.floor((baseFontSize / 10))

    fontSize = FontSize(baseFontSize, baseFontCharLength, baseFontCharHeightOffset)

    svgWidth = 800
    svgHeight = 0

    svgSize = ElementSize(svgWidth, svgHeight)

    roleIconWidth = 12
    roleIconHeight = 10

    roleIconSize = ElementSize(roleIconWidth, roleIconHeight)

    return fontSize, svgSize, roleIconSize


def has_command_line_argument(sysArgs):
    return len(sysArgs) > 1


def is_help_command(argument):
    return str(argument).lower() == "--help" or str(argument).lower() == "-h"


def print_help():
    print()
    print("\nCreates a list of Twitch usernames on a SVG format, based on CSV file.")
    print(
        "See https://github.com/maardal/spacey_svg_builder for requirements for CSV file."
    )
    print("\noptional arguments:\n\t-h, --help\t\tshow this message and exit.")
    print()


def validate_cli_arguments():

    print("validating cli arguments")

    sysArgs = sys.argv
    scriptName = sysArgs[0]
    USAGE = f"Usage: python {scriptName} [--help] | <path_to_csv_file>"  # Move to global scope? #make command that returns the string?

    if not has_command_line_argument(sysArgs):
        print("No arguments provided.")
        raise SystemExit(USAGE)

    argument = sysArgs[1]

    if is_help_command(argument):
        print_help()
        raise SystemExit(USAGE)

    filePath = Path(argument)

    if not filePath.exists:
        print("Path/File does not exist.")
        raise SystemExit(USAGE)

    if not filePath.is_file():
        print("File not provided.")
        raise SystemExit(USAGE)

    if not filePath.suffix.lower() == ".csv":
        print("File format needs to be CSV.")
        raise SystemExit(USAGE)

    return scriptName, str(filePath)


def processCSV(scriptName, csvPath):
    print(f"{scriptName} processing CSV...")
    viewers = []
    USAGE = f"Usage: python {scriptName} [--help] | <path_to_csv_file>"  # Move to global scope? #make command that returns the string?

    try:
        with open(csvPath, newline="") as csvfile:
            viewer_list = csvReader.reader(csvfile, delimiter=",", quotechar="|")
            for name, color, nickname, role in viewer_list:
                if name != "":
                    viewers.append(
                        Viewer(
                            nickname.strip() if nickname != "" else name.strip(),
                            color.strip(),
                            role.strip().lower(),
                        )
                    )

    except FileNotFoundError as error:
        print(f"Please provide a csv file. Provided path and file is: {csvPath}")
        raise SystemExit(USAGE)

    except ValueError as error:
        print(
            f"{scriptName} expects exactly 4 values in the order of name,color,nickname,role. See See https://github.com/maardal/spacey_svg_builder for more details."
        )
        raise SystemExit(USAGE)

    except OSError as error:
        print(
            "Could not open and/or read file. File must be csv file in the supported format. See https://github.com/maardal/spacey_svg_builder for more details."
        )
        raise SystemExit(USAGE)

    except Exception as exception:
        print("IN METHOD")
        print(exception.__class__)
        print(exception)
        print(
            "\nUnexpected error. Report error at https://github.com/maardal/spacey_svg_builder\n"
        )
        raise SystemExit(USAGE)

    csvfile.close()

    return viewers


# Calculate coordinates for names. Will not let names overflow the width of the SVG.
# Also sorts list name, so spaces at the end of a line will be filled by the first possible name that is short enough.
def set_viewer_coordinates(viewers, svgSize, fontSize, roleIconSize):

    print("Calculating coordinates for names...")

    sorted_list = []
    temp_remove_array = []
    temp_max_x = svgSize.width
    temp_x = 0
    svgHeight = 0  # svgHeight is determined by the amount of names.

    while len(viewers) > 0:
        for j in range(0, len(viewers)):
            if temp_max_x == 0:
                break

            temp_viewer = viewers[j]
            calulatedPixelLengthName = math.ceil(
                len(temp_viewer.displayName) * fontSize.charLength
            )
            if temp_viewer.role == "vip" or temp_viewer.role == "mod":
                calulatedPixelLengthName += roleIconSize.width

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
        temp_max_x = svgSize.width
        temp_x = 0
        svgHeight += fontSize.charHeightOffset

    svgSize.height = svgHeight

    return sorted_list, svgSize


def build_svg(viewer_list, font, svgSize, roleIconSize):
    # Build SVG.
    print("Building svg...")

    heightBuffer = 10

    svg = et.Element(
        "svg",
        width=str(svgSize.width),
        height=str(svgSize.height + heightBuffer),
        version="1.1",
        xmlns="http://www.w3.org/2000/svg",
        viewBox=f"0 -{font.fontSize.fontSize} {svgSize.width} {svgSize.height}",
    )

    defs = et.Element("defs")

    iconWidth = roleIconSize.width
    iconHeight = roleIconSize.height

    ## vip_badge_coordinates - a diamond.
    vip_pattern_points = create_vip_pattern_points_string(iconWidth, iconHeight)

    vip_pattern_definition = et.SubElement(
        defs,
        "pattern",
        id="vip_badge",
        x="0",
        y="0",
        width=str(iconWidth),
        height=str(iconHeight),
        patternUnits="objectBoundingBox",
    )
    vip_pattern_geometry = et.SubElement(
        vip_pattern_definition,
        "polygon",
        fill="#fb0493",
        points=vip_pattern_points,
    )

    ## mod_badge_coordinates - a sword.
    mod_pattern_points = create_mod_pattern_points_string(iconWidth, iconHeight)

    mod_pattern_definition = et.SubElement(
        defs,
        "pattern",
        id="mod_badge",
        x="0",
        y="0",
        width=str(iconWidth),
        height=str(iconHeight),
        patternUnits="objectBoundingBox",
    )
    mod_pattern_geometry = et.SubElement(
        mod_pattern_definition,
        "polygon",
        fill="#14cb04",
        points=mod_pattern_points,
    )

    svg.append(defs)

    ## Place names in SVG based on coordinates.

    for viewer in viewer_list:
        viewer_x_position = viewer.x

        if viewer.role.lower() == "vip":
            svg.append(
                et.Element(
                    "rect",
                    x=str(viewer_x_position),
                    y=str(viewer.y - 20),
                    width=str(iconWidth),
                    height=str(iconHeight),
                    fill="url(#vip_badge)",
                )
            )
            viewer_x_position += iconWidth

        if viewer.role.lower() == "mod":
            svg.append(
                et.Element(
                    "rect",
                    x=str(viewer_x_position),
                    y=str(viewer.y - 20),
                    width=str(iconWidth),
                    height=str(iconHeight),
                    fill="url(#mod_badge)",
                )
            )
            viewer_x_position += iconWidth

        text = et.Element(
            "text",
            x=str(viewer_x_position),
            y=str(viewer.y),
            fill=str(viewer.color),
            style=f"font-family:{font.font}; font-size:{font.fontSize.fontSize}px",
        )
        text.text = viewer.displayName
        svg.append(text)

    et.indent(svg, "  ")

    currentDateTime = datetime.now().strftime("-%Y%m%d-%H%M%S")

    f = open(f"spacey{currentDateTime}.svg", "wb")
    f.write(et.tostring(svg))
    f.close()

    print("SVG built...")


def create_vip_pattern_points_string(iconWidth, iconHeight):
    diamond_left_middle = f"{0} {iconHeight * 0.26}"
    diamond_left_top = f"{iconWidth * 0.1875} {0}"
    diamond_right_top = f"{iconWidth * 0.8125} {0}"
    diamond_right_middle = f"{iconWidth} {iconHeight * 0.26}"
    diamond_bottom_tip = f"{iconWidth/2} {iconHeight}"

    return f"{diamond_left_middle}, {diamond_left_top}, {diamond_right_top}, {diamond_right_middle}, {diamond_bottom_tip}"


def create_mod_pattern_points_string(iconWidth, iconHeight):
    grip_bottom_left = f"{0} {iconHeight * 0.875}"
    grip_upper_left = f"{iconWidth * 0.125} {iconHeight * 0.6875}"
    guard_bottom_left = f"{0} {iconHeight * 0.5625}"
    guard_upper_left = f"{iconWidth * 0.125} {iconHeight * 0.4375}"
    blade_base_left = f"{iconWidth * 0.275} {iconHeight * 0.55}"
    blade_point_left = f"{iconWidth * 0.75} {0}"
    blade_point_middle = f"{iconWidth} {0}"
    blade_point_right = f"{iconWidth} {iconHeight * 0.25}"
    blade_base_right = f"{iconWidth * 0.4375} {iconHeight * 0.6875}"
    guard_upper_right = f"{iconWidth * 0.625} {iconHeight * 0.875}"
    guard_bottom_right = f"{iconWidth * 0.5} {iconHeight}"
    grip_upper_right = f"{iconWidth * 0.275} {iconHeight * 0.875}"
    grip_bottom_right = f"{iconWidth * 0.125} {iconHeight}"

    return f"{grip_bottom_left}, {grip_upper_left}, {guard_bottom_left}, {guard_upper_left}, {blade_base_left}, {blade_point_left}, {blade_point_middle}, {blade_point_right}, {blade_base_right}, {guard_upper_right}, {guard_bottom_right}, {grip_upper_right}, {grip_bottom_right}"


def main():
    fontSize, svgSize, roleIconSize = set_base_sizes()

    scriptName, csvPath = validate_cli_arguments()
    viewers = processCSV(scriptName, csvPath)

    multiplicationFactor = 2

    fontSize.multiply(multiplicationFactor)
    svgSize.multiply(multiplicationFactor)
    roleIconSize.multiply(multiplicationFactor)

    font = Font("Consolas", fontSize)

    # set size of SVG - yet to make this function.
    sorted_viewers, svgSize = set_viewer_coordinates(
        viewers, svgSize, fontSize, roleIconSize
    )
    build_svg(sorted_viewers, font, svgSize, roleIconSize)


if __name__ == "__main__":
    main()
