from scraper.TwitterScraper import TwitterScraper
from scraper.FacebookScraper import FacebookScraper
from datetime import datetime
import locale
import sys

if "linux" in sys.platform:
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
else:
    locale.setlocale(locale.LC_ALL, 'en_US')

# twitter_name = "realdonaldtrump"
# twitter_scraper = TwitterScraper(twitter_name)
#
from_date = datetime(2017, 9, 27)
to_date = datetime(2017, 12, 7)
#
# # twitter_scraper.scrape_all()
# twitter_scraper.scrape_timeframe(from_date, to_date)
# print(twitter_scraper.tweets)
# print("Size:", len(twitter_scraper.tweets))

facebook_name = 'arminwolf.journalist'
facebook_scraper = FacebookScraper(facebook_name, 1234, numeric_id=360686647276544)
facebook_scraper.scrape_timeframe(from_date, to_date)
print("Size:", len(facebook_scraper.posts))
for post in facebook_scraper.posts:
    print(post)
    print("------------------")