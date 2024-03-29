#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2022 Grant Hadlich
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
import re

state_file_list = {
    "Alabama" : "AL.txt",
    "Alaska" : "AK.txt",
    "Arizona" : "AZ.txt",
    "Arkansas" : "AR.txt",
    "California" : "CA.txt",
    "Colorado" : "CO.txt",
    "Connecticut" : "CT.txt",
    "District of Columbia" : "DC.txt",
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
    "New Hampshire" : "NH.txt",
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
    "Wisconsin" : "WI.txt",
    "Wyoming" : "WY.txt",
    }

state_query = {
    "Alabama"       : "context:159.1004433527683731457",
    "Alaska"        : "context:159.856868825404391424",
    "Arizona"       : "context:159.1004434267835809792",
    "Arkansas"      : "context:159.1004434802752217088",
    "California"    : "context:159.856860158428798977",
    "Colorado"      : "context:159.856862177474433024",
    "Connecticut"   : "context:159.1004435347592261633",
    "Delaware"      : "context:159.1004435667005333504",
    "Florida"       : "context:159.855436277054750722",
    "Georgia"       : "context:159.1004436112062812160",
    "Hawaii"        : "context:159.856861547208916992",
    "Idaho"         : "context:159.1004437124567842817",
    "Illinois"      : "context:159.1004437399626080256",
    "Indiana"       : "context:159.1004437679377768449",
    "Iowa"          : "context:159.1004438001567465472",
    "Kansas"        : "context:159.1004438305662910464",
    "Kentucky"      : "context:159.1004444164426067969",
    "Louisiana"     : "context:159.856862983665758209",
    "Maine"         : "entity:\"Maine\"",
    "Maryland"      : "context:159.1004446797169717248",
    "Massachusetts" : "context:159.1004448259815772160",
    "Michigan"      : "context:159.1004448635902259200",
    "Minnesota"     : "context:159.1004448843033763840",
    "Mississippi"   : "context:159.1004449226598768640",
    "Missouri"      : "context:159.1004449411504590848",
    "Montana"       : "context:159.1004449615544872960",
    "Nebraska"      : "context:159.1004449860026753024",
    "Nevada"        : "context:159.908351432948047872",
    "New Hampshire" : "context:159.1004450291985469440",
    "New Jersey"    : "context:159.1004451994877157376",
    "New Mexico"    : "entity:\"New Mexico\"",
    "New York"      : "context:159.1022498369795547136",
    "North Carolina" : "context:159.1010252770618703872",
    "North Dakota"  : "context:159.1010253165491466240",
    "Ohio"          : "context:159.1010253454822895616",
    "Oklahoma"      : "context:159.1010253916540305408",
    "Oregon"        : "context:159.1010254568087670785",
    "Pennsylvania"  : "context:159.1010255110465679361",
    "Rhode Island"  : "context:159.1016381330861391873",
    "South Carolina" : "context:159.1016381785339408384",
    "South Dakota"  : "context:159.1016382213472935936",
    "Tennessee"     : "context:159.1016382805914210304",
    "Texas"         : "context:159.855432197297192961",
    "Utah"          : "context:159.1016383724139601920",
    "Vermont"       : "context:159.1016384821512175618",
    "Virginia"      : "context:159.1016385183258312705 -West",
    "Washington"    : "context:159.1016385934814674944 -DC -George -Post -Nationals -Capitol -Examiner",
    "West Virginia" : "context:159.1016386746685128705",
    "Wisconsin"     : "context:159.1016387791591096320",
    "Wyoming"       : "context:159.1016388184941330432",
    "District of Columbia" : "entity:\"Washington DC\"",
    }

def pull_tweets(date, num_tweets=10, max_raw_tweets=5000):
    dir = os.path.join("./raw_tweets", date)

    if (os.path.exists(dir)):
        print(f"Tweets Already Pulled! Location: {dir}")
        return dir, None

    os.makedirs(dir)

    # Keep Total Count
    tweets_pulled = 0

    for state in state_file_list:
        output_file = os.path.join(dir, state_file_list[state])
        tweet_count, total_tweet_count = recent_search_query(f"-is:retweet lang:en {state_query[state]}",
                                            output_file=output_file,
                                            place=None,
                                            max_results = num_tweets)

        tweets_pulled += total_tweet_count


    return dir, tweets_pulled


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

        tweets = [tweet['text'] for tweet in tweets]

        # Remove Links
        tweets = [re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                    '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', tweet) for tweet in tweets]

        # Remove Long Lengths (Things like &lt; can blow up models due to length)
        tweets = [tweet[:min(len(tweet), 512)] for tweet in tweets]

        # Need to put this state first due to things like West Virgina
        states_list = [state]
        states_list += [st for st in state_file_list]
        for st in states_list:
            for i in range(len(tweets)):
                # Remove State Names
                patterns = [re.compile(st+"'s", re.IGNORECASE),
                            re.compile(st+"s", re.IGNORECASE),
                            re.compile(st, re.IGNORECASE)]

                for pattern in patterns:
                    tweets[i] = pattern.sub("[state]", tweets[i])

        # For Each Tweet, use English Language Tweets
        results = model.predict_batch(tweets)

        for result in results:
            prediction, _ = result

            if (prediction == "Positive"):
                positive += 1
            elif (prediction == "Negative"):
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


import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re

def transform_format(val):
    if val[0] == 0:
        return 255
    else:
        return val[0]

def create_image(tweets, img_path, word_cloud_path, date, max_words=300):
    mask = np.array(Image.open(img_path))

    # Transform mask
    transformed_mask = np.ndarray((mask.shape[0],mask.shape[1]), np.int32)

    for i in range(len(mask)):
        transformed_mask[i] = list(map(transform_format, mask[i]))

    stopwords = set(STOPWORDS)
    stopwords.update(["nbsp", "amp", "amps", "state", "m", "city", "u", "will", "s", "one", "states", "posted", "gt", "lt", "DC", "West", "people", "go", "now", "time", "us", "many", "live", "know", "today", "see", "day", "ctztime", "state"])
    wordcloud = WordCloud(width=1125, height=625, max_words=max_words, stopwords=stopwords, normalize_plurals=False, background_color="white", mask=mask, contour_width=1, contour_color='black').generate(tweets)
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    #plt.title(f"© Grant Hadlich - {date}", loc='right')
    plt.tight_layout()
    plt.savefig(word_cloud_path)

def create_word_clouds(date):

    dir = "./raw_tweets/" + date
    # Plots Sentiment Data per State
    state_word_cloud = dict()

    tweets_total = ""

    # Cycle Through Each State
    print("Creating a word cloud for each state")
    tweet_count = 0
    for state in tqdm(state_image_list, total=len(state_image_list), position=0, leave=True):
        tweets = read_tweets(dir + "/" + state_file_list[state])
        img_path = f"./state_images/{state_image_list[state]}"
        word_cloud_path = dir + "/" + state_image_list[state]
        state_word_cloud[state] = word_cloud_path

        tweets_cleaned = []
        # Remove Any Nazi References
        for tweet in tweets:
            skip = False
            if "entities" in tweet:
                if "annotations" in tweet["entities"]:
                    for annotation in tweet["entities"]["annotations"]:
                        if annotation["normalized_text"] == "Nazis":
                            skip = True

            if not skip:
                tweets_cleaned.append(tweet)

        tweets = tweets_cleaned
        tweet_count += len(tweets)

        for i in range(len(tweets)):
            tweets[i] = tweets[i]['text']

            # Remove Links
            tweets[i] = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', tweets[i])

            # Remove a few unicode items
            tweets[i] = tweets[i].replace(u"\u2019", "'").replace('\u2019', "'")

        # Need to put this state first due to things like West Virgina
        states_list = [state]
        states_list += [st for st in state_image_list]
        for st in states_list:
            for i in range(len(tweets)):
                # Remove State Names
                patterns = [re.compile(st+"'s", re.IGNORECASE),
                            re.compile(st+"s", re.IGNORECASE),
                            re.compile(st, re.IGNORECASE)]

                for pattern in patterns:
                    tweets[i] = pattern.sub(" ", tweets[i])
                    tweets[i] = tweets[i].replace("D.C.", "")

        tweet_text = " ".join(tweets)

        for i in range(int(len(tweets) / 60)):
            tweet_text += "Copyright_Grant_Hadlich_2022 the "

        tweets_total += " " + tweet_text

        create_image(tweet_text, img_path, word_cloud_path, date)

    # Now do USA
    word_cloud_path = dir + "/" + "US.png"
    img_path = f"./state_images/US.png"

    state_word_cloud["USA"] = word_cloud_path

    create_image(tweets_total, img_path, word_cloud_path, date, max_words=500)

    return state_word_cloud, tweet_count