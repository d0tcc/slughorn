from lib.scraper import FacebookScraper, TwitterScraper
from lib.processor import WordExtractor

import click
import os
import logging.config

logging.config.fileConfig('logs/logging.conf')
log = logging.getLogger(__name__)

ascii_slug = """

                  /|                                        
                 |_|                                       
                 / |                                       
           -.-.  | |   -.-.                                
          -    ` |_|  -    `                                
          -  o / | |  - o  /                                
           `::´  | |   `::´                                
            ::  |__|    ::                                  
           .::-./``/....::....                            
        .-.`    /  |          `.                             
       :`                     :                             
      -.                       :                            
      /                        /                            
      :                        :                            
     -.                        ..                           
     :                 `       `:                           
     /                 .`       :                           
     /               .--        /                           
     /    /       ./ymN.         /                           
     :   /...----/MMMMd         :                           
     /       MMMMMMMMMM+        /                           
     :       MMMMMMMMMMd        /                           
     :       MMMM:::::dM        /                           
     `       /MN.......         :                           
     -        `                `/......_,                  
     .                          .        |              
`--`-.                          `        |                
/                                     ___...............   
`                                                       `.-
 `..`....................................................-`
        _             _                      
       | |           | |                     
    ___| |_   _  __ _| |__   ___  _ __ _ __  
   / __| | | | |/ _` | '_ \ / _ \| '__| '_ \ 
   \__ \ | |_| | (_| | | | | (_) | |  | | | |
   |___/_|\__,_|\__, |_| |_|\___/|_|  |_| |_|
                 __/ |                       
                |___/                        
"""


def check_for_constants( ):
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


def start_processing(post_list, output, case_id):
    extractor = WordExtractor.WordExtractor(post_list, case_id)
    extractor.extract_words()
    extractor.write_to_file(directory=output)
    return extractor.final_word_list


@click.command()
@click.option('-c', '--case_id', required=True, help="Required Case ID")
@click.option('-f', '--facebook_username', default='', help="Target's Facebook user name")
@click.option('-t', '--twitter_username', default='', help="Target's Twitter user name without leading @")
@click.option('-o', '--output', default='', help="Path to output directory")
def cli(case_id, facebook_username, twitter_username, output):
    click.echo(ascii_slug)

    post_list = []

    if facebook_username:
        click.echo("Starting Facebook scraping for user '{}'".format(facebook_username))
        post_list.extend(start_facebook_scraper(facebook_username, output, case_id))
    if twitter_username:
        click.echo("Starting Twitter scraping for user '{}'".format(twitter_username))
        post_list.extend(start_twitter_scraper(twitter_username, output, case_id))

    word_list = start_processing(post_list, output, case_id)
    # password_list = start_password_generation(word_list)
