from lib.scraper.webdriver.FacebookWebdriver import *
from lib.scraper import util

from datetime import datetime, timedelta
import click_spinner
import facebook
import os
#import redis
import pickle
import logging

log = logging.getLogger('slughorn')

#r = redis.StrictRedis(host='localhost', port=6379, db=0)

class FacebookScraper:
    """
    A FacebookScraper object represents one attempt to retrieve facebook posts of a user.
    """

    def __init__(self, user_name, case_id, numeric_id=0):
        """
        Init method of the FacebookScraper Class.

        Initializes a FacebookScraper object, containing a given user_name and case_number.
        Based on the user_name the type of profile is being checked: public page or private profile.
        A numeric ID can be used for the Facebook API and is optional. If the page is public the numeric ID can be 
        retrieved and is used later on.
        Furthermore an empty list of posts is initialized.

        :param user_name: User name of the owner of the Twitter profile
        :param case_id: String representation of the case number
        :param numeric_id: Numeric ID of the Facebook profile
        """
        self.user_name = user_name
        self.case_id = case_id
        from lib.scraper.constants import constants
        self.graph = facebook.GraphAPI(
            access_token=constants['facebook_access_token'],
            version="2.5")
        self.is_public_page = self.check_for_public_page()

        if not numeric_id and self.is_public_page:
            self.numeric_id = self.get_numeric_id()
        else:
            self.numeric_id = numeric_id

        self.posts = []


    def scrape_all(self):
        """
        Scrape all Facebook posts.

        Scrape all Facebook posts of the user which name is provided in self.user_name and saves them in self.posts. 
        Calls self.scrape_timeframe with date of the foundation of Facebook and today's date.

        :return: Number of scraped Facebook posts
        """
        today = datetime.now()
        first_day_of_facebook = datetime(2004, 2, 1)
        return self.scrape_timeframe(first_day_of_facebook, today)

    def scrape_timeframe(self, from_date, to_date):
        """
        Scrape specific time frame.

        Scrape all Facebook posts of the user which name is provided in self.user_name in a given time frame and saves 
        them in self.posts.
        Time frame scraping is only available if the user has a public page. Otherwise all posts are scraped.
        Uses Facebook's Graph API if user name belongs to a public site. Otherwise it uses the FacebookWebdriver.

        :param from_date: start date of time frame (Facebook posts from this day are included)
        :param to_date: end date of time frame (Facebook posts from this day are included)
        :return: Number of scraped Facebook posts
        """
        found_posts = []

        if self.is_public_page:
            more_to_come = True

            with click_spinner.spinner():
                while more_to_come:
                    url = util.create_url_for_facebook_api(self.numeric_id, from_date, to_date)
                    site = self.graph.request(url)

                    posts_data = site['data']
                    log.debug(posts_data)
                    posts_with_time = [(post.get('message', post.get('story', '')), post.get('created_time')) for post in posts_data]
                    if len(posts_with_time) < 100:
                        more_to_come = False
                        posts = [post[0] for post in posts_with_time]
                    else:
                        raw_last_date = posts_with_time[-1][1]
                        log.debug("REACHED 100 at {}".format(raw_last_date))
                        last_date = datetime.strptime(raw_last_date, '%Y-%m-%dT%H:%M:%S+%f').date()
                        to_date = last_date + timedelta(days=1)  # to_date is not included in the search, +1 to include it
                        posts = [post[0] for post in posts_with_time if not datetime.strptime(post[1], '%Y-%m-%dT%H:%M:%S+%f').date() == last_date]  # remove days from the current day because they will be included in the next search step
                    found_posts.extend(posts)

                self.posts.extend(found_posts)
                return len(found_posts)

        else:
            from lib.scraper.constants import constants
            facebook_webdriver = FacebookWebdriver('/usr/local/bin/chromedriver')
            facebook_webdriver.set_page_load_timeout(10)
            facebook_webdriver.login(constants['facebook_email'], constants['facebook_password'])
            all_posts = facebook_webdriver.get_posts_from_profile(self.user_name, moreText="Mehr anzeigen") #  moreText must be adapted to language settings
                                                                       #  of scraping profile
            self.posts = all_posts
            facebook_webdriver.close()

        print("Finished scraping Facebook posts for user '{}'".format(self.user_name))


    def get_numeric_id(self):
        """
        Find numeric ID of the user's public profile.

        User's profiles are represented with numeric IDs which can be used for the Facebook Graph API. In our scenario 
        only public profile IDs are needed. A way to get IDs from profiles is provided anyway.

        :return: Numeric ID of profile
        """
        if self.is_public_page:
            url = "/{}".format(self.user_name)
            site = self.graph.request(url)
            numeric_id = site.get('id', 0)
            return numeric_id
        else:
            from lib.scraper.constants import constants
            facebook_driver = FacebookWebdriver('/usr/local/bin/chromedriver')
            facebook_driver.set_page_load_timeout(10)
            facebook_driver.login(constants['facebook_email'], constants['facebook_password'])
            numeric_id = facebook_driver.get_numeric_id(self.user_name)
            facebook_driver.close()
            return numeric_id

    def check_for_public_page(self):
        """
        Checks whether the user's profile is a public page or a private profile.
        
        Only public pages can be accessed via the Facebook Graph API. If an exception is thrown the user's profile is 
        private.

        :return: Whether the profile is public or private
        """
        try:
            url = "/{}".format(self.user_name)
            self.graph.request(url)
        except facebook.GraphAPIError as e:
            log.debug("Page is not public. Starting FacebookWebdriver ...")
            return False
        return True

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
        file = os.path.join(directory, 'facebook_{}_{}.{}'.format(self.user_name, today, ('pkl' if pickled else 'txt')))

        log.info("Writing Facebook posts to file")
        if pickled:
            with open(file, "wb") as f:
                pickle.dump(self.posts, f)
        else:
            output = ''
            for post in self.posts:
                output += post + "\n----------\n"

            with open(file=file, mode='w+') as f:
                f.write(output)

        log.info("Successfully written to file {}".format(file))
