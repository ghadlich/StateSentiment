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
from utils.utils import create_word_clouds
from time import sleep
from datetime import datetime
from collections import defaultdict
from tqdm.auto import tqdm

if __name__ == "__main__":
    #sleep(3600*11)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    date = "2021-06-26"

    states = create_word_clouds(date)

    usa_img = states["USA"]
    del states["USA"]

    text = f"Each week I pull ~51000 tweets on US State mentions. Here's a collection of word clouds from tweets pulled on {date}. Each state + DC can be found in the replies!"
    text += f"\n#Python #USA #WordCloud #TwitterData"

    previous_id = tweet(text, image_path=usa_img, enable_tweet=True)

    for state in tqdm(states, total=len(states), position=0, leave=True):
        clipped = state.replace(" ", "")
        text = f"Each week I pull ~51000 tweets on US State mentions. Here's the word cloud for #{clipped} from tweets pulled on {date}!"
        text += f"\n#Python #WordCloud #TwitterData"
        previous_id = tweet(text, image_path=states[state], in_reply_to_status_id=previous_id, enable_tweet=True)
        sleep(1)

    
