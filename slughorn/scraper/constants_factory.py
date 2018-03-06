import os
import pickle

constants = dict()
constants_path = 'slughorn/scraper/constants.pkl'


def load_constants():
    global constants
    with open(constants_path, 'rb') as f:
        constants = pickle.load(f)


def reset_constants():
    global constants
    os.remove(constants_path)
    constants = dict()


def get_facebook_token():
    global constants
    return constants.get('facebook_access_token', '')


def get_facebook_email():
    global constants
    return constants.get('facebook_email', '')


def get_facebook_password():
    global constants
    return constants.get('facebook_password', '')
