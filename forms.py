from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms import validators


class TwitterScrapeForm(FlaskForm):
    name = StringField(u'Twitter name', [validators.required()])
    from_date = DateField(u'From')
    to_date = DateField(u'To')
    all_tweets = BooleanField(u'Scrape all Tweets')

    submit = SubmitField(u'Scrape!')