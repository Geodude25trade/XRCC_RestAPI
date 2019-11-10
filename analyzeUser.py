import argparse
from empUser import EmpUser
from chiUser import ChiUser
import twitterHandler
from getEmojis import get_emojis
import userTableGenerator
import sys


def analyze_user(person, num_of_tweets=2000, force_new_tweets=False, emojis=False):
    tweets = None

    # Check for successful load of user data
    if not person.load_user_data():
        force_new_tweets = True
    elif len(person.tweets) <= 0:
        force_new_tweets = True

    # Check if we are forcing the system to get new tweets
    if force_new_tweets:
        if num_of_tweets > 0:
            print(f"Grabbing tweets for {person.username}")
            tweets = twitterHandler.get_tweets(person.username, num_of_tweets)

    # Do the analysis
    print(f"Analyzing tweets for {person.username}")
    person.find_words(tweets)
    # user.print_words()
    if isinstance(person, ChiUser):
        print(f"Working statistical analysis for {person.username}")
        userTableGenerator.add_user(person)
        userTableGenerator.calculate_user(person)
    # user.print_interests()
    if emojis:
        print(f"Getting emojis for {person.username}")
        get_emojis(person)
    return person


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="analyzeUser",
                                     description="Analyze the given Twitter user")

    parser.add_argument("username",
                        type=str,
                        help="The username of the Twitter user to analyze")
    parser.add_argument("tweet_num",
                        type=int,
                        nargs="?",
                        default=2000,
                        help="The number of Tweets to collect and analyze")
    parser.add_argument("-a",
                        "--analyzer",
                        action="store",
                        type=str,
                        nargs="?",
                        default="wfc",
                        const="empath",
                        help="Use the empath version of interest extraction (default: Word Frequency Counter analyzer)")
    parser.add_argument("-f",
                        "--force-get-tweets",
                        dest="force",
                        action="store_true",
                        help="Force the system to retrieve new tweets")
    parser.add_argument("-e",
                        "--emojis",
                        dest="emojis",
                        action="store_true",
                        help="Get emojis for the analyzed user")

    args = parser.parse_args()
    user = None
    if args.analyzer == "empath":
        user = EmpUser(args.username)
    elif args.analyzer == "wfc":
        user = ChiUser(args.username)
    else:
        user = ChiUser(args.username)

    analyze_user(user, args.tweet_num, args.force, args.emojis)
