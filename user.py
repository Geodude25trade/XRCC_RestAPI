import operator
from abc import ABC, abstractmethod
from collections import OrderedDict
import re
import os
import json


class User(ABC):
    username = ""
    words = OrderedDict()
    interests = OrderedDict()
    tweets = ""
    emojis = OrderedDict()

    def __init__(self, username):
        self.username = username

    @staticmethod
    def get_top_n(data, num):
        top = {}
        for i in range(num):
            max_key = max(data.items(), key=operator.itemgetter(1))[0]
            print(max_key)
            top[max_key] = data[max_key]
            del data[max_key]
        return top

    @staticmethod
    def find_similar_interests(user1, user2, num_interests=10):
        common_interests = {}
        for interest in user1.interests:
            if interest in user2.interests:
                value = user1.interests[interest] + user2.interests[interest]
                common_interests[interest] = value
        # Select the top n interests
        return User.get_top_n(common_interests, num_interests)

    @staticmethod
    def top_n_interests(user1, num_interests=10):
        interests = {}
        for interest in user1.interests:
            value = user1.interests[interest]
            interests[interest] = value
        # Select the top n interests
        return User.get_top_n(interests, num_interests)

    def preprocess_data(self, text):
        if text is not None:
            self.tweets = " ".join(text)
        elif self.tweets is None:
            print("No tweets to process")
            return

        # Clean the text saving only letters and white space
        return re.sub(r"[^a-zA-Z\s]+", " ", self.tweets)

    @abstractmethod
    def process_data(self, clean):
        pass

    def find_words(self, text=None):
        # Clean the text, process the data in subclasses, then do postprocess stuff
        self.postprocess_data(self.process_data(self.preprocess_data(text)))

    def postprocess_data(self, raw_data):
        # Sort by score highest to lowest, Store, and Save the interests
        sorted_data = OrderedDict(sorted(raw_data.items(), key=lambda x: x[1], reverse=True))
        self.words = sorted_data
        self.interests = sorted_data
        self.save_user_data()

    def print_words(self):
        # Print the user's interests
        for word in self.words:
            if self.words[word] > 0:
                print(f"{word}: {self.words[word]}")

    def print_interests(self):
        # Print the user's interests
        for interest in self.interests:
            if self.interests[interest] > 0:
                print(f"{interest}: {self.interests[interest]}")

    def add_interests(self, interests):
        sorted_interests = OrderedDict(sorted(interests.items(), key=lambda x: x[1], reverse=True))
        self.interests = sorted_interests
        self.save_user_data()

    def add_emojis(self, emojis):
        sorted_emojis = OrderedDict(sorted(emojis.items(), key=lambda x: x[1], reverse=True))
        self.emojis = sorted_emojis
        self.save_user_data()

    def save_user_data(self):
        # Create object to store in JSON
        user_obj = {"username": self.username, "words": self.words,
                    "emojis": self.emojis, "interests": self.interests}
        tweets = {"tweets": self.tweets}
        # Try to make the directory first if it doesn't already exist
        directory = os.path.dirname(
            "data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json")
        tweets_dir = os.path.dirname("data/people/" + self.username + "/" + self.username + ".tweets.json")
        try:
            os.makedirs(directory)
        except IOError as err:
            print(err)
        try:
            os.makedirs(tweets_dir)
        except IOError as err:
            print(err)
        # Save the user interests to a JSON file
        if self.words is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json",
                          "w") as file:
                    json.dump(user_obj, file)
            except IOError as err:
                print(err)
        if self.tweets is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + ".tweets.json",
                          "w") as file:
                    json.dump(tweets, file)
            except IOError as err:
                print(err)

    def load_user_data(self):
        # Load the interests JSON and set to self.interests
        user_obj = {}
        tweets = {}
        try:
            with open("data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json",
                      "r") as data:
                user_obj = json.load(data)
        except IOError as err:
            print(err)
            try:
                with open("data/people/" + self.username + "/" + self.username + ".json", "r") as data:
                    user_obj = json.load(data)
            except IOError as err:
                print(err)
                return False
        try:
            with open("data/people/" + self.username + "/" + self.username + ".tweets.json", "r") as tweet_data:
                tweets = json.load(tweet_data)
        except IOError as err:
            print(err)

        # Assign values from load to fields
        if 'usersname' in user_obj:
            self.username = user_obj["username"]
        if 'words' in user_obj:
            self.words = user_obj["words"]
        if 'interests' in user_obj:
            self.interests = user_obj["interests"]
        if 'tweets' in tweets:
            print("GOT THE TWEETS")
            self.tweets = tweets["tweets"]
        elif 'tweets' in user_obj:
            print("GOT THE TWEETS")
            self.tweets = user_obj["tweets"]
        else:
            print("There seem to be no tweets")
        if 'emojis' in user_obj:
            self.emojis = user_obj["emojis"]
        return True
