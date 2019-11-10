import json
import operator
import os
import re
from itertools import islice
from csv import reader
import requests
import glob
import sys


def get_emojis(user):
    user.load_user_data()

    with open("data/emojidata/emoji_df.csv", mode="r", encoding="utf-8", newline="") as file:
        lines = reader(file)

        codes = {}

        for emoji in lines:
            for interest in user.interests:
                if re.search(f"\\b{interest}", emoji[1]) is not None:
                    print(interest, emoji[1])
                    if ":" not in emoji[1] and "," not in emoji[1]:
                        if interest not in codes:
                            codes[interest] = emoji[1]
                        else:
                            codes[interest] += ("," + emoji[1])

    uniq_emojis = []
    emoji_rank = {}
    for interest in codes:
        lines = codes[interest].split(",")
        for emoji in lines:
            emoji = emoji.replace(" ", "-")
            if emoji not in emoji_rank:
                emoji_rank[emoji] = user.interests[interest]
            else:
                emoji_rank[emoji] += user.interests[interest]
            if emoji not in uniq_emojis:
                uniq_emojis.append(emoji.lower())

    print(emoji_rank)
    user.add_emojis(emoji_rank)
    print(uniq_emojis)
    clean_old_emojis(user.username)
    for emoji in uniq_emojis:
        save_emoji(emoji, user.username)
        convert_to_png(emoji, user.username)


def save_emoji(emoji, username):
    directory = os.path.dirname(f"data/people/{username}/emojis/")
    try:
        os.makedirs(directory)
    except IOError as err:
        err = None

    svg = requests.get(f"https://api.iconify.design/twemoji:{emoji}.svg").text
    with open(f"data/people/{username}/emojis/{emoji}.svg", "w") as pic:
        pic.write(svg)


def clean_old_emojis(username):
    files = glob.glob(f"data/people/{username}/emojis/*.svg")
    for file in files:
        os.remove(file)

    files = glob.glob(f"data/people/{username}/emojis/*.png")
    for file in files:
        os.remove(file)


def convert_to_png(emoji, username):
    os.system(f'inkscape -z -e data/people/{username}/emojis/{emoji}.png -w 1024 -h 1024 data/people/{username}/emojis/{emoji}.svg')
