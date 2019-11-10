from user import User
from chiUser import ChiUser
import json
import os.path
from tweepy.error import TweepError


def create_data():
    with open('data/handles.json', 'r') as path:
        people = list(json.load(path))

    users = {}
    words = {}
    for person in people:
        print(person)
        person = ChiUser(person)
        person.load_user_data()
        person.find_words()
        if len(person.words) <= 0:
            continue
        # user.find_interests()
        users[person.username] = {}
        users[person.username]['words'] = person.words
        users[person.username]['probability'] = 0.0
        for word in person.words:
            if 'totaly' not in users[person.username]:
                users[person.username]['totaly'] = person.words[word]
            else:
                users[person.username]['totaly'] += person.words[word]
            if word not in words:
                words[word] = {}
            if 'totalx' not in words[word]:
                words[word]['totalx'] = person.words[word]
            else:
                words[word]['totalx'] += person.words[word]
            words[word]['probability'] = 0.0

    model = {'users': users, 'words': words}
    save_model(model)


def compute_table():
    model = open_model()

    # Reset the model's total
    model['totalxy'] = 0

    # Make sure the total is the same for both x and y axis of the model
    test = 0
    for person in model['users']:
        model['totalxy'] += model['users'][person]['totaly']
    for word in model['words']:
        test += model['words'][word]['totalx']
    print(f"{test} vs. {model['totalxy']}")

    # If they are the same...
    if test == model['totalxy']:
        # Calculate all peoples' probabilities
        for person in model['users']:
            prob = float(float(model['users'][person]['totaly']) / float(model['totalxy']))
            model['users'][person]['probability'] = prob
        # Calculate all words' probabilities
        for word in model['words']:
            prob = float(float(model['words'][word]['totalx']) / float(model['totalxy']))
            model['words'][word]['probability'] = prob
    save_model(model)


def add_user(person):
    model = open_model()

    # If the person is not in the model...
    if person.username not in model['users']:
        # print("They were not in the table")

        # Add the person to the model
        model['users'][person.username] = {}

        # Update the totals in the table for words and the new user (totalx, totaly)
        update_table_totals(person, model)
    # If the user is not in the model...
    else:
        # print("They were in the table")

        # If the user does not have the exact same data as before...
        if set(person.words.keys()) != set(model['users'][person.username]['words'].keys()) or set(
                person.words.values()) != set(model['users'][person.username]['words'].values()):

            # print("They had different values from the ones in the table")

            # Subtract their previous values...
            for word in model['users'][person.username]['words']:
                model['words'][word]['totalx'] -= model['users'][person.username]['words'][word]
            # And add their new values
            update_table_totals(person, model)

    save_model(model)
    compute_table()


def calculate_user(person):
    model = open_model()

    # If the person is in the model
    if person.username in model['users']:

        # Set up needed variables
        person_prob = model['users'][person.username]['probability']
        grand_total = model['totalxy']
        interests = {}

        # For each word, calculate its Chi-Squared Contribution
        for word in person.words:
            word_prob = model['words'][word]['probability']

            expected = word_prob * person_prob * grand_total
            observed = model['users'][person.username]['words'][word]

            # CSC = ( (observed - expected) ^ 2 ) / expected
            csc = ((float(observed) - float(expected)) ** 2) / expected
            interests[word] = csc

        # Add the interests to the user object and print the interests
        person.add_interests(interests)
        # person.print_interests()


def save_model(model):
    with open('data/chiSqModel.json', 'w') as file:
        json.dump(model, file)


def open_model():
    with open('data/chiSqModel.json', 'r') as file:
        model = json.load(file)
    return model


def update_table_totals(person, model):

    # Reset the user's data to 0 and their words to their frequency count
    model['users'][person.username]['words'] = person.words
    model['users'][person.username]['probability'] = 0.0
    model['users'][person.username]['totaly'] = 0

    # Update the totals for each word the user has
    for word in person.words:
        model['users'][person.username]['totaly'] += person.words[word]
        if word not in model['words']:
            model['words'][word] = {}
        if 'totalx' not in model['words'][word]:
            model['words'][word]['totalx'] = person.words[word]
        else:
            model['words'][word]['totalx'] += person.words[word]
        model['words'][word]['probability'] = 0.0


def retrain_model():
    with open('data/handles.json', 'r') as path:
        people = list(json.load(path))
    for person in people:
        user = ChiUser(person)
        user.load_user_data()
        user.find_words()
        add_user(user)
    compute_table()


# if __name__ == "__main__":
    # retrain_model()
    # compute_table()
    # if not os.path.exists('data/chiSqModel.json'):
    #     create_data()
    #     compute_table()
