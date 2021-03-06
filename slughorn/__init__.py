import logging.config
import os
import pickle

import click

from slughorn.processor import ExpressionExtractor, WordListGenerator, RuleGenerator
from slughorn.scraper import FacebookScraper, TwitterScraper
from slughorn.scraper import constants_factory
from slughorn.scraper.constants_factory import load_constants, reset_constants, constants_present, set_constants

here = os.path.dirname(__file__)
logging.config.fileConfig(os.path.join(here, 'logging.conf'))
log = logging.getLogger(__name__)


def check_for_constants():
    if not constants_present:
        if click.confirm('No constants found for Facebook scraping. Do you want to create it now?',
                         default=True):
            facebook_access_token = click.prompt('Please enter your Facebook access token', type=str)
            facebook_email = click.prompt('Please enter the email address for your Facebook account',
                                                       type=str)
            facebook_password = click.prompt(
                'Please enter the password for your Facebook account (Please use a '
                'dedicated account for this purpose. The password has to be stored in '
                'clear text)', type=str,
                hide_input=True, confirmation_prompt=True)
            set_constants(facebook_access_token, facebook_email, facebook_password)
            click.echo("Thank you! The constants were saved successfully. Let's continue ...")
        else:
            raise click.Abort()
    else:
        constants_factory.load_constants()


def start_facebook_scraper(user_name, case_id, output='', scrape_all=True, from_date=None, to_date=None):
    click.echo("Starting Facebook scraping for user '{}'. Why not get a tea? This could take some time!".format(
        user_name))
    if not output:
        output = "data/{}".format(case_id)
    check_for_constants()
    facebook_scraper = FacebookScraper.FacebookScraper(user_name=user_name, case_id=case_id)
    if scrape_all:
        facebook_scraper.scrape_all()
    elif from_date and to_date:
        click.echo("Please note: time frame scraping of Facebook is only available for public sites. "
                   "Private profiles will to be scraped as a whole.")
        facebook_scraper.scrape_timeframe(from_date, to_date)
    else:
        click.echo("No valid time frame or scrape_all flag for Facebook scraping. from_date and to_date need to be ")
    facebook_scraper.write_to_file(directory=output)
    return facebook_scraper.posts


def start_twitter_scraper(user_name, case_id, output='', scrape_all=True, from_date=None, to_date=None):
    click.echo("Starting Twitter scraping for user '{}'. Why not get a tea? This could take some time!".format(
        user_name))
    if not output:
        output = "data/{}".format(case_id)
    twitter_scraper = TwitterScraper.TwitterScraper(user_name=user_name, case_id=case_id)
    if scrape_all:
        twitter_scraper.scrape_all()
    elif from_date and to_date:
        twitter_scraper.scrape_timeframe(from_date, to_date)
    else:
        click.echo("No valid time frame or scrape_all flag for Twitter scraping.")
    twitter_scraper.write_to_file(directory=output)
    return twitter_scraper.tweets


def start_processing(post_list, case_id, language, output='', pickled=True, weight=0.5):
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    if not output:
        output = "data/{}".format(case_id)
    weight = float(weight)
    extractor = ExpressionExtractor.ExpressionExtractor(post_list, case_id, language)
    extractor.extract_words_and_numbers(weight)
    extractor.write_to_file(directory=output, pickled=pickled)
    return extractor.final_expressions


def start_wordlist_generation(expressions, case_id, output=''):
    if not output:
        output = "data/{}".format(case_id)
    generator = WordListGenerator.WordListGenerator(expressions, case_id)
    generator.generate_word_list()
    generator.write_to_file(directory=output)


def start_rule_generation(expressions, case_id, output=''):
    if not output:
        output = "data/{}".format(case_id)
    generator = RuleGenerator.RuleGenerator(expressions, case_id)
    generator.generate_rules()
    generator.write_to_file(directory=output)