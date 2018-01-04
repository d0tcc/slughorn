import facebook
from datetime import datetime, timedelta
import redis
import logging
import requests
from bs4 import BeautifulSoup
import urllib3
import re
from scraper.constants import facebook_access_token
logging.basicConfig(format='%(asctime)s [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)


class FacebookScraper:

    def __init__(self, user_name, case_number, numeric_id=None):
        self.user_name = user_name
        self.case_number = case_number

        if not numeric_id:
            self.numeric_id = self.find_numeric_id()
        else:
            self.numeric_id = numeric_id

        self.posts = []

    def scrape_all(self):
        today = datetime.now()
        first_day_of_facebook = datetime(2004, 2, 1)
        return self.scrape_timeframe(first_day_of_facebook, today)

    def scrape_timeframe(self, from_date, to_date):
        more_to_come = True
        found_posts = []
        graph = facebook.GraphAPI(
            access_token=facebook_access_token,
            version="2.5")

        while more_to_come:
            url = create_url(self.numeric_id, from_date, to_date)
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

    def find_numeric_id(self):
        url = 'https://www.facebook.com/' + self.user_name
        http_pool = urllib3.connection_from_url(url)
        r = http_pool.urlopen('GET', url)
        html = r.data.decode('utf-8')
        try:
            match = re.search(r"profile_id=(\d*)", html)
            numeric_id = match.group(1)
            return numeric_id
        except (AttributeError, TypeError, KeyError, ValueError):
            log.error("Numeric ID not found, returning 0")
            return 0


def format_date(date):
    return date.strftime('%Y-%m-%d')


def create_url(numeric_id, from_date, to_date):
    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "/{}/posts?limit=100&since={}&until={}".format(numeric_id, from_string, to_string)
    return url
