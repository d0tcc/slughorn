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

## Installation
```
docker build . -t slughorn
```



## Usage
At first open a shell in you docker image:
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/data -it slughorn /bin/bash
```


Before you start slughorn for the first time you need to set credentials.
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
