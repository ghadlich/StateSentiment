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
import time
import math
import json
import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from tabulate import tabulate
from collections import defaultdict 
from twitterutils.twitterutils import recent_search_query
from tqdm.auto import tqdm

state_file_list = {
    "Alabama" : "AL.txt",
    "Alaska" : "AK.txt",
    "Arizona" : "AZ.txt",
    "Arkansas" : "AR.txt",
    "California" : "CA.txt",
    "Colorado" : "CO.txt",
    "Connecticut" : "CT.txt",
    "Delaware" : "DE.txt",
    "Florida" : "FL.txt",
    "Georgia" : "GA.txt",
    "Hawaii" : "HI.txt",
    "Idaho" : "ID.txt",
    "Illinois" : "IL.txt",
    "Indiana" : "IN.txt",
    "Iowa" : "IA.txt",
    "Kansas" : "KS.txt",
    "Kentucky" : "KY.txt",
    "Louisiana" : "LA.txt",
    "Maine" : "ME.txt",
    "Maryland" : "MD.txt",
    "Massachusetts" : "MA.txt",
    "Michigan" : "MI.txt",
    "Minnesota" : "MN.txt",
    "Mississippi" : "MS.txt",
    "Missouri" : "MO.txt",
    "Montana" : "MT.txt",
    "Nebraska" : "NE.txt",
    "Nevada" : "NV.txt",
    "New Hampshire" : "NV.txt",
    "New Jersey" : "NJ.txt",
    "New Mexico" : "NM.txt",
    "New York" : "NY.txt",
    "North Carolina" : "NC.txt",
    "North Dakota" : "ND.txt",
    "Ohio" : "OH.txt",
    "Oklahoma" : "OK.txt",
    "Oregon" : "OR.txt",
    "Pennsylvania" : "PA.txt",
    "Rhode Island" : "RI.txt",
    "South Carolina" : "SC.txt",
    "South Dakota" : "SD.txt",
    "Tennessee" : "TN.txt",
    "Texas" : "TX.txt",
    "Utah" : "UT.txt",
    "Vermont" : "VT.txt",
    "Virginia" : "VA.txt",
    "Washington" : "WA.txt",
    "West Virginia" : "WV.txt",
    "Wisconsin" : "WA.txt",
    "Wyoming" : "WY.txt",
    "District of Columbia" : "DC.txt",
    }

state_query = {
    "Alabama" : "Alabama",
    "Alaska" : "Alaska",
    "Arizona" : "Arizona",
    "Arkansas" : "Arkansas",
    "California" : "California",
    "Colorado" : "Colorado",
    "Connecticut" : "Connecticut",
    "Delaware" : "Delaware",
    "Florida" : "Florida",
    "Georgia" : "Georgia",
    "Hawaii" : "Hawaii",
    "Idaho" : "Idaho",
    "Illinois" : "Illinois",
    "Indiana" : "Indiana -Jones",
    "Iowa" : "Iowa",
    "Kansas" : "Kansas",
    "Kentucky" : "Kentucky",
    "Louisiana" : "Louisiana",
    "Maine" : "Maine",
    "Maryland" : "Maryland",
    "Massachusetts" : "Massachusetts",
    "Michigan" : "Michigan",
    "Minnesota" : "Minnesota",
    "Mississippi" : "Mississippi",
    "Missouri" : "Missouri",
    "Montana" : "Montana -Hannah -La",
    "Nebraska" : "Nebraska",
    "Nevada" : "Nevada",
    "New Hampshire" : "New Hampshire",
    "New Jersey" : "New Jersey",
    "New Mexico" : "New Mexico",
    "New York" : "New York",
    "North Carolina" : "North Carolina",
    "North Dakota" : "North Dakota",
    "Ohio" : "Ohio",
    "Oklahoma" : "Oklahoma",
    "Oregon" : "Oregon",
    "Pennsylvania" : "Pennsylvania",
    "Rhode Island" : "Rhode Island",
    "South Carolina" : "South Carolina",
    "South Dakota" : "South Dakota",
    "Tennessee" : "Tennessee",
    "Texas" : "Texas",
    "Utah" : "Utah",
    "Vermont" : "Vermont",
    "Virginia" : "Virginia",
    "Washington" : "Washington",
    "West Virginia" : "West Virginia",
    "Wisconsin" : "Wisconsin",
    "Wyoming" : "Wyoming",
    "District of Columbia" : "Washington DC",
    }

def pull_tweets(date, num_tweets=10):
    dir = os.path.join("./raw_tweets", date)

    if (os.path.exists(dir)):
        return dir

    os.makedirs(dir)

    for state in tqdm(state_file_list, total=len(state_file_list), position=0, leave=True):
        output_file = os.path.join(dir, state_file_list[state])
        if (state == "District of Columbia"):
            recent_search_query(f"-is:retweet lang:en Washington DC", 
                                output_file=output_file, 
                                place=None, 
                                max_results = num_tweets)
        else:
            recent_search_query(f"-is:retweet lang:en {state_query[state]}", 
                                output_file=output_file, 
                                place=state, 
                                max_results = num_tweets)

    return dir


def read_tweets(filename):
    # Reads in Tweets from a JSON File
    data = None
    with open(filename) as json_file:
        data = json.load(json_file)

    return data

def tabulate_results(state_sentiment, state_tweet_number):
    # Print out tabular results
    print("\nState Results:")
    header = ['State', 'Positive', 'Tweets']
    data = []

    for state in state_sentiment:
        data.append([])
        data[-1].append(state)
        data[-1].append(str(state_sentiment[state])+"%")
        data[-1].append(str(state_tweet_number[state]))

    print(tabulate(data, header, tablefmt="github"))

def parse_tweets(model, dir):
    # Plots Sentiment Data per State
    state_sentiment = dict()
    state_tweet_number = dict()

    # Cycle Through Each State
    print("Parsing and Predicting Sentiment per state with model: " + model.name())
    for state in tqdm(state_file_list, total=len(state_file_list), position=0, leave=True):
        tweets = read_tweets(dir + "/" + state_file_list[state])
        positive = 0
        negative = 0

        # For Each Tweet, use English Language Tweets
        for tweet in tqdm(tweets, total=len(tweets), position=0, leave=True):
            if (tweet["lang"] != "en"):
                continue

            prediction, _ = model.predict(tweet['text'])

            if (prediction == "Positive"):
                positive += 1
            else:
                negative += 1

        # Calculate Positive Percentage
        percent_positive = round(100*positive / (positive+negative), 2)

        state_tweet_number[state] = positive+negative

        print(state + " Percent Positive: " + str(percent_positive) + "% of " + str(state_tweet_number[state]) + " tweets")

        state_sentiment[state] = percent_positive

    best_state = "North Dakota"
    best_percent_positive = 0
    for state in state_sentiment:
        if (state_sentiment[state] > best_percent_positive):
            best_percent_positive = state_sentiment[state]
            best_state = state

    return state_sentiment, best_state, state_tweet_number

def create_composite(model_data):
    state_sentiment = defaultdict(float)
    num_models = len(model_data)

    for model_name in model_data:
        for state in model_data[model_name]:
            state_sentiment[state] += model_data[model_name][state]/num_models

    best_state = "North Dakota"
    best_percent_positive = 0
    for state in state_sentiment:
        if (state_sentiment[state] > best_percent_positive):
            best_percent_positive = state_sentiment[state]
            best_state = state

    return state_sentiment, best_state