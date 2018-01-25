# coding: utf-8
#
# based on hikaruAi's FacebookBot (https://github.com/hikaruAi/FacebookBot)
#
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import click
import re
import logging

log = logging.getLogger('slughorn')


def mfacebookToBasic(url):
    """
    Reformat a url to load mbasic facebook
    
    Reformat a url to load mbasic facebook instead of regular facebook, return the same string if
    the url does not contain facebook
    
    Parameters
    ----------
    url : str
        URL to be transformed

    Returns
    -------
    str
        Transformed URL or unchanged parameter if URL did not contain 'facebook'
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


        Parameters
        ----------
        path_to_web_driver: str
            Path to the installed webdriver
        """
        self.path_to_web_driver = path_to_web_driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        webdriver.Chrome.__init__(self, executable_path=self.path_to_web_driver, chrome_options=options)

    def get(self, url):
        """
        Call get function of super class but with transformed URL.
        
        Parameters
        ----------
        url: str
            URL to be called
        """
        super().get(mfacebookToBasic(url))

    def login(self, email, password):
        """
        Login to facebook using email and password.

        Parameters
        ----------
        email: str
            email address of Facebook account
        password: str
            password of Facebook account

        Returns
        -------
        bool
            Whether the login was successful
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
            print("Logged in")
            return True
        except NoSuchElementException as e:
            print("Fail to login")
            return False

    def logout(self):
        """
        Logout from Facebook

        Returns
        -------
        bool
            Whether the logout was successful
        """

        url = "https://mbasic.facebook.com/logout.php?h=AffSEUYT5RsM6bkY&t=1446949608&ref_component=mbasic_footer&ref_page=%2Fwap%2Fhome.php&refid=7"
        try:
            self.get(url)
            return True
        except Exception as e:
            print("Failed to log out ->\n", e)
            return False

    def get_numeric_id(self, user_name):
        """
        Find numeric ID of the user's public profile.

        User's profiles are represented with numeric IDs which can be used for the Facebook Graph API.
        
        Parameters
        ----------
        user_name: str
            user_name of Facebook profile
        
        Returns
        -------
        int
            Numeric ID of profile
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

        Returns
        -------
        dict
            A dictionary of all groups
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
                print("Can't get group link")
        return groups

    def get_posts_from_profile(self, user_name, moreText="Mostrar"):
        """
        Return a list of Posts in a profile/fanpage

        Scrapes all facebook posts of the user which name is provided in user_name and returns them.

        Parameters
        ----------
        user_name: str
            user_name of Facebook profile
            
        Returns
        -------
        list
            List of scraped Facebook posts
        """
        """Return a list of Posts in a profile/fanpage , setup the "moreText" using your language, theres not elegant way to handle that"""
        posts_list = list()
        url = 'https://mbasic.facebook.com/{}?v=timeline'.format(user_name)
        self.get(url)

        years_elements = self.find_elements_by_xpath("//div[@class='h']/a[contains(., '20')]")
        years = [y.text for y in years_elements]
        years.append('9999')  # append one dummy year for the extraction of the last year in the list

        with click.progressbar(years, label='Scraping {} years'.format(len(years)), show_eta=False) as bar:
            for year in bar:
                more_button_exists = True
                while more_button_exists:
                    try:
                        articles = self.find_elements_by_xpath("//div[@role='article']")
                        for article in articles:
                            try:
                                posts_list.append(str(article.text))
                            except Exception as e:
                                print("ERROR: " + str(e))

                        # press more if more button exists
                        try:
                            show_more_link_element = self.find_element_by_partial_link_text(moreText)
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
                        print("Timeout:", str(e))
                        time.sleep(1)
                    except BaseException as e:
                        print("ERROR:", str(e))

        return posts_list
