import click
import os
from scraper import FacebookScraper, TwitterScraper
import logging
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


def check_for_constants():
    constants_path = 'scraper/constants.py'
    if not os.path.isfile(constants_path):
        if click.confirm('You need to create a constants.py file for Facebook scraping. Do you want to create it now?', default=True):
            constants = {}
            constants['facebook_access_token'] = click.prompt('Please enter your Facebook access token', type=str)
            constants['facebook_email'] = click.prompt('Please enter the email address for your Facebook account', type=str)
            constants['facebook_password'] = click.prompt('Please enter the password for your Facebook account (Please use a '
                                             'dedicated account for this purpose. The password has to be stored in '
                                             'clear text)', type=str,
                                             hide_input=True, confirmation_prompt=True)
            with open('scraper/constants.py', 'w+') as f:
                f.write('constants = ' + str(constants))
            click.echo("Thank you! The file constants.py was created successfully. Let's continue ...")


def start_facebook_scraper(user_name, output):
    check_for_constants()
    facebook_scraper = FacebookScraper.FacebookScraper(user_name, 1234)
    facebook_scraper.scrape_all()
    facebook_scraper.write_to_file(output)


def start_twitter_scraper(user_name, output):
    twitter_scraper = TwitterScraper.TwitterScraper(user_name, 1234)
    twitter_scraper.scrape_all()
    twitter_scraper.write_to_file(output)


@click.command()
@click.option('-f', '--facebook', default='', help="Target's Facebook user name")
@click.option('-t', '--twitter', default='', help="Target's Twitter user name without leading @")
@click.option('-o', '--output', default='', help="Path to output directory")
def cli(facebook, twitter, output):
    click.echo(ascii_slug)
    if facebook:
        click.echo("Starting Facebook scraping for user '{}'".format(facebook))
        start_facebook_scraper(facebook, output)
    if twitter:
        click.echo("Starting Twitter scraping for user '{}'".format(twitter))
        start_twitter_scraper(twitter, output)