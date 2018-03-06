import glob
import os
import pickle

import click

from slughorn import start_processing, start_twitter_scraper, start_facebook_scraper, start_password_generation
from slughorn.scraper import constants_factory

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
        constants_path = 'slughorn/scraper/constants.pkl'
        if not os.path.isfile(constants_path):
            click.echo("There are no constants to delete!")
        else:
            if click.confirm('Are you sure you want to delete the saved constants?',
                             default=False):
                constants_factory.reset_constants()

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
                    facebook_posts = start_facebook_scraper(facebook_username, case_id, output)
                else:
                    with open(file, 'rb') as f:
                        facebook_posts = pickle.load(f)
                post_list.extend(facebook_posts)
            if twitter_username:
                use_file, file = ask_for_existing_files('twitter', output)
                if not use_file:
                    click.echo("Starting Twitter scraping for user '{}'. Why not get a tea? This could take some time!".format(twitter_username))
                    twitter_tweets = start_twitter_scraper(twitter_username, case_id, output)
                else:
                    with open(file, 'rb') as f:
                        twitter_tweets = pickle.load(f)
                post_list.extend(twitter_tweets)

            if len(post_list) > 0:
                expression_list = start_processing(post_list, case_id, language, output, not txt, weight)
            else:
                click.echo("No posts found. Please try again ...")

        else:
            with open(file, 'rb') as f:
                expression_list = pickle.load(f)

        if len(expression_list) > 0:
            start_password_generation(expression_list, case_id, output)
            click.echo("slughorn finished. Happy cracking!")
        else:
            click.echo("No words found. Please try again ...")