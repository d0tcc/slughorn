import redis
import threading
from flask import Flask, render_template, flash, request, redirect, url_for, make_response
from markupsafe import escape
from forms import TwitterScrapeForm
from config import BaseConfig
from scraper import TwitterScraper
import logging
from logging import Formatter, FileHandler

r = redis.StrictRedis(host='localhost', port=6379, db=0)

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
        case_number = form.case_number.data
        scraper = TwitterScraper.TwitterScraper(form.name.data, case_number)
        if scrape_all_tweets:
            scrape_thread = threading.Thread(target=scraper.scrape_all)
        else:
            scrape_thread = threading.Thread(target=scraper.scrape_timeframe, args=[from_date, to_date])
        scrape_thread.start()

        response = make_response(redirect("/status"))
        response.set_cookie('case_number', case_number)
        return response

    return render_template('forms/scraper.html', form=form)


@app.route("/progressbar/<case_number>")
def progressbar(case_number):
    twitter_weeks_total = int(r.get("{}_twitter_weeks_total".format(case_number)))
    twitter_weeks_done = int(r.get("{}_twitter_weeks_done".format(case_number)))
    if twitter_weeks_total == 0:
        percentage = 0.0
    else:
        percentage = (twitter_weeks_done / twitter_weeks_total) * 100
    print("PERCENTAGE: ", percentage)
    return render_template('pages/progress_bar.html', percentage=percentage)


@app.route("/status")
def status():
    case_number = request.cookies.get('case_number')
    #twitter_status = get_twitter_status(case_number)
    return render_template('pages/status.html',
                           case_number=case_number)
                           #twitter_status=twitter_status)


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
