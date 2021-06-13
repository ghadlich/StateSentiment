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
from tqdm.auto import tqdm


state_image_list = {
    "Alabama" : "AL.png",
    "Alaska" : "AK.png",
    "Arizona" : "AZ.png",
    "Arkansas" : "AR.png",
    "California" : "CA.png",
    "Colorado" : "CO.png",
    "Connecticut" : "CT.png",
    "Delaware" : "DE.png",
    "Florida" : "FL.png",
    "Georgia" : "GA.png",
    "Hawaii" : "HI.png",
    "Idaho" : "ID.png",
    "Illinois" : "IL.png",
    "Indiana" : "IN.png",
    "Iowa" : "IA.png",
    "Kansas" : "KS.png",
    "Kentucky" : "KY.png",
    "Louisiana" : "LA.png",
    "Maine" : "ME.png",
    "Maryland" : "MD.png",
    "Massachusetts" : "MA.png",
    "Michigan" : "MI.png",
    "Minnesota" : "MN.png",
    "Mississippi" : "MS.png",
    "Missouri" : "MO.png",
    "Montana" : "MT.png",
    "Nebraska" : "NE.png",
    "Nevada" : "NV.png",
    "New Hampshire" : "NH.png",
    "New Jersey" : "NJ.png",
    "New Mexico" : "NM.png",
    "New York" : "NY.png",
    "North Carolina" : "NC.png",
    "North Dakota" : "ND.png",
    "Ohio" : "OH.png",
    "Oklahoma" : "OK.png",
    "Oregon" : "OR.png",
    "Pennsylvania" : "PA.png",
    "Rhode Island" : "RI.png",
    "South Carolina" : "SC.png",
    "South Dakota" : "SD.png",
    "Tennessee" : "TN.png",
    "Texas" : "TX.png",
    "Utah" : "UT.png",
    "Vermont" : "VT.png",
    "Virginia" : "VA.png",
    "Washington" : "WA.png",
    "West Virginia" : "WV.png",
    "Wisconsin" : "WI.png",
    "Wyoming" : "WY.png",
    "District of Columbia" : "DC.png",
    }

if __name__ == "__main__":
    # Construct Output File
    directory = "./state_images"

    for state in tqdm(state_image_list, total=len(state_image_list), position=0, leave=True):
        output_file = os.path.join(directory, state_image_list[state])
        
        """  Takes in a map by state name with some decimal percentage as the value to plot on US Map """
        states = geopandas.read_file("./data/cb_2018_us_state/cb_2018_us_state_500k.shp")

        # Get States
        m = states['NAME'] == state

        # Create polygon that is the area of interest
        if state == "Hawaii":
            target_poly = Polygon([(-162, 23), (-162, 15), 
                            (-154, 15), (-154, 23)])
        else:
            target_poly = Polygon([(-179.9, 18), (-179.9, 89), 
                            (-65, 89), (-65, 18)])

        # Collect States for Plot
        conus = states[m]

        # Clip the Map
        conus_clipped = conus.copy()
        conus_clipped['geometry'] = conus.intersection(target_poly)
        conus = conus_clipped[conus_clipped['geometry'] != Polygon()]

        # Create Initial Plot
        us_map = conus.plot(figsize=(15, 8))
        #us_map = conus.plot()

        # Create and Save the Plot
        us_map.axis('off')
        fig = us_map.get_figure()
        fig.tight_layout()

        fig.savefig(output_file)

    # Create Conus
    output_file = os.path.join(directory, "US.png")
    
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
    conus = conus_clipped[conus_clipped['geometry'] != Polygon()]

    # Create Initial Plot
    us_map = conus.plot(figsize=(15, 8))

    # Create and Save the Plot
    us_map.axis('off')
    fig = us_map.get_figure()
    fig.tight_layout()

    fig.savefig(output_file)