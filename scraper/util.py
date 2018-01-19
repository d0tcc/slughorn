import pickle

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