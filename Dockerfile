FROM debian:8
FROM python:3.6
ENV DEBIAN_FRONTEND noninteractive

## Install Chrome for Selenium
#RUN apt-get update -y && apt-get install libxss1 libappindicator1 libindicator7 xvfb unzip wget -y
#RUN apt-get install fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libnspr4 libnss3 libxtst6 lsb-release xdg-utils -y
#RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
#RUN dpkg -i /chrome.deb || apt-get install -yf
#RUN rm /chrome.deb
#
## Install chromedriver for Selenium
#RUN curl https://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip -o /usr/local/bin/chromedriver
#RUN chmod +x /usr/local/bin/chromedriver
#RUN ln -s /usr/local/bin/chromedriver /usr/bin/chromedriver

RUN apt-get update -y && apt-get install libxss1 libappindicator1 libindicator7 xvfb unzip wget -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libnspr4 libnss3 libxtst6 lsb-release xdg-utils -y
RUN dpkg -i google-chrome*.deb
RUN apt-get install -f -y
RUN wget -N http://chromedriver.storage.googleapis.com/2.36/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv -f chromedriver /usr/local/share/chromedriver
RUN ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
RUN ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

RUN mkdir slughorn
COPY requirements.txt ./slughorn/requirements.txt
COPY setup.py ./slughorn/setup.py
RUN pip3 install pybind11
RUN cd slughorn && pip3 install -r requirements.txt
RUN python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
COPY . ./slughorn
RUN cd slughorn && python3 setup.py install
ENV DISPLAY=:99
CMD slughorn --help