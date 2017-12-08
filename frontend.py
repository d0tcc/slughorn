from flask import Flask
from flask_bootstrap import Bootstrap

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
from flask_wtf.csrf import CSRFProtect
from nav import nav
from forms import TwitterScrapeForm
from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
Bootstrap(app)
frontend = Blueprint('frontend', __name__)
app.register_blueprint(frontend)
nav.init_app(app)
csrf = CSRFProtect(app)


# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('Slughorn', '.index'),
    View('Twitter', '.twitter')))


# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/twitter')
def twitter():
    form = TwitterScrapeForm()

    if form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Scraping for {} in progress ...'
              .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.twitter'))

    return render_template('twitter.html', form=form)


if __name__ == '__main__':
    app.run()