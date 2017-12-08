from scraper.TwitterScraper import TwitterScraper
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

twitter_name = "realdonaldtrump"
twitter_scraper = TwitterScraper(twitter_name)

from_date = datetime(2017, 12, 6)
to_date = datetime(2017, 12, 7)

twitter_scraper.scrape_all()
print(twitter_scraper.tweets)
print("Size:", len(twitter_scraper.tweets))