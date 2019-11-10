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


api.add_resource(UserDataRequest, '/user/')

if __name__ == '__main__':
    app.run()
