import logging
from time import sleep

import requests
from fake_useragent import UserAgent
from lxml import etree, html

ua = UserAgent(fallback='chrome')

log = logging.getLogger('slughorn')

SLEEP_TIME = 1


def sanitize_text(text):
    text = text.strip(' \t\n\r')
    text = text.replace(' @ ', '@').replace('@ ', '@').replace(' # ', '#').replace('# ', '#')  # handle twitter specific characters
    text = text.replace(' . ', '. ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')  # handle punctuations and spaces
    text = text.replace('http:// ', 'http://').replace('https:// ', 'https://')  # handle URIs
    return text


class TwitterSpider:

    def __init__(self, user_name, from_date, to_date):
        self.user_name = user_name
        self.url = "https://twitter.com/i/search/timeline?l=&f=tweets&q=from%3A{}%20since%3A{}%20until%3A{}include%3Aretweets&src=typed&max_position={}".format(
            user_name, from_date, to_date, '{}')
        self.tweets = []
        self.last_url = ''

    def get_tweets_from_profile(self):
        # set url for first round
        url = self.url.format('')

        while url != self.last_url:
            log.debug("Scraping url: {}".format(url))
            data = self.get_json(url)
            self.parse(data)

            min_position = data['min_position']
            self.last_url = url
            url = self.url.format(min_position)

        return self.tweets

    def get_json(self, url):
        header = {'User-Agent': str(ua.random)}
        r = requests.get(url, headers=header, allow_redirects=False)
        try:
            data = r.json()
        except ValueError:
            log.debug("ValueError: Sleep {} second(s) and try again".format(SLEEP_TIME))
            sleep(SLEEP_TIME)
            data = self.get_json(url)
        return data

    def parse(self, data):

        items_html = data['items_html']
        items_html = items_html.strip().encode('utf8')

        if items_html:
            parser = etree.XMLParser(recover=True, encoding='utf8')
            root = etree.fromstring(items_html, parser=parser)
            tweet_items = root.xpath('//li[@data-item-type="tweet"]/div')

            for tweet_item in tweet_items:
                tweet_text_elements = tweet_item.xpath('.//div[@class="js-tweet-text-container"]/p')
                log.debug("Amount of Text elements: {}".format(len(tweet_text_elements)))
                try:
                    tweet_text_element = tweet_text_elements[0]
                except IndexError:
                    continue

                # remove elements with unwanted text
                for xpath in ['.//div[@class="stream-item-footer"]', './/div[@class="AdaptiveMediaOuterContainer"]']:
                    for bad in tweet_text_element.xpath(xpath):
                        bad.getparent().remove(bad)

                tweet_text_string = etree.tostring(tweet_text_element)
                p_html_element = html.fromstring(tweet_text_string)
                tweet_text = p_html_element.text_content()
                tweet_text = sanitize_text(tweet_text)
                if tweet_text:
                    self.tweets.append(tweet_text)
