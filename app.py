from flask import Flask, request
from flask_restplus import Resource, Api
import analyzeUser
from user import User
from chiUser import ChiUser
from empUser import EmpUser
from wfcUser import WFCUser

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
            return person.interests
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
            return similar_interests
        return "<h1>Error</h1>"


api.add_resource(UserDataRequest, '/user/')
api.add_resource(UserComparisonRequest, '/compare/')

if __name__ == '__main__':
    app.run()
