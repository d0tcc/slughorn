import sys
from datetime import datetime

import facebook
import locale

from scraper.FacebookScraper import FacebookScraper
from scraper.constants import facebook_access_token

graph = facebook.GraphAPI(
            access_token=facebook_access_token,
            version="2.7")

if "linux" in sys.platform:
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
else:
    locale.setlocale(locale.LC_ALL, 'en_US')

# twitter_name = "realdonaldtrump"
# twitter_scraper = TwitterScraper(twitter_name)

import sys
sys.path.insert(0, "/usr/local/bin/")

from_date = datetime(2016, 1, 27)
to_date = datetime(2017, 12, 1)


# import requests
# url = 'https://mbasic.facebook.com/felix.holzschuh'
# page = requests.get(url)
# print (page.text.encode('utf8'))

#
# r = requests.get(url, headers={"Accept-Language": "en-US"})
# soup = BeautifulSoup(r.content, "html.parser")

#
# twitter_scraper.scrape_all()
# twitter_scraper.scrape_timeframe(from_date, to_date)
# print(twitter_scraper.tweets)
# print("Size:", len(twitter_scraper.tweets))

facebook_name = 'test_user'
facebook_scraper = FacebookScraper(facebook_name, 1234)
#facebook_scraper.scrape_timeframe(from_date, to_date)
#print(facebook_scraper.numeric_id)
facebook_scraper.scrape_all()

# print("Size:", len(facebook_scraper.posts))
# for post in facebook_scraper.posts:
#     print(post)
#     print("------------------")
