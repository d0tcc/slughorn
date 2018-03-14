import os
import pickle

constants = dict()
here = os.path.dirname(__file__)
constants_path = os.path.join(here, 'constants.pkl')


def load_constants():
    global constants
    with open(constants_path, 'rb') as f:
        constants = pickle.load(f)


def set_constants(facebook_access_token, facebook_email, facebook_password):
    global constants
    constants['facebook_access_token'] = facebook_access_token
    constants['facebook_email'] = facebook_email
    constants['facebook_password'] = facebook_password
    with open(constants_path, 'wb') as f:
        pickle.dump(constants, f)


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


def constants_present():
    if os.path.isfile(constants_path):
        return True
    else:
        return False
