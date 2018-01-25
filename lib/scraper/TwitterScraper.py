from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os
import click_spinner
from lib.scraper.webdriver.TwitterWebdriver import *

log = logging.getLogger('slughorn')

#r = redis.StrictRedis(host='localhost', port=6379, db=0)

class TwitterScraper:
    """
    A TwitterScraper object represents one attempt to retrieve tweets of a user.
    """

    def __init__(self, user_name, case_number):
        """
        Init function of the TwitterScraper object.

        Initializes a TwitterScraper object, containing a given user_name and case_number.
        Based on the user_name the join_date is being retrieved with the method find_join_date().
        Furthermore an empty list of tweets and the webdriver is initialized.

        Parameters
        ----------
        user_name: str
            User name of the owner of the Twitter profile
        case_number: str
            String representation of the case number
        """
        self.user_name = user_name
        self.case_number = case_number
        self.join_date = self.find_join_date()
        self.tweets = []

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

    def scrape_all(self):
        """
        Scrape all tweets.
    
        Scrape all tweets of the user which name is provided in self.user_name and saves them in self.tweets. Calls 
        self.scrape_timeframe with the users join date and today's date.
    
        Returns
        -------
        int
            Number of scraped tweets
    
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

        Parameters
        ----------
        from_date: datetime
            start date of time frame (tweets from this day are included)
        to_date: datetime
            end date of time frame (tweets from this day are included)

        Returns
        -------
        int
            Number of scraped tweets
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

        Returns
        -------
        datetime
            Join date of user or 21st of March 2006 if no date could be found
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

    def write_to_file(self, directory=''):
        """
        Writes scraped data to a file.

        Parameters
        ----------
        directory: str
            Optional directory where the file will be located
        """
        if not directory:
            directory = 'data/twitter/'

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file = os.path.join(directory, 'tw_{}_{}_{}.txt'.format(self.case_number, self.user_name, today))

        # TODO change from whole posts to words to password lists
        log.info("Writing Tweets to file {}".format(file))
        output = ''
        for post in self.tweets:
            output += post + "\n----------\n"


        with open(file=file, mode='w+') as f:
            f.write(output)
        log.info("Successfully written to file {}".format(file))