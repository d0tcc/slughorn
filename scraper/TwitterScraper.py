import math
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import redis
import logging
logging.basicConfig(format='%(asctime)s [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

tweet_selector = "div.js-tweet-text-container"

r = redis.StrictRedis(host='localhost', port=6379, db=0)

class TwitterScraper:

    def __init__(self, user_name, case_number):
        self.user_name = user_name
        self.case_number = case_number
        self.join_date = self.find_join_date()
        self.tweets = []

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)

    def scrape_all(self):
        today = datetime.now()
        return self.scrape_timeframe(self.join_date, today)

    def scrape_timeframe(self, from_date, to_date):

        def scroll_down_and_count_tweets(delay):
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(delay)
            return self.driver.find_elements_by_css_selector(tweet_selector)

        period = (to_date - from_date).days + 1
        log.info("Period: {}".format(period))
        weeks_total = int(math.ceil(period / 7))
        period = min(period, 7)
        weeks_done = 0
        log.info("Initialize status: {}/{}".format(weeks_done, weeks_total))
        r.set("{}_twitter_weeks_total".format(self.case_number), weeks_total)
        r.set("{}_twitter_weeks_done".format(self.case_number), weeks_done)
        number_of_found_tweets = 0
        timeframe_end_date = to_date + timedelta(days=1)
        week_start_date = from_date
        week_end_date = from_date + timedelta(days=period)

        while week_end_date <= timeframe_end_date and week_start_date < timeframe_end_date:
            log.info("\n\n")
            log.info("Checking tweets in week {} - {}".format(week_start_date.strftime('%Y-%m-%d'),
                                                              week_end_date.strftime('%Y-%m-%d')))
            url = create_url(self.user_name, week_start_date, week_end_date)
            self.driver.get(url)
            found_tweet_divs = self.driver.find_elements_by_css_selector(tweet_selector)
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
                    number_of_found_tweets = number_of_found_tweets + 1
                except NoSuchElementException:
                    log.error("Element 'tweet-text' not found in div.")

            log.info("---------")
            log.info("{} Tweets found in this week. {} total".format(len(found_tweet_divs), len(self.tweets)))
            log.info("---------")
            week_start_date = week_start_date + timedelta(days=7)
            week_end_date = week_end_date + timedelta(days=7)
            if week_end_date > timeframe_end_date:
                week_end_date = timeframe_end_date
            weeks_done = weeks_done + 1
            r.set("{}_twitter_weeks_done".format(self.case_number), weeks_done)

        self.driver.close()
        return number_of_found_tweets

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
    url = "https://twitter.com/search?f=tweets&vertical=default&q=from%3A{}%20since%3A{}%20until%3A{" \
          "}include%3Aretweets&src=typd".format(user_name, from_string, to_string)
    return url
