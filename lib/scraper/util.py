import pickle
from datetime import datetime

def login_facebook(driver, email, password):
    url = 'https://www.facebook.com'
    driver.get(url)
    emailelement = driver.find_element_by_name('email')
    passwordelement = driver.find_element_by_name('pass')
    emailelement.send_keys(email)
    passwordelement.send_keys(password)
    loginButtonXPath = "// *[ @ id = 'u_0_2']"#"//label[@id='loginbutton']/input]"
    loginelement = driver.find_element_by_xpath(loginButtonXPath)
    loginelement.submit()
    pickle.dump(driver.get_cookies() , open("FacebookCookies.pkl","wb"))
    # for cookie in pickle.load(open("FacebookCookies.pkl", "rb")):
    #     driver.add_cookie(cookie)
    # return driver


def format_date(date):
    """
    Format date for creation of Twitter URL and Facebook API.

    Format a datetime object to a string in the form of '%Y-%m-%d', e.g. '2018-01-21'

    Parameters
    ----------
    date : datetime
        date to be formated

    Returns
    -------
    str
        date in string representation
    """
    return date.strftime('%Y-%m-%d')


def create_twitter_url(user_name, from_date, to_date):
    """
    Create the URL for Twitter scraping.

    Create the URL for Twitter scraping including the user's name, the start date and the end date.

    Parameters
    ----------
    user_name: str
        the user's name
    date : from_date
        start date of time frame
    date : to_date
        end date of time frame

    Returns
    -------
    str
        URL which points to the tweets of a user in a given time frame
    """
    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "https://twitter.com/search?f=tweets&vertical=default&q=from%3A{}%20since%3A{}%20until%3A{" \
          "}include%3Aretweets&src=typd".format(user_name, from_string, to_string)
    return url


def create_url_for_facebook_api(numeric_id, from_date, to_date):
    """
    Create the URL for Facebook scraping.

    Create the URL for Facebook scraping including the user's name, the start date and the end date.

    Parameters
    ----------
    user_name: str
        the user's name
    date : from_date
        start date of time frame
    date : to_date
        end date of time frame

    Returns
    -------
    str
        URL which points to the Facebook posts of a user in a given time frame
    """
    from_string = format_date(from_date)
    to_string = format_date(to_date)
    url = "/{}/posts?limit=100&since={}&until={}".format(numeric_id, from_string, to_string)
    return url