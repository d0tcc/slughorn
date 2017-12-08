from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from time import sleep
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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

        more_tweets_are_coming = True
        url = create_url(self.user_name, from_date, to_date)
        driver.get(url)
        found_tweet_divs = []
        #found_tweet_divs = driver.find_elements_by_css_selector(tweet_selector)
        increment = 20
        #print("Found tweets: ", len(found_tweet_divs), ", Increment: ", increment)

        while more_tweets_are_coming:
            print("Found tweets: ", len(found_tweet_divs), ", Increment: ", increment)
            print('scrolling down to load more tweets')
            found_tweet_divs = scroll_down_and_count_tweets(1)

            # grace period when no new tweets are counted
            if len(found_tweet_divs) < increment:
                for grace in range(3):
                    if len(found_tweet_divs) < increment and grace == 2:
                        more_tweets_are_coming = False
                        break
                    if len(found_tweet_divs) < increment:
                        sleep(1)
                        print("No new tweets found. Trying again in 5 seconds ...")
                        found_tweet_divs = scroll_down_and_count_tweets(5)

            increment += 20

        # while len(found_tweet_divs) >= increment:
        #     print("Found tweets: ", len(found_tweet_divs), ", Increment: ", increment)
        #     print('scrolling down to load more tweets')
        #     driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        #     sleep(delay)
        #     found_tweet_divs = driver.find_elements_by_css_selector(tweet_selector)
        #     increment += 20

        for tweet_div in found_tweet_divs:
            tweet = tweet_div.find_element_by_class_name('tweet-text').text
            print(tweet)
            self.tweets.append(tweet)

    def find_join_date(self):

        url = 'https://twitter.com/' + self.user_name
        r = requests.get(url, headers = {"Accept-Language": "en-US"})
        soup = BeautifulSoup(r.content, "html.parser")
        first_use_string = soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})['title']
        return datetime.strptime(first_use_string, "%I:%M %p - %d %b %Y")


def format_date(date):

    return date.strftime('%Y-%m-%d')


def create_url(user_name, from_date, to_date):

    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "https://twitter.com/search?f=tweets&vertical=default&q=from%3A{}%20since%3A{}%20until%3A{" \
           "}include%3Aretweets&src=typd".format(user_name, from_string, to_string)
    # print(url)
    return url

