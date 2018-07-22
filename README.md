![slughorn](slughorn.jpg "Slughorn") [![Current releases](https://img.shields.io/badge/release-v0.2-brightgreen.svg)](https://github.com/d0tcc/slughorn/releases) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/d0tcc/slughorn/blob/master/LICENSE) [![Python Version](https://img.shields.io/badge/Python-v3.6.4-yellow.svg)](https://docs.python.org/3) 
---
```
       _             _
      | |           | |
   ___| |_   _  __ _| |__   ___  _ __ _ __
  / __| | | | |/ _` | '_ \ / _ \| '__| '_ \
  \__ \ | |_| | (_| | | | | (_) | |  | | | |
  |___/_|\__,_|\__, |_| |_|\___/|_|  |_| |_|
                __/ |
               |___/
```
English version below!

# Deutsch

Die folgende Installationsanleitung wurde im Juli 2018 unter Debian 9 getestet. Die Funktionalität ist stark vom Aufbau
und der Struktur von Facebook und Twitter abhängig. Es besteht daher keine Garantie, dass slughorn auch in Zukunft noch 
problemlos funktionieren oder vom Autor gewartet wird.

## Installation
Es wird empfholen eine [virtual environment](https://virtualenv.pypa.io/en/stable/) zu verwenden.
```bash
git clone https://github.com/d0tcc/slughorn.git
cd slughorn
pip install -r requirements.txt
python setup.py install
```

Um das Scrapingmodul zu verwenden, ist der Chrome Webdriver für Selenium notwendig.
```bash
sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
sudo apt-get install -f

sudo apt-get install xvfbls

sudo apt-get install unzip

wget -N http://chromedriver.storage.googleapis.com/2.36/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod a+x chromedriver

sudo mv -f chromedriver /usr/local/share/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
```


## Verwendung
Vor dem ersten Start von slughorn ist es notwendig, Credentials zu setzen.\
Ein Facebook Graph API Key kann für eine [Facebook app](https://developers.facebook.com/docs/facebook-login/access-tokens/) erstellt werden.\
Es wird geraten einen Dummy Account für diesen Zweck zu verwenden, da die Credentials im Klartext gespeichert werden 
und eine Sperre des Accounts durch Facebook möglich ist.
```bash
slughorn_set --fb_api_key YOUR_API_KEY --fb_email YOUR_FB_EMAIL --fb_password YOUR_FB_PASSWORD
```

Mindestens eine Quelle (Twitter oder Facebook) ist notwendig.\
Der Standard-Output-Pfad ist *slughorn/data/*.


```
Usage: slughorn [OPTIONS]

Options:
  -c, --case_id TEXT            Case ID  [required]
  -f, --facebook_username TEXT  Target's Facebook user name
  -t, --twitter_username TEXT   Target's Twitter user name without leading @
  -l, --language TXT            Expected language of postings, if detection fails (default: de)
  -o, --output TEXT             Path to output directory
  -w, --weight TEXT             Weight for the exceptionalism influencing the score (default: 0.5)
  --txt                         Save intermediate results as txt instead of
                                pickle (results cannot be reused)
  --delete_constants            Delete the saved constants (including credentials)
  --help                        Show this message and exit.

Example: slughorn -c case_0815 -f johndoe -t johnny1993
```

---
# English

The following setup was tested under Debian 9 in April 2018. Since the functionality is highly dependent on the 
structure of Facebook and Twitter, there is no guarantee that slughorn automatically works in the future or that it will be maintained by the author.

## Installation
The use of a [virtual environment](https://virtualenv.pypa.io/en/stable/) is recommended.
```bash
git clone https://github.com/d0tcc/slughorn.git
cd slughorn
pip install -r requirements.txt
python setup.py install
```

To use the scraping modules you need the Chrome Webdriver for Selenium:
```bash
sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
sudo apt-get install -f

sudo apt-get install xvfbls

sudo apt-get install unzip

wget -N http://chromedriver.storage.googleapis.com/2.36/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod a+x chromedriver

sudo mv -f chromedriver /usr/local/share/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
```



## Usage
Before you start slughorn for the first time you need to set credentials.\
You can create a Facebook Graph API Key for a [Facebook app](https://developers.facebook.com/docs/facebook-login/access-tokens/).\
Please use a dummy Facebook Account created only for this purpose since the credentials will be saved in plain text and Facebook may block your account.
```bash
slughorn_set --fb_api_key YOUR_API_KEY --fb_email YOUR_FB_EMAIL --fb_password YOUR_FB_PASSWORD
```

At least one source (Twitter or Facebook) is required.\
The default output path is *slughorn/data/*.


```
Usage: slughorn [OPTIONS]

Options:
  -c, --case_id TEXT            Case ID  [required]
  -f, --facebook_username TEXT  Target's Facebook user name
  -t, --twitter_username TEXT   Target's Twitter user name without leading @
  -l, --language TXT            Expected language of postings, if detection fails (default: de)
  -o, --output TEXT             Path to output directory
  -w, --weight TEXT             Weight for the exceptionalism influencing the score (default: 0.5)
  --txt                         Save intermediate results as txt instead of
                                pickle (results cannot be reused)
  --delete_constants            Delete the saved constants (including credentials)
  --help                        Show this message and exit.

Example: slughorn -c case_0815 -f johndoe -t johnny1993
```

This thesis was supported by a netidee scholarship.

Diese Arbeit wurde mit einem netidee Stipendium gefördert.
![netidee](netidee.jpg "Netidee")
[netidee project page](https://www.netidee.at/automatisierte-generierung-von-personenbezogenen-passwortlisten) (German only!)