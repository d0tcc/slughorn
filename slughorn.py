from lib.scraper import FacebookScraper, TwitterScraper
from lib.processor import ExpressionExtractor, PasswordGenerator
from lib.scraper.constants_factory import load_constants, reset_constants

import click
import os
import glob
import pickle
import logging.config

logging.config.fileConfig('logs/logging.conf')
log = logging.getLogger(__name__)

ascii_slug = """
        _             _                      
       | |           | |                     
    ___| |_   _  __ _| |__   ___  _ __ _ __  
   / __| | | | |/ _` | '_ \ / _ \| '__| '_ \ 
   \__ \ | |_| | (_| | | | | (_) | |  | | | |
   |___/_|\__,_|\__, |_| |_|\___/|_|  |_| |_|
                 __/ |                 v.0.1 
                |___/                        
"""


def check_for_constants():
    constants_path = 'lib/scraper/constants.pkl'
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
            load_constants()
        else:
            raise click.Abort()
    else:
        load_constants()


def ask_for_existing_files(type, directory):
    files = glob.glob(os.path.join(directory, '{}_*.pkl'.format(type)))
    if not files:
        return False, None
    else:
        file = files[0]
        use_file = click.confirm('An existing {} file "{}" for this case was found. '
                             'Do you want to use it?'.format(type, file), default=True)
        return use_file, file


def start_facebook_scraper(user_name, output, case_id):
    check_for_constants()
    facebook_scraper = FacebookScraper.FacebookScraper(user_name=user_name, case_id=case_id)
    facebook_scraper.scrape_all()
    facebook_scraper.write_to_file(directory=output)
    return facebook_scraper.posts


def start_twitter_scraper(user_name, output, case_id):
    twitter_scraper = TwitterScraper.TwitterScraper(user_name=user_name, case_id=case_id)
    twitter_scraper.scrape_all()
    twitter_scraper.write_to_file(directory=output)
    return twitter_scraper.tweets


def start_processing(post_list, language, output, case_id, pickled, weight):
    weight = float(weight)
    extractor = ExpressionExtractor.ExpressionExtractor(post_list, case_id, language)
    extractor.extract_words_and_numbers(weight)
    extractor.write_to_file(directory=output, pickled=pickled)
    return extractor.final_expressions


def start_password_generation(word_list, output, case_id):
    generator = PasswordGenerator.PasswordGenerator(word_list, case_id)
    generator.generate_passwords()
    generator.write_to_file(directory=output)


def validate_weight(ctx, param, value):
    try:
        weight = float(value)
        if weight < 0.0 or weight > 1.0:
            raise click.BadParameter('Weight needs to be a value between 0.0 and 1.0')
        return weight
    except ValueError:
        raise click.BadParameter('Weight needs to be a value between 0.0 and 1.0')


@click.command()
@click.option('-c', '--case_id', required=True, help="Case ID")
@click.option('-f', '--facebook_username', default='', help="Target's Facebook user name")
@click.option('-t', '--twitter_username', default='', help="Target's Twitter user name without leading @")
@click.option('-l', '--language', default='de', help="Expected language of postings, if detection fails (default: de)")
@click.option('-o', '--output', default='', help="Path to output directory")
@click.option('-w', '--weight', callback=validate_weight, default='0.5', help="Weight for the exceptionalism influencing the score (default: 0.5)")
@click.option('--txt', is_flag=True, help="Save intermediate results as txt instead of pickle (results cannot be reused)")
@click.option('--delete_constants', is_flag=True, help="Delete the saved constants (including credentials)")
def cli(case_id, facebook_username, twitter_username, language, output, weight, txt, delete_constants):
    click.echo(ascii_slug)

    if delete_constants:
        constants_path = 'lib/scraper/constants.pkl'
        if not os.path.isfile(constants_path):
            click.echo("There are no constants to delete!")
        else:
            if click.confirm('Are you sure you want to delete the saved constants?',
                             default=False):
                reset_constants()

    if not (facebook_username or twitter_username):
        click.echo("Please specify at least one username. If you need help try 'slughorn --help'")
    else:

        if not output:
            output = 'data/{}'.format(case_id)

        expression_list = []

        use_file, file = ask_for_existing_files('expressions', output)
        if not use_file:

            post_list = []

            if facebook_username:
                use_file, file = ask_for_existing_files('facebook', output)
                if not use_file:
                    click.echo("Starting Facebook scraping for user '{}'. Why not get a tea? This could take some time!".format(facebook_username))
                    facebook_posts = start_facebook_scraper(facebook_username, output, case_id)
                else:
                    with open(file, 'rb') as f:
                        facebook_posts = pickle.load(f)
                post_list.extend(facebook_posts)
            if twitter_username:
                use_file, file = ask_for_existing_files('twitter', output)
                if not use_file:
                    click.echo("Starting Twitter scraping for user '{}'. Why not get a tea? This could take some time!".format(twitter_username))
                    twitter_tweets = start_twitter_scraper(twitter_username, output, case_id)
                else:
                    with open(file, 'rb') as f:
                        twitter_tweets = pickle.load(f)
                post_list.extend(twitter_tweets)

            if len(post_list) > 0:
                expression_list = start_processing(post_list, language, output, case_id, not txt, weight)
            else:
                click.echo("No posts found. Please try again ...")

        else:
            with open(file, 'rb') as f:
                expression_list = pickle.load(f)

        if len(expression_list) > 0:
            start_password_generation(expression_list, output, case_id)
            click.echo("slughorn finished. Happy cracking!")
        else:
            click.echo("No words found. Please try again ...")
