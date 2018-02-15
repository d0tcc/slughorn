from lib.scraper import FacebookScraper, TwitterScraper
from lib.processor import ExpressionExtractor, PasswordGenerator

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
    constants_path = 'lib/scraper/constants.py'
    if not os.path.isfile(constants_path):
        if click.confirm('You need to create a constants.py file for Facebook scraping. Do you want to create it now?',
                         default=True):
            constants = {}
            constants['facebook_access_token'] = click.prompt('Please enter your Facebook access token', type=str)
            constants['facebook_email'] = click.prompt('Please enter the email address for your Facebook account',
                                                       type=str)
            constants['facebook_password'] = click.prompt(
                'Please enter the password for your Facebook account (Please use a '
                'dedicated account for this purpose. The password has to be stored in '
                'clear text)', type=str,
                hide_input=True, confirmation_prompt=True)
            with open('scraper/constants.py', 'w+') as f:
                f.write('constants = ' + str(constants))
            click.echo("Thank you! The file constants.py was created successfully. Let's continue ...")


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


def start_processing(post_list, output, case_id, pickled):
    extractor = ExpressionExtractor.ExpressionExtractor(post_list, case_id)
    extractor.extract_words_and_numbers()
    extractor.write_to_file(directory=output, pickled=pickled)
    return extractor.final_expressions


def start_password_generation(word_list, output, case_id):
    generator = PasswordGenerator.PasswordGenerator(word_list, case_id)
    generator.generate_passwords()
    generator.write_to_file(directory=output)


@click.command()
@click.option('-c', '--case_id', required=True, help="Required Case ID")
@click.option('-f', '--facebook_username', default='', help="Target's Facebook user name")
@click.option('-t', '--twitter_username', default='', help="Target's Twitter user name without leading @")
@click.option('-o', '--output', default='', help="Path to output directory")
@click.option('--txt', is_flag=True, help="Save intermediate results as txt instead of pickle (results cannot be reused)")
def cli(case_id, facebook_username, twitter_username, output, txt):
    if not (facebook_username or twitter_username):
        click.echo("Please specify at least one username. If you need help try 'slughorn --help'")
    else:
        click.echo(ascii_slug)

        if not output:
            output = 'data/{}'.format(case_id)

        expression_list = []

        use_file, file = ask_for_existing_files('expressions', output)
        if not use_file:

            post_list = []

            if facebook_username:
                use_file, file = ask_for_existing_files('facebook', output)
                if not use_file:
                    click.echo("Starting Facebook scraping for user '{}'".format(facebook_username))
                    facebook_posts = start_facebook_scraper(facebook_username, output, case_id)
                else:
                    facebook_posts = pickle.load(open(file, 'rb'))
                post_list.extend(facebook_posts)
            if twitter_username:
                use_file, file = ask_for_existing_files('twitter', output)
                if not use_file:
                    click.echo("Starting Twitter scraping for user '{}'".format(twitter_username))
                    twitter_tweets = start_twitter_scraper(twitter_username, output, case_id)
                else:
                    twitter_tweets = pickle.load(open(file, 'rb'))
                post_list.extend(twitter_tweets)

            if len(post_list) > 0:
                expression_list = start_processing(post_list, output, case_id, not txt)
            else:
                click.echo("No posts found. Please try again ...")

        else:
            expression_list = pickle.load(open(file, 'rb'))

        if len(expression_list) > 0:
            start_password_generation(expression_list, output, case_id)
            click.echo("slughorn finished. Happy cracking!")
        else:
            click.echo("No words found. Please try again ...")
