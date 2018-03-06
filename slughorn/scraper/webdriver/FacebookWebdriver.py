# coding: utf-8
#
# based on hikaruAi's FacebookBot (https://github.com/hikaruAi/FacebookBot)
#
import logging
import re
import time

import click
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from slughorn.scraper.util import FB_DATE_REGEX, FB_LIKE_REGEX

log = logging.getLogger('slughorn')


def mfacebookToBasic(url):
    """
    Reformat a url to load mbasic facebook
    
    Reformat a url to load mbasic facebook instead of regular facebook, return the same string if
    the url does not contain facebook
    
    :param url: URL to be transformed

    :return: Transformed URL or unchanged parameter if URL did not contain 'facebook'
    """

    if "m.facebook.com" in url:
        return url.replace("m.facebook.com", "mbasic.facebook.com")
    elif "www.facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com")
    else:
        return url


class FacebookWebdriver(webdriver.Chrome):
    """
    Class for browsing Facebook with a webdriver
    """

    def __init__(self, path_to_web_driver='/usr/local/bin/chrome'):
        """
        Init function of the FacebookWebdriver object.

        Initializes a FacebookWebdriver object with webdriver at the given path.

        :param path_to_web_driver: Path to the installed webdriver
        """
        self.path_to_web_driver = path_to_web_driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        webdriver.Chrome.__init__(self, executable_path=self.path_to_web_driver, chrome_options=options)

    def get(self, url):
        """
        Call get function of super class but with transformed URL.
        
        :param url: URL to be called
        """
        super().get(mfacebookToBasic(url))

    def login(self, email, password):
        """
        Login to facebook using email and password.

        :param email: email address of Facebook account
        :param password: password of Facebook account
        :return: Whether the login was successful
        """
        url = "https://mbasic.facebook.com"
        self.get(url)
        email_element = self.find_element_by_name("email")
        email_element.send_keys(email)
        pass_element = self.find_element_by_name("pass")
        pass_element.send_keys(password)
        pass_element.send_keys(Keys.ENTER)
        if self.find_element_by_class_name("bi"):
            self.find_element_by_class_name("bp").click();
        try:
            self.find_element_by_name("xc_message")
            log.debug("Logged in")
            return True
        except NoSuchElementException as e:
            log.error("Failed to login")
            return False

    def logout(self):
        """
        Logout from Facebook

        :return: Whether the logout was successful
        """

        url = "https://mbasic.facebook.com/logout.php?h=AffSEUYT5RsM6bkY&t=1446949608&ref_component=mbasic_footer&ref_page=%2Fwap%2Fhome.php&refid=7"
        try:
            self.get(url)
            return True
        except Exception as e:
            log.error("Failed to log out ->\n", e)
            return False

    def get_numeric_id(self, user_name):
        """
        Find numeric ID of the user's public profile.

        User's profiles are represented with numeric IDs which can be used for the Facebook Graph API.
        
        :param user_name: user_name of Facebook profile
        :return: Numeric ID of profile
        """
        url = 'https://www.facebook.com/' + user_name
        self.get(url)
        source = self.page_source
        try:
            match = re.search(r"profile_id=(\d*)", source)
            numeric_id = match.group(1)
            return numeric_id
        except (AttributeError, TypeError, KeyError, ValueError):
            log.error("Numeric ID not found, returning 0")
            return 0

    def get_groups(self):
        """
        Get all groups a user is member in

        :return: A dictionary of all groups
        """
        url = "https://m.facebook.com/groups/?seemore"
        groups = dict()
        self.get(url)
        br = self.find_elements_by_class_name("br")
        for b in br:
            try:
                notis = int(b.text[-2:])
                group_name = b.text[:-2]
            except ValueError:
                group_name = b.text
                notis = 0
            try:
                link = b.find_element_by_tag_name("a").get_attribute('href')
                groups[group_name] = (mfacebookToBasic(link), notis)
            except Exception as e:
                log.error("Can't get group link")
        return groups

    def get_facebook_name(self, user_name):
        """
        Get name of the account

        :return: Name of the account
        """
        url = 'https://mbasic.facebook.com/{}'.format(user_name)
        self.get(url)
        name = self.title
        log.debug("NAME: " + name)
        return name

    def get_posts_from_profile(self, user_name, moreText="Mehr anzeigen"):
        """
        Return a list of Posts in a profile/fanpage

        Scrapes all facebook posts of the user which name is provided in user_name and returns them.

        :param user_name: user_name of Facebook profile  
        :return: List of scraped Facebook posts
        """
        """Return a list of Posts in a profile/fanpage , setup the "moreText" using your language, theres not elegant way to handle that"""
        name = self.get_facebook_name(user_name)
        posts_list = list()
        url = 'https://mbasic.facebook.com/{}?v=timeline'.format(user_name)
        self.get(url)

        years_elements = self.find_elements_by_xpath("//div[@class='h']/a[contains(., '20')]")
        years = [y.text for y in years_elements]
        years.append('9999')  # append one dummy year for the extraction of the last year in the list

        with click.progressbar(years, label='Scraping {} years'.format(len(years)), show_eta=True) as bar:
            for year in bar:
                more_button_exists = True
                while more_button_exists:
                    try:
                        articles = self.find_elements_by_xpath("//div[@role='article']")
                        for article in articles:
                            try:
                                content = str(article.text)
                                content = FB_DATE_REGEX.sub('', content)
                                content = FB_LIKE_REGEX.sub('', content)
                                content = content.replace(name, '')
                                posts_list.append(content)
                            except Exception as e:
                                log.error("ERROR: " + str(e))

                        # press more if more button exists
                        try:
                            show_more_link_element = self.find_element_by_xpath("//div[@class='h']/a[text()='{}']".format(moreText))
                            show_more_link = show_more_link_element.get_attribute('href')
                            self.get(show_more_link)
                        except NoSuchElementException:
                            # if more button does not exist go to the next year
                            more_button_exists = False
                            if year is not '9999':
                                year_link_element = self.find_element_by_xpath("//div[@class='h']/a[text()='{}']".format(year))
                                year_link = year_link_element.get_attribute('href')
                                self.get(year_link)

                    except TimeoutError as e:
                        log.error("Timeout:", str(e))
                        time.sleep(1)
                    except BaseException as e:
                        log.error("ERROR:", str(e))

        return posts_list
