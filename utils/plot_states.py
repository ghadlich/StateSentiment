#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021 Grant Hadlich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE. 
import os
import geopandas
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Polygon
import numpy as np

def plot_state_sentiment(state_list, model_name, date, directory):
    # Construct Output File
    output_file = os.path.join(directory, "us_states" + "_" + model_name + ".png")
     
    """  Takes in a map by state name with some decimal percentage as the value to plot on US Map """
    states = geopandas.read_file("./data/cb_2018_us_state/cb_2018_us_state_500k.shp")

    # Shift Alaska
    m = states['NAME'] == 'Alaska'
    states[m] = states[m].set_geometry(states[m].translate(-75, -39).scale(.3,.5))

    # Shift Hawaii
    m = states['NAME'] == 'Hawaii'
    states[m] = states[m].set_geometry(states[m].translate(44,5).scale(1.7,1.7))

    # Shift DC
    m = states['NAME'] == 'District of Columbia'
    states[m] = states[m].set_geometry(states[m].translate(5,-3).scale(16,16))

    # Collect States for Plot
    conus = states[~states['STUSPS'].isin(['PR', "AS", "VI", "MP", "GU"])]

    # Create polygon that is the area of interest
    target_poly = Polygon([(-125, 18), (-125, 52), 
                        (-65, 52), (-65, 18)])

    # Clip the Map
    conus_clipped = conus.copy()
    conus_clipped['geometry'] = conus.intersection(target_poly)
    conus_clipped = conus_clipped[conus_clipped['geometry'] != Polygon()]

    # Create Color Gradient
    colors_map = matplotlib.cm.get_cmap('Blues', 10001)

    # Map the Colors
    color_list = []
    for i in range(len(conus_clipped['NAME'])):
        color_list.append(colors_map(5000))

    for state_name in state_list:
        m = conus_clipped['NAME'] == state_name
        idx = np.where(m)[0][0]
        color_list[idx] = colors_map(int(state_list[state_name]*100))

    # Create Initial Plot
    us_map = conus_clipped.plot(figsize=(12, 8), color=color_list)

    norm = matplotlib.colors.Normalize(vmin=0, vmax=100)

    sm = plt.cm.ScalarMappable(cmap=colors_map, norm=norm)
    sm.set_array([])  # only needed for matplotlib < 3.1

    # Create and Save the Plot
    us_map.axis('off')
    us_map.set_title('State Mention Sentiment \nDate: ' + date + '\nModel: ' + model_name + "\n© Grant Hadlich", loc='right')
    fig = us_map.get_figure()
    fig.tight_layout()
    fig.colorbar(sm, shrink=0.75, label='Percent Positive')

    fig.savefig(output_file, dpi=256)

    return output_file
