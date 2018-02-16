from lib.scraper.webdriver.TwitterWebdriver import *

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import click_spinner
import pickle
import logging

log = logging.getLogger('slughorn')

#r = redis.StrictRedis(host='localhost', port=6379, db=0)

class TwitterScraper:
    """
    A TwitterScraper object represents one attempt to retrieve tweets of a user.
    """

    def __init__(self, user_name, case_id):
        """
        Init function of the TwitterScraper object.

        Initializes a TwitterScraper object, containing a given user_name and case_number.
        Based on the user_name the join_date is being retrieved with the method find_join_date().
        Furthermore an empty list of tweets and the webdriver is initialized.

        :param user_name: User name of the owner of the Twitter profile
        :param case_id: String representation of the case number
        """
        self.user_name = user_name
        self.case_id = case_id
        self.join_date = self.find_join_date()
        self.tweets = []

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

    def scrape_all(self):
        """
        Scrape all tweets.
    
        Scrape all tweets of the user which name is provided in self.user_name and saves them in self.tweets. Calls 
        self.scrape_timeframe with the users join date and today's date.
    
        :return: Number of scraped tweets
    
        """
        today = datetime.now()
        with click_spinner.spinner():
            return self.scrape_timeframe(self.join_date, today)

    def scrape_timeframe(self, from_date, to_date):
        """
        Scrape specific time frame.

        Scrape all tweets of the user which name is provided in self.user_name in a given time frame and saves them 
        in self.tweets.
        Uses TwitterWebdriver to retrieve the tweets.

        :param from_date: start date of time frame (tweets from this day are included)
        :param to_date: end date of time frame (tweets from this day are included)
        :return: Number of scraped tweets
        """
        twitter_webdriver = TwitterWebdriver('/usr/local/bin/chromedriver')
        twitter_webdriver.set_page_load_timeout(10)
        found_tweets = twitter_webdriver.get_tweets_from_profile(self.user_name, from_date, to_date)
        self.tweets = found_tweets
        twitter_webdriver.close()

    def find_join_date(self):
        """
        Get the date the user joined Twitter.

        Scrape the join date of the user from the user's profile header card.
        If no join date can be found the day of the first tweet (21st of March 2006) is returned.

        :return: Join date of user or 21st of March 2006 if no date could be found
        """
        url = 'https://twitter.com/' + self.user_name
        r = requests.get(url, headers={"Accept-Language": "en-US"})
        soup = BeautifulSoup(r.content, "html.parser")
        try:
            first_use_string = soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})['title']
            return datetime.strptime(first_use_string, "%I:%M %p - %d %b %Y")
        except (TypeError, KeyError, ValueError):
            log.error("Join date not found, returning date of first tweet ever!")
            return datetime(2006, 3, 21)

    def write_to_file(self, directory='', pickled=True):
        """
        Writes scraped data to a file.

        :param directory: Optional directory where the file will be located
        :param pickled: Whether the file should be a pickle (txt if False)
        """
        if not directory:
            directory = 'data/{}'.format(self.case_id)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = os.path.join(directory, 'twitter_{}_{}.{}'.format(self.user_name, today, ('pkl' if pickled else 'txt')))

        log.info("Writing Tweets to file")
        if pickled:
            with open(file, "wb") as f:
                pickle.dump(self.tweets, f)
        else:
            output = ''
            for post in self.tweets:
                output += post + "\n----------\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))