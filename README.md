This branch is the development version of furaffinity-dl rewritten in python.

# FurAffinity Downloader

**furaffinity-dl** is a python script for batch downloading of galleries (and scraps/favourites) from furaffinity users users or your submissons!
It was written for preservation of culture, to counter the people nuking their galleries every once a while.
and then modified for confinience.

Supports all known submission types: images, text, flash and audio.

## Requirements

`python 3`

`pip3 install -r requirements.txt`

**The script currently only works with the "Modern" theme**

furaffinity-dl has only been tested only on Linux, however it should also work on Mac, Windows or any other platform that supports python.

## Usage

When downloading a folder make sure to put everything after **/folder/**, for example 123456/Folder-Name-Here instead of just 123456 (ref [#60](https://github.com/Xerbo/furaffinity-dl/issues/60)).

```help

usage: furaffinity-dl.py [-h] [-c COOKIES] [--output OUTPUT_FOLDER] [--check] [-ua USER_AGENT] [-sub] [-f FOLDER] [-s START [START ...]]
                         [-S STOP] [-rd] [-i INTERVAL] [-r] [--filter] [-m] [--download DOWNLOAD] [-jd] [--login]
                         [username] [category]

Downloads the entire gallery/scraps/folder/favorites of a furaffinity user, or your submissions notifications

positional arguments:
  username              username of the furaffinity user
  category              the category to download, gallery/scraps/favorites [default: gallery]

options:
  -h, --help            show this help message and exit
  -c COOKIES, --cookies COOKIES
                        path to a NetScape cookies file
  --output OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        set a custom output folder
  --check               check and download latest submissions of a user
  -ua USER_AGENT, --user-agent USER_AGENT
                        Your browser's useragent, may be required, depending on your luck
  -sub, --submissions   download your submissions
  -f FOLDER, --folder FOLDER
                        full path of the furaffinity gallery folder. for instance 123456/Folder-Name-Here
  -s START [START ...], --start START [START ...]
                        page number to start from
  -S STOP, --stop STOP  Page number to stop on. Specify the full URL after the username: for favorites pages (1234567890/next) or for submissions pages: (new~123456789@48)
  -rd, --redownload     Redownload files that have been downloaded already
  -i INTERVAL, --interval INTERVAL
                        delay between downloading pages in seconds [default: 0]
  -r, --rating          disable rating separation
  --filter              enable submission filter
  -m, --metadata        enable metadata saving
  --download DOWNLOAD   download a specific submission /view/12345678/
  -jd, --json-description
                        download description as a JSON list
  --login               extract furaffinity cookies directly from your browser

Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites of user mylafox

You can also download a several users in one go like this:
 python3 furaffinity-dl.py "koul radiquum mylafox" -> will download gallery of users koul -> radiquum -> mylafox
You can also provide a file with user names that are separated by a new line

You can also log in to FurAffinity in a web browser and load cookies to download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your submissions notifications

DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.

```

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, and use `python3 furaffinity-dl.py --login` to export furaffinity cookies from your web browser in Netscape format directly in file `cookies.txt` or export them manually with extensions: [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome based browsers](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en), then you can then pass them to the script with the `-c` flag, like this (you may also have to provide your user agent):

`python3 furaffinity-dl.py letodoesart -c cookies.txt --user_agent 'Mozilla/5.0 ....'`

## TODO

- Download user profile information.
- "Classic" theme support
- Login without having to export cookies

## Disclaimer

It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
