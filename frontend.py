from flask import Flask, render_template, flash, redirect, url_for
from markupsafe import escape
from forms import TwitterScrapeForm
from config import BaseConfig
from scraper import TwitterScraper
import logging
from logging import Formatter, FileHandler

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object(BaseConfig)


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/scraper', methods=['GET', 'POST'])
def scraper():
    form = TwitterScrapeForm()

    if form.validate_on_submit():

        try:
            from_date = form.from_date.data
        except ValueError:
            flash('Date {} not valid'
                  .format(escape(form.from_date.data)))
            return render_template('forms/scraper.html', form=form)
        try:
            to_date = form.to_date.data
        except ValueError:
            flash('Date {} not valid'
                  .format(escape(form.to_date.data)))
            return render_template('forms/scraper.html', form=form)

        flash('Scraping tweets for user @{} in progress ...'
              .format(escape(form.name.data)))

        scrape_all_tweets = bool(form.all_tweets.data)
        scraper = TwitterScraper.TwitterScraper(form.name.data)
        if scrape_all_tweets:
            number_of_found_tweets = scraper.scrape_all()
        else:
            number_of_found_tweets = scraper.scrape_timeframe(from_date, to_date)
        flash("Successfully scraped {} new tweets!".format(number_of_found_tweets))

        return render_template('forms/scraper.html', form=form)

    return render_template('forms/scraper.html', form=form)


#----------------------------------------------------------------------------#
# Error handlers.
#----------------------------------------------------------------------------#

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

if __name__ == '__main__':
    app.run()
