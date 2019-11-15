from flask import Flask, request, send_file
from flask_restplus import Resource, Api
import analyzeUser
from user import User
from chiUser import ChiUser
from empUser import EmpUser
from wfcUser import WFCUser
import emoji2vector
import os
import getEmojis

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


class UserDataRequest(Resource):
    def post(self):
        settings = request.get_json()
        algorithm = settings['algorithm']
        username = settings['username']
        new_tweets = settings['newtweets']
        num_tweets = settings['numtweets']
        algorithm = algorithm.lower()
        if algorithm is not None and username is not None:
            if algorithm in "chi-squared":
                person = ChiUser(username)
            if algorithm in "wfc":
                person = WFCUser(username)
            if algorithm in "empath":
                person = EmpUser(username)
            analyzeUser.analyze_user(person, num_tweets, new_tweets)
            top_interests = User.top_n_interests(person)
            for interest in top_interests:
                count = top_interests[interest]
                top_interests[interest] = {}
                top_interests[interest]['count'] = count
                emoji = emoji2vector.find_closest_emoji(interest)
                if emoji is not None:
                    top_interests[interest]['emoji'] = emoji[0][0]
                    top_interests[interest]['emoji_score'] = emoji[0][1]

            return top_interests
        return "<h1>Error</h1>"


class UserComparisonRequest(Resource):
    def post(self):
        settings = request.get_json()
        algorithm = settings['algorithm']
        user1 = settings['user1']
        user2 = settings['user2']
        new_tweets = settings['newtweets']
        num_tweets = settings['numtweets']
        algorithm = algorithm.lower()
        if algorithm is not None and user1 is not None and user2 is not None:
            if algorithm in "chi-squared":
                user1 = ChiUser(user1)
                user2 = ChiUser(user2)
            if algorithm in "wfc":
                user1 = WFCUser(user1)
                user2 = WFCUser(user2)
            if algorithm in "empath":
                user1 = EmpUser(user1)
                user2 = EmpUser(user2)
            analyzeUser.analyze_user(user1, num_tweets, new_tweets)
            analyzeUser.analyze_user(user2, num_tweets, new_tweets)
            similar_interests = User.find_similar_interests(user1, user2)
            for interest in similar_interests:
                count = similar_interests[interest]
                similar_interests[interest] = {}
                similar_interests[interest]['count'] = count
                emoji = emoji2vector.find_closest_emoji(interest)
                if emoji is not None:
                    similar_interests[interest]['emoji'] = emoji[0][0]
                    similar_interests[interest]['emoji_score'] = emoji[0][1]
            return similar_interests
        return "<h1>Error</h1>"


class EmojiImageRequest(Resource):
    def post(self):
        settings = request.get_json()
        emoji = settings['emoji']
        filename = os.path.dirname(f"data/emojis/{emoji}.png")
        if os.path.exists(filename):
            return send_file(f"data/emojis/{emoji}.png", mimetype="image/png")
        else:
            getEmojis.get_emojis(emoji)
            return send_file(f"data/emojis/{emoji}.png", mimetype="image/png")


api.add_resource(UserDataRequest, '/user/')
api.add_resource(UserComparisonRequest, '/compare/')
api.add_resource(EmojiImageRequest, '/emojis/')

if __name__ == '__main__':
    app.run()
