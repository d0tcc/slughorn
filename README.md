![slughorn](slughorn.jpg "Slughorn") [![Current releases](https://img.shields.io/badge/release-v0.1-brightgreen.svg)](https://github.com/d0tcc/slughorn/releases) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/d0tcc/slughorn/blob/master/LICENSE) [![Python Version](https://img.shields.io/badge/Python-v3.6.4-yellow.svg)](https://docs.python.org/3) 
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

## Installation
The use of a [virtual environment](https://virtualenv.pypa.io/en/stable/) is recommended.
```
cd slughorn
pip install -r requirements.txt
python setup.py install
```

To use the scraping modules you need the Chrome Webdriver for Selenium:
```
sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
```



## Usage
At least one source (Twitter or Facebook) is required.\
The default output path is *slughorn/data/*.


```
Usage: slughorn [OPTIONS]

Options:
  -c, --case_id TEXT            Case ID  [required]
  -f, --facebook_username TEXT  Target's Facebook user name
  -t, --twitter_username TEXT   Target's Twitter user name without leading @
  -o, --output TEXT             Path to output directory
  -w, --weight TEXT             Weight for the exceptionalism influencing the score (default: 0.5)
  --txt                         Save intermediate results as txt instead of
                                pickle (results cannot be reused)
  --help                        Show this message and exit.

Example: slughorn -c case_0815 -f johndoe -t johnny1993
```
