# coding: utf-8
import logging
import math
import time
from datetime import timedelta

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from slughorn.scraper import util

log = logging.getLogger('slughorn')

tweet_selector = "div.js-tweet-text-container"


class TwitterWebdriver(webdriver.Chrome):
    """
    Class for browsing Twitter with a webdriver
    """

    def __init__(self, path_to_web_driver='/usr/local/bin/chrome'):
        """
        Init function of the TwitterWebdriver object.

        Initializes a TwitterWebdriver object with webdriver at the given path.

        :param path_to_web_driver: Path to the installed webdriver
        """
        self.path_to_web_driver = path_to_web_driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        webdriver.Chrome.__init__(self, executable_path=self.path_to_web_driver, chrome_options=options)


    def get_tweets_from_profile(self, user_name, from_date, to_date):
        """
        Scrape specific time frame.

        Scrape all tweets of the user which name is provided in user_name in a given time frame and returns them.
        Tweets are scraped in blocks of one week. By scrolling down new tweets are dynamically loaded through 
        JavaScript.

        :param user_name: user name of the Twitter profile that will be scraped
        :param from_date: start date of time frame (tweets from this day are included)
        :param to_date: end date of time frame (tweets from this day are included)

        :return: List of scraped tweets
        """
        def scroll_down_and_count_tweets(driver, delay):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(delay)
            return driver.find_elements_by_css_selector(tweet_selector)

        period = (to_date - from_date).days + 1
        log.debug("Time Period: {}".format(period))
        weeks_total = int(math.ceil(period / 7))
        period = min(period, 7)
        weeks_done = 0
        #log.debug("Initialize status: {}/{}".format(weeks_done, weeks_total))
        #r.set("{}_twitter_weeks_total".format(self.case_number), weeks_total)
        #r.set("{}_twitter_weeks_done".format(self.case_number), weeks_done)
        number_of_found_tweets = 0
        tweets_list = []
        timeframe_end_date = to_date + timedelta(days=1)
        week_start_date = from_date
        week_end_date = from_date + timedelta(days=period)

        while week_end_date <= timeframe_end_date and week_start_date < timeframe_end_date:
            log.debug("Checking tweets for user {} in week {} - {}".format(user_name, week_start_date.strftime('%Y-%m-%d'),
                                                              week_end_date.strftime('%Y-%m-%d')))
            url = util.create_twitter_url(user_name, week_start_date, week_end_date)
            self.get(url)
            found_tweet_divs = self.find_elements_by_css_selector(tweet_selector)
            increment = 20
            log.debug("Found tweets: {}, Increment: {}".format(len(found_tweet_divs), increment))

            while len(found_tweet_divs) >= increment:
                log.debug('Scrolling down to load more tweets')
                found_tweet_divs = scroll_down_and_count_tweets(self, 1)
                log.debug("Found more tweets: {}, Increment: {}".format(len(found_tweet_divs), increment))
                increment += 20

            for tweet_div in found_tweet_divs:
                try:
                    tweet = tweet_div.find_element_by_class_name('tweet-text').text
                    log.debug("--- Tweet: {}".format(tweet))
                    tweets_list.append(tweet)
                    number_of_found_tweets = number_of_found_tweets + 1
                except NoSuchElementException:
                    log.error("Element 'tweet-text' not found in div.")

            log.debug("{} Tweets found in this week. {} total".format(len(found_tweet_divs), len(tweets_list)))
            week_start_date = week_start_date + timedelta(days=7)
            week_end_date = week_end_date + timedelta(days=7)
            if week_end_date > timeframe_end_date:
                week_end_date = timeframe_end_date
            weeks_done = weeks_done + 1
            #r.set("{}_twitter_weeks_done".format(self.case_number), weeks_done)

        log.info("Finished scraping Tweets for user '{}'".format(user_name))
        return tweets_list
