import logging.config
import os
import pickle

import click

from slughorn.processor import ExpressionExtractor, PasswordGenerator
from slughorn.scraper import FacebookScraper, TwitterScraper
from slughorn.scraper import constants_factory
from slughorn.scraper.constants_factory import load_constants, reset_constants

logging.config.fileConfig('logs/logging.conf')
log = logging.getLogger(__name__)


def check_for_constants():
    constants_path = 'slughorn/scraper/constants.pkl'
    if not os.path.isfile(constants_path):
        if click.confirm('No constants found for Facebook scraping. Do you want to create it now?',
                         default=True):
            constants = dict()
            constants['facebook_access_token'] = click.prompt('Please enter your Facebook access token', type=str)
            constants['facebook_email'] = click.prompt('Please enter the email address for your Facebook account',
                                                       type=str)
            constants['facebook_password'] = click.prompt(
                'Please enter the password for your Facebook account (Please use a '
                'dedicated account for this purpose. The password has to be stored in '
                'clear text)', type=str,
                hide_input=True, confirmation_prompt=True)
            with open(constants_path, 'wb') as f:
                pickle.dump(constants, f)
            click.echo("Thank you! The constants were saved successfully. Let's continue ...")
            constants_factory.load_constants()
        else:
            raise click.Abort()
    else:
        constants_factory.load_constants()


def start_facebook_scraper(user_name, case_id, output=''):
    if not output:
        output = "data/{}".format(case_id)
    check_for_constants()
    facebook_scraper = FacebookScraper.FacebookScraper(user_name=user_name, case_id=case_id)
    facebook_scraper.scrape_all()
    facebook_scraper.write_to_file(directory=output)
    return facebook_scraper.posts


def start_twitter_scraper(user_name, case_id, output=''):
    if not output:
        output = "data/{}".format(case_id)
    twitter_scraper = TwitterScraper.TwitterScraper(user_name=user_name, case_id=case_id)
    twitter_scraper.scrape_all()
    twitter_scraper.write_to_file(directory=output)
    return twitter_scraper.tweets


def start_processing(post_list, case_id, language, output='', pickled=True, weight=0.5):
    if not output:
        output = "data/{}".format(case_id)
    weight = float(weight)
    extractor = ExpressionExtractor.ExpressionExtractor(post_list, case_id, language)
    extractor.extract_words_and_numbers(weight)
    extractor.write_to_file(directory=output, pickled=pickled)
    return extractor.final_expressions


def start_password_generation(word_list, case_id, output=''):
    if not output:
        output = "data/{}".format(case_id)
    generator = PasswordGenerator.PasswordGenerator(word_list, case_id)
    generator.generate_passwords()
    generator.write_to_file(directory=output)
