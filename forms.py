from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms.fields import StringField, BooleanField, SubmitField
from wtforms import validators


class TwitterScrapeForm(FlaskForm):
    case_number = StringField(u'Case Number', [validators.required()])
    name = StringField(u'User Name', [validators.required()])
    from_date = DateField(u'From')
    to_date = DateField(u'To')
    all_tweets = BooleanField(u'All Tweets from this user')

    submit = SubmitField(u'Scrape!')