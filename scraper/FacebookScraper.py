import facebook
from datetime import datetime, timedelta
import redis
import logging
from constants import facebook_access_token
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

        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)

    def scrape_all(self):

        graph = facebook.GraphAPI(
            access_token=facebook_access_token,
            version="2.5")

        site = graph.get_objects(ids=[self.numeric_id], fields="feed")
        posts_data = site[self.numeric_id]['posts']['data']
        posts = [post['message'] for post in posts_data]
        self.posts = posts
        return len(posts)

    def scrape_timeframe(self, from_date, to_date):
        return 0

    def find_numeric_id(self):
        return 0

def format_date(date):

    return date.strftime('%Y-%m-%d')


def create_url(user_name, from_date, to_date):

    return 0
