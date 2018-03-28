import glob
import os
import pickle

import click

from slughorn import start_processing, start_twitter_scraper, start_facebook_scraper, start_wordlist_generation, \
    start_rule_generation, set_constants
from slughorn.scraper.constants_factory import constants_present, reset_constants

ascii_slug = """
        _             _                      
       | |           | |                     
    ___| |_   _  __ _| |__   ___  _ __ _ __  
   / __| | | | |/ _` | '_ \ / _ \| '__| '_ \ 
   \__ \ | |_| | (_| | | | | (_) | |  | | | |
   |___/_|\__,_|\__, |_| |_|\___/|_|  |_| |_|
                 __/ |                 v.0.2 
                |___/                        
"""


def ask_for_existing_files(type, directory):
    files = glob.glob(os.path.join(directory, '{}_*.pkl'.format(type)))
    if not files:
        return False, None
    else:
        file = files[0]
        use_file = click.confirm('An existing {} file "{}" for this case was found. '
                             'Do you want to use it?'.format(type, file), default=True)
        return use_file, file


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
        if not constants_present():
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

        expression_dict = dict()

        use_file, file = ask_for_existing_files('expressions', output)
        if not use_file:

            post_list = []

            if facebook_username:
                use_file, file = ask_for_existing_files('facebook', output)
                if not use_file:
                    facebook_posts = start_facebook_scraper(facebook_username, case_id, output)
                else:
                    with open(file, 'rb') as f:
                        facebook_posts = pickle.load(f)
                post_list.extend(facebook_posts)
            if twitter_username:
                use_file, file = ask_for_existing_files('twitter', output)
                if not use_file:
                    twitter_tweets = start_twitter_scraper(twitter_username, case_id, output)
                else:
                    with open(file, 'rb') as f:
                        twitter_tweets = pickle.load(f)
                post_list.extend(twitter_tweets)

            if len(post_list) > 0:
                expression_dict = start_processing(post_list, case_id, language, output, not txt, weight)
            else:
                click.echo("No posts found. Please try again ...")

        else:
            with open(file, 'rb') as f:
                expression_dict = pickle.load(f)

        if len(expression_dict) > 0:
            start_wordlist_generation(expression_dict, case_id, output)
            start_rule_generation(expression_dict, case_id, output)
            click.echo("slughorn finished. Happy cracking!")
        else:
            click.echo("No words found. Please try again ...")


@click.command()
@click.option('--delete', is_flag=True, help="Just delete constants, ignore other parameters")
@click.option('--fb_api_key', help="Key for Facebook Graph API")
@click.option('--fb_email', help="Email address of your scraping facebook account")
@click.option('--fb_password', help="Password of your scraping facebook account")
def reset(delete, fb_api_key, fb_email, fb_password):

    if delete:
        if constants_present():
            reset_constants()
            click.echo("Constants deleted!")
        else:
            click.echo("No constants found!")
    elif fb_api_key and fb_password and fb_email:
        if not constants_present():
            set_constants(fb_api_key, fb_email, fb_password)
            click.echo("Constants set!")
        else:
            if click.confirm('Constants file found. Are you sure you want to delete the saved constants?',
                             default=False):
                reset_constants()
                set_constants(fb_api_key, fb_email, fb_password)
                click.echo("Constants set!")
    else:
        click.echo("Error: Missing options, --delete OR (--fb_api_key AND --fb_email AND --fb_password)")
