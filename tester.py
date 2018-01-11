from scraper.TwitterScraper import TwitterScraper
from scraper.FacebookScraper import FacebookScraper
from datetime import datetime
import locale
import sys
import facebook
import pickle
from scraper import util
import requests
from bs4 import BeautifulSoup
import urllib3
import re
from scraper.constants import facebook_email, facebook_password, facebook_access_token

from selenium import webdriver

graph = facebook.GraphAPI(
            access_token=facebook_access_token,
            version="2.7")

if "linux" in sys.platform:
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
else:
    locale.setlocale(locale.LC_ALL, 'en_US')

# twitter_name = "realdonaldtrump"
# twitter_scraper = TwitterScraper(twitter_name)

from_date = datetime(2016, 1, 27)
to_date = datetime(2017, 12, 1)
#
# twitter_scraper.scrape_all()
# twitter_scraper.scrape_timeframe(from_date, to_date)
# print(twitter_scraper.tweets)
# print("Size:", len(twitter_scraper.tweets))

#facebook_name = 'felix.holzschuh'
#facebook_scraper = FacebookScraper(facebook_name, 1234)#, numeric_id=360686647276544)
#facebook_scraper.scrape_timeframe(from_date, to_date)
#print(facebook_scraper.numeric_id)
#facebook_scraper.scrape_all()

# print("Size:", len(facebook_scraper.posts))
# for post in facebook_scraper.posts:
#     print(post)
#     print("------------------")
