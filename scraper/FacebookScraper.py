import facebook
from datetime import datetime, timedelta
import redis
import logging
import re
from scraper import util
from scraper.constants import facebook_access_token, facebook_password, facebook_email
from selenium import webdriver
from FacebookWebBot import *


logging.basicConfig(format='%(asctime)s [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)
graph = facebook.GraphAPI(
            access_token=facebook_access_token,
            version="2.5")

class FacebookScraper:

    def __init__(self, user_name, case_number, numeric_id=0):
        self.user_name = user_name
        self.case_number = case_number
        self.is_public_page = self.check_for_public_page()
        self.driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')

        if not numeric_id and self.is_public_page:
            self.numeric_id = self.find_numeric_id()
        else:
            self.numeric_id = numeric_id

        self.posts = []

    def scrape_all(self):
        today = datetime.now()
        first_day_of_facebook = datetime(2004, 2, 1)
        return self.scrape_timeframe(first_day_of_facebook, today)

    def scrape_timeframe(self, from_date, to_date):
        found_posts = []

        if self.is_public_page:
            more_to_come = True


            while more_to_come:
                url = create_url_for_api(self.numeric_id, from_date, to_date)
                site = graph.request(url)

                posts_data = site['data']
                print(posts_data)
                posts_with_time = [(post.get('message', post.get('story', '')), post.get('created_time')) for post in posts_data]
                if len(posts_with_time) < 100:
                    more_to_come = False
                    posts = [post[0] for post in posts_with_time]
                else:
                    raw_last_date = posts_with_time[-1][1]
                    print("REACHED 100 at", raw_last_date)
                    last_date = datetime.strptime(raw_last_date, '%Y-%m-%dT%H:%M:%S+%f').date()
                    to_date = last_date + timedelta(days=1)  # to_date is not included in the search, +1 to include it
                    posts = [post[0] for post in posts_with_time if not datetime.strptime(post[1], '%Y-%m-%dT%H:%M:%S+%f').date() == last_date]  # remove days from the current day because they will be included in the next search step
                found_posts.extend(posts)

            self.posts.extend(found_posts)
            return len(found_posts)

        else:
            print("DISCLAIMER: Timeframe scraping is only possible for public pages. Scraping all posts ...")

            bot = FacebookBot('/usr/local/bin/chromedriver')
            bot.set_page_load_timeout(10)
            bot.login(facebook_email, facebook_password)
            all_posts = bot.getPostInProfile('https://mbasic.facebook.com/{}'.format(self.user_name), moreText="Mehr anzeigen")
            for p in all_posts:
                print(p)

            self.driver.close()


    def find_numeric_id(self):
        # if self.is_public_page:
        url = "/{}".format(self.user_name)
        site = graph.request(url)
        numeric_id = site.get('id', 0)
        return numeric_id
        # else:
        #     url = 'https://www.facebook.com/' + self.user_name
        #     util.login_facebook(self.driver, facebook_email, facebook_password)
        #     self.driver.get(url)
        #     source = self.driver.page_source
        #     try:
        #         match = re.search(r"profile_id=(\d*)", source)
        #         numeric_id = match.group(1)
        #         return numeric_id
        #     except (AttributeError, TypeError, KeyError, ValueError):
        #         log.error("Numeric ID not found, returning 0")
        #         return 0

    def check_for_public_page(self):
        try:
            url = "/{}".format(self.user_name)
            graph.request(url)
        except facebook.GraphAPIError:
            return False
        return True


def format_date(date):
    return date.strftime('%Y-%m-%d')


def create_url_for_api(numeric_id, from_date, to_date):
    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "/{}/posts?limit=100&since={}&until={}".format(numeric_id, from_string, to_string)
    return url
