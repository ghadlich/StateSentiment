#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021 Grant Hadlich
#
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
from twitterutils.twitterutils import tweet
from utils.utils import pull_tweets
from utils.plot_states import plot_state_sentiment
from utils.utils import parse_tweets
from utils.utils import create_composite
from time import sleep
from datetime import datetime
from sentimentmodels.get_models import get_models
from collections import defaultdict

if __name__ == "__main__":
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")

    print("Loading Models")
    models = get_models()
    print("Loaded Models: " + str([model.name() for model in models]))

    print("Pulling Tweets from Twitter")
    directory = pull_tweets(date, 1000)

    model_data = dict()
    model_tweet_content = dict()
    model_filenames = dict()

    for model in models:
        print("Running Model: " + model.name())
        model_type = model.model_name_long()
        data, top_state, _ = parse_tweets(model, directory)

        filename = plot_state_sentiment(data, model.name(), date, directory)
        model_filenames[model.name()] = filename
        top_state = "#"+top_state.replace(" ", "")
        model_data[model.name()] = data

        text = f"I analyzed the sentiment on Twitter for each state + DC from the last week using a {model_type}."
        text += f"\nWhich state had the most positive mentions this week? The Answer is: {top_state}!"
        text += f"\n#NLP #Python #GrantBot"
        model_tweet_content[model.name()] = text

    # Create Composite Model
    data, top_state = create_composite(model_data)
    filename = plot_state_sentiment(data, "Composite", date, directory)
    top_state = "#"+top_state.replace(" ", "")

    print("Creating Initial Tweet")
    text = f"Which state had the most positive mentions this week? The Answer is: {top_state}!"
    text += "\nThis was based on a composite model I created which analyzed 50,000+ Tweets. In the replies are a few of the raw models."
    text += "\nGitHub: https://github.com/ghadlich/StateSentiment"
    text += "\n#NLP #Python"
    previous_id = tweet(text, image_path=filename, enable_tweet=True)

    for model_name in model_tweet_content:
        print("Tweeting Model: " + model_name)
        previous_id = tweet(model_tweet_content[model_name], image_path=model_filenames[model_name], in_reply_to_status_id=previous_id, enable_tweet=True)

    print("Completed Tweets")

    #while True:
    #    sleep(3600*12-10)
