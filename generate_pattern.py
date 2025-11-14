#!/usr/bin/env python

"""
Adapted from opencv's generate_pattern.py file
"""

"""generate_pattern.py
Usage example:
python generate_pattern.py -o out.svg -r 11 -c 8 -T circles -s 20.0 -R 5.0 -u mm -w 216 -h 279
-o, --output - output file (default out.svg)
-r, --rows - pattern rows (default 11)
-c, --columns - pattern columns (default 8)
-T, --type - type of pattern: circles, acircles, checkerboard, radon_checkerboard, charuco_board. default circles.
-s, --square_size - size of squares in pattern (default 20.0)
-R, --radius_rate - circles_radius = square_size/radius_rate (default 5.0)
-u, --units - mm, inches, px, m (default mm)
-w, --page_width - page width in units (default 216)
-h, --page_height - page height in units (default 279)
-a, --page_size - page size (default A4), supersedes -h -w arguments
-m, --markers - list of cells with markers for the radon checkerboard
-p, --aruco_marker_size - aruco markers size for ChAruco pattern (default 10.0)
-f, --dict_file - file name of custom aruco dictionary for ChAruco pattern
-do, --dict_offset - index of the first ArUco index used
-H, --help - show help
"""

import argparse
import numpy as np
import json
import gzip
from svgfig import *
from warnings import warn

def make_circles_pattern(square_size, radius_rate, cols, rows, width, height):
    g = SVG("g")
    spacing = square_size
    r = spacing / radius_rate
    pattern_width = ((cols - 1.0) * spacing) + (2.0 * r)
    pattern_height = ((rows - 1.0) * spacing) + (2.0 * r)
    x_spacing = (width - pattern_width) / 2.0
    y_spacing = (height - pattern_height) / 2.0
    for x in range(0, cols):
        for y in range(0, rows):
            dot = SVG("circle", cx=(x * spacing) + x_spacing + r,
                      cy=(y * spacing) + y_spacing + r, r=r, fill="black", stroke="none")
            g.append(dot)
    return g

def make_acircles_pattern(square_size, radius_rate, cols, rows, width, height):
    g = SVG("g")
    spacing = square_size
    r = spacing / radius_rate
    pattern_width = ((cols-1.0) * 2 * spacing) + spacing + (2.0 * r)
    pattern_height = ((rows-1.0) * spacing) + (2.0 * r)
    x_spacing = (width - pattern_width) / 2.0
    y_spacing = (height - pattern_height) / 2.0
    for x in range(0, cols):
        for y in range(0, rows):
            dot = SVG("circle", cx=(2 * x * spacing) + (y % 2)*spacing + x_spacing + r,
                      cy=(y * spacing) + y_spacing + r, r=r, fill="black", stroke="none")
            g.append(dot)
    return g

def make_checkerboard_pattern(square_size, width, height, rows, cols):
    g = SVG("g")
    spacing = square_size
    xspacing = (width - cols * square_size) / 2.0
    yspacing = (height - rows * square_size) / 2.0
    for x in range(0, cols):
        for y in range(0, rows):
            if x % 2 == y % 2:
                square = SVG("rect", x=x * spacing + xspacing, y=y * spacing + yspacing, width=spacing,
                             height=spacing, fill="black", stroke="none")
            else:
                square = SVG("rect", x=x * spacing + xspacing, y=y * spacing + yspacing, width=spacing,
                             height=spacing, fill="white", stroke="none")
            g.append(square)
    return g

def _make_round_rect(x, y, diam, corners=("right", "right", "right", "right")):
    rad = diam / 2
    cw_point = ((0, 0), (diam, 0), (diam, diam), (0, diam))
    mid_cw_point = ((0, rad), (rad, 0), (diam, rad), (rad, diam))
    res_str = "M{},{} ".format(x + mid_cw_point[0][0], y + mid_cw_point[0][1])
    n = len(cw_point)
    for i in range(n):
        if corners[i] == "right":
            res_str += "L{},{} L{},{} ".format(x + cw_point[i][0], y + cw_point[i][1],
                                               x + mid_cw_point[(i + 1) % n][0], y + mid_cw_point[(i + 1) % n][1])
        elif corners[i] == "round":
            res_str += "A{},{} 0,0,1 {},{} ".format(rad, rad, x + mid_cw_point[(i + 1) % n][0],
                                                    y + mid_cw_point[(i + 1) % n][1])
        else:
            raise TypeError("unknown corner type")
    return res_str

def _get_type(x, y):
    corners = ["right", "right", "right", "right"]
    is_inside = True
    if x == 0:
        corners[0] = "round"
        corners[3] = "round"
        is_inside = False
    if y == 0:
        corners[0] = "round"
        corners[1] = "round"
        is_inside = False
    if x == self.cols - 1:
        corners[1] = "round"
        corners[2] = "round"
        is_inside = False
    if y == self.rows - 1:
        corners[2] = "round"
        corners[3] = "round"
        is_inside = False
        return corners, is_inside

def make_radon_checkerboard_pattern(square_size, width, height, cols, rows, markers=None):
    g = SVG("g")
    spacing = square_size
    xspacing = (width - cols * square_size) / 2.0
    yspacing = (height - rows * square_size) / 2.0
    for x in range(0, cols):
        for y in range(0, rows):
            if x % 2 == y % 2:
                corner_types, is_inside = _get_type(x, y)
                if is_inside:
                    square = SVG("rect", x=x * spacing + xspacing, y=y * spacing + yspacing, width=spacing,
                                 height=spacing, fill="black", stroke="none")
                else:
                    square = SVG("path", d=_make_round_rect(x * spacing + xspacing, y * spacing + yspacing,
                                  spacing, corner_types), fill="black", stroke="none")
                g.append(square)
    if markers is not None:
        r = square_size * 0.17
        pattern_width = ((cols - 1.0) * spacing) + (2.0 * r)
        pattern_height = ((rows - 1.0) * spacing) + (2.0 * r)
        x_spacing = (width - pattern_width) / 2.0
        y_spacing = (height - pattern_height) / 2.0
        for x, y in markers:
            color = "black"
            if x % 2 == y % 2:
                color = "white"
            dot = SVG("circle", cx=(x * spacing) + x_spacing + r,
                      cy=(y * spacing) + y_spacing + r, r=r, fill=color, stroke="none")
            g.append(dot)
    return g

def _create_marker_bits(markerSize_bits, byteList):

    marker = np.zeros((markerSize_bits+2, markerSize_bits+2))
    bits = marker[1:markerSize_bits+1, 1:markerSize_bits+1]

    for i in range(markerSize_bits):
        for j in range(markerSize_bits):
            bits[i][j] = int(byteList[i*markerSize_bits+j])

    return marker

def make_charuco_board(aruco_marker_size, square_size, dict_file, cols, rows, width, height, dict_offset):
    g = SVG("g")
    if (aruco_marker_size > square_size):
        raise Exception("Aruco marker cannot be lager than chessboard square!")

    try:
        with gzip.open(dict_file, 'r') as fin:
            json_bytes = fin.read()
            json_str = json_bytes.decode('utf-8')
            dictionary = json.loads(json_str)
    except gzip.BadGzipFile as e:
        f = open(dict_file)
        dictionary = json.load(f)

    if (dictionary["nmarkers"] < int(cols * rows / 2)):
        raise Exception("Aruco dictionary contains less markers than it needs for chosen board. Please choose another dictionary or use smaller board than required for chosen board")

    markerSize_bits = dictionary["markersize"]

    side = aruco_marker_size / (markerSize_bits + 2)
    spacing = square_size
    xspacing = (width - cols * square_size) / 2.0
    yspacing = (height - rows * square_size) / 2.0

    ch_ar_border = (square_size - aruco_marker_size) / 2
    if ch_ar_border < side * 0.7:
        warn("Marker border {} is less than 70% of ArUco pin size {}. Please increase --square_size or decrease --marker_size for stable board detection".format(ch_ar_border, int(side)))
    marker_id = dict_offset
    for y in range(0, rows):
        for x in range(0, cols):

            if x % 2 == y % 2:
                square = SVG("rect", x=x * spacing + xspacing, y=y * spacing + yspacing, width=spacing,
                             height=spacing, fill="black", stroke="none")
                g.append(square)
            else:
                img_mark = _create_marker_bits(markerSize_bits, dictionary["marker_"+str(marker_id)])
                marker_id +=1
                x_pos = x * spacing + xspacing
                y_pos = y * spacing + yspacing

                square = SVG("rect", x=x_pos+ch_ar_border, y=y_pos+ch_ar_border, width=aruco_marker_size,
                                         height=aruco_marker_size, fill="black", stroke="none")
                g.append(square)

                # BUG: https://github.com/opencv/opencv/issues/27871
                # The loop bellow merges white squares horizontally and vertically to exclude visible grid on the final pattern
                for x_ in range(len(img_mark[0])):
                    y_ = 0
                    while y_ < len(img_mark):
                        y_start = y_
                        while y_ < len(img_mark) and img_mark[y_][x_] != 0:
                            y_ += 1

                        if y_ > y_start:
                            rect = SVG("rect", x=x_pos+ch_ar_border+(x_)*side, y=y_pos+ch_ar_border+(y_start)*side, width=side,
                                       height=(y_ - y_start)*side, fill="white", stroke="none")
                            g.append(rect)

                        y_ += 1

                for y_ in range(len(img_mark)):
                    x_ = 0
                    while x_ < len(img_mark[0]):
                        x_start = x_
                        while x_ < len(img_mark[0]) and img_mark[y_][x_] != 0:
                            x_ += 1

                        if x_ > x_start:
                            rect = SVG("rect", x=x_pos+ch_ar_border+(x_start)*side, y=y_pos+ch_ar_border+(y_)*side, width=(x_-x_start)*side,
                                       height=side, fill="white", stroke="none")
                            g.append(rect)

                        x_ += 1
    return g

def render(g, width, height, vwidth, vheight):
    return bytearray(
        canvas(g,
            width="%dpx" % (vwidth), height="%dpx" % (vheight),
            viewBox="0 0 %d %d" % (width, height)).standalone_xml(encoding="utf-8"),
            encoding="utf-8",
    )

def save(g, width, height, units, output):
    c = canvas(g, width="%d%s" % (width, units), height="%d%s" % (height, units),
               viewBox="0 0 %d %d" % (width, height))
    c.save(output)