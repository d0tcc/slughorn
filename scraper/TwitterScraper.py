from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

import logging
logging.basicConfig(format='%(asctime)s [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)

tweet_selector = "div.js-tweet-text-container"


class TwitterScraper:

    def __init__(self, user_name):
        self.user_name = user_name
        self.join_date = self.find_join_date()
        self.tweets = []

    def scrape_all(self):
        today = datetime.now()
        return self.scrape_timeframe(self.join_date, today)

    def scrape_timeframe(self, from_date, to_date):

        def scroll_down_and_count_tweets(delay):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(delay)
            return driver.find_elements_by_css_selector(tweet_selector)

        timeframe_end_date = to_date + timedelta(days=1)
        week_start_date = from_date
        week_end_date = from_date + timedelta(days=7)

        while week_end_date <= timeframe_end_date and week_start_date < timeframe_end_date:
            log.info("\n\n")
            log.info("Checking tweets in week {} - {}".format(week_start_date.strftime('%Y-%m-%d'),
                                                              week_end_date.strftime('%Y-%m-%d')))
            url = create_url(self.user_name, week_start_date, week_end_date)
            driver.get(url)
            found_tweet_divs = driver.find_elements_by_css_selector(tweet_selector)
            increment = 20
            log.info("Found tweets: {}, Increment: {}".format(len(found_tweet_divs), increment))

            while len(found_tweet_divs) >= increment:
                log.info('Scrolling down to load more tweets')
                found_tweet_divs = scroll_down_and_count_tweets(1)
                log.info("Found more tweets: {}, Increment: {}".format(len(found_tweet_divs), increment))
                increment += 20

            for tweet_div in found_tweet_divs:
                try:
                    tweet = tweet_div.find_element_by_class_name('tweet-text').text
                    log.info("--- Tweet: {}".format(tweet))
                    self.tweets.append(tweet)
                except NoSuchElementException:
                    log.error("Element 'tweet-text' not found in div.")

            log.info("---------")
            log.info("{} Tweets found in this week. {} total".format(len(found_tweet_divs), len(self.tweets)))
            log.info("---------")
            week_start_date = week_start_date + timedelta(days=7)
            week_end_date = week_end_date + timedelta(days=7)
            if week_end_date > timeframe_end_date:
                week_end_date = timeframe_end_date

    def find_join_date(self):

        url = 'https://twitter.com/' + self.user_name
        r = requests.get(url, headers={"Accept-Language": "en-US"})
        soup = BeautifulSoup(r.content, "html.parser")
        try:
            first_use_string = soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})['title']
            return datetime.strptime(first_use_string, "%I:%M %p - %d %b %Y")
        except (TypeError, KeyError, ValueError):
            log.error("Join date not found, returning date of first tweet ever!")
            return datetime(2006, 3, 21)


def format_date(date):

    return date.strftime('%Y-%m-%d')


def create_url(user_name, from_date, to_date):

    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "https://twitter.com/search?f=tweets&vertical=default&q=from%3A{}%20since%3A{}%20until%3A{" +\
          "}include%3Aretweets&src=typd".format(user_name, from_string, to_string)
    return url
