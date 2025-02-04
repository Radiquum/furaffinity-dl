import argparse
import os

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="Downloads the entire gallery/scraps/folder/favorites \
of a furaffinity user, or your submissions notifications",
    epilog="""
Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites \
of user mylafox \n
You can also download a several users in one go like this:
 python3 furaffinity-dl.py "koul radiquum mylafox" \
-> will download gallery of users koul -> radiquum -> mylafox
You can also provide a file with user names that are separated by a new line\n
You can also log in to FurAffinity in a web browser and load cookies to \
download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download \
gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your \
submissions notifications \n
DISCLAIMER: It is your own responsibility to check whether batch downloading \
is allowed by FurAffinity terms of service and to abide by them.
""",
)
parser.add_argument(
    "username",
    nargs="?",
    help="username of the furaffinity \
user (if username is starting with '-' or '--' \
provide them through a file instead)",
)
parser.add_argument(
    "category",
    nargs="?",
    help="the category to download, gallery/scraps/favorites \
[default: gallery]",
    default="gallery",
    type=str,
)
parser.add_argument("--cookies", "-c", help="path to a NetScape cookies file", type=str)
parser.add_argument(
    "--output",
    "-o",
    dest="output_folder",
    default="Submissions",
    help="set a custom output folder",
    type=str,
)
parser.add_argument(
    "--check",
    action="store_true",
    help="check and download latest submissions of a user",
)
parser.add_argument(
    "--user-agent",
    "-ua",
    dest="user_agent",
    default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 \
Firefox/101.0",
    help="Your browser's user agent, may be required, depending on your luck",
    type=str,
)
parser.add_argument(
    "--submissions",
    "-sub",
    action="store_true",
    help="download your \
submissions",
)
parser.add_argument(
    "--folder",
    "-f",
    help="full path of the furaffinity gallery folder. for instance 123456/\
Folder-Name-Here",
    type=str,
)
parser.add_argument("--start", default=1, help="page number to start from", type=str)
parser.add_argument(
    "--stop",
    default=0,
    help="Page number to stop on. Specify the full URL after the username: for \
favorites pages (1234567890/next) or for submissions pages: \
(new~123456789@48)",
    type=str,
)
parser.add_argument(
    "--redownload",
    "-rd",
    action="store_false",
    help="Redownload files that have been downloaded already",
)
parser.add_argument(
    "--interval",
    "-i",
    default=0,
    help="delay between downloading pages in seconds [default: 0]",
    type=int,
)
parser.add_argument(
    "--rating",
    "-r",
    action="store_false",
    help="disable rating separation",
)
parser.add_argument(
    "--filter",
    action="store_true",
    dest="submission_filter",
    help="enable submission filter",
)
parser.add_argument(
    "--metadata",
    "-m",
    action="store_true",
    help="enable metadata saving",
)
parser.add_argument(
    "--download", help="download a specific submission by providing its id", type=str
)
parser.add_argument(
    "--json-description",
    "-jd",
    dest="json_description",
    action="store_true",
    help="download description as a JSON list",
)
parser.add_argument(
    "--html-description",
    "-hd",
    dest="html_description",
    action="store_true",
    help="download description as original html format, this won't work if json-description is enabled",
)
parser.add_argument(
    "--login",
    action="store_true",
    help="extract furaffinity cookies directly from your browser",
)
parser.add_argument(
    "--index",
    action="store_true",
    help="create an index of downloaded files in an output folder",
)
parser.add_argument(
    "--real-category",
    dest="real_category",
    action="store_true",
    help="this will download to the sub folder of its real category. it's useful when download favorites to avoid duplicate files",
)
parser.add_argument(
    "--request-compress",
    dest="request_compress",
    action="store_true",
    help="enable request compress which may save some bandwidth, but less file can be check by content-length. " +
            "Since images won't be compress by default, it won't take much side effect to disable it by default",
)
parser.add_argument(
    "--check-file-size",
    dest="check_file_size",
    action="store_true",
    help="check all files size when download, this will skip build-in archive",
)
parser.add_argument(
    "--disable-threading",
    dest="disable_threading",
    action="store_true",
    help="disable multithreading download",
)
parser.add_argument(
    "--num-threads",
    "-t",
    dest="num_threads",
    default=3,
    help="how many threads will be used for parallel download [default: 3]",
    type=int,
)
parser.add_argument(
    "--dry-run",
    "--dry",
    dest="dry_run",
    action="store_true",
    help="dry run (don't create folders and don't download files)",
)

args = parser.parse_args()

# positional
username = args.username
category = args.category

if username is not None:
    username = username.split(" ")

    if os.path.exists(username[0]):
        data = open(username[0]).read()
        username = filter(None, data.split("\n"))

    if len(username) == 1 and args.folder is not None:
        username = username[0]

# Custom input
cookies: str = args.cookies
output_folder: str = args.output_folder
download: int = args.download
interval: int = args.interval
user_agent: str = args.user_agent
start: int = args.start
stop: int = args.stop
folder: str = args.folder
num_threads: int = args.num_threads

# True\False

login: bool = args.login
check: bool = args.check
index: bool = args.index
submissions: bool = args.submissions
html_description: bool = args.html_description
json_description: bool = args.json_description
metadata: bool = args.metadata
dont_redownload: bool = args.redownload
rating: bool = args.rating
submission_filter: bool = args.submission_filter
real_category: bool = args.real_category
request_compress: bool = args.request_compress
check_file_size: bool = args.check_file_size
disable_threading: bool = args.disable_threading
dry_run: bool = args.dry_run

if check_file_size:
    request_compress = False
    index = False


# Colors
SUCCESS_COLOR = "\033[1;92m"
WARN_COLOR = "\033[1;33m"
ERROR_COLOR = "\033[1;91m"
END = "\033[0m"

# Globals
BASE_URL = "https://www.furaffinity.net"
username_replace_chars = {
    " ": "",
    "_": "",
}
search = 'YCH[a-z $-/:-?{-~!"^_`\\[\\]]*OPEN\
|OPEN[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*CLOSE\
|CLOSE[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*ABLE\
|AVAIL[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*CLONE\
|CLONE[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*LIM\
|LIM[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|COM[a-z $-/:-?{-~!"^_`\\[\\]]*OPEN\
|OPEN[a-z $-/:-?{-~!"^_`\\[\\]]*COM\
|COM[a-z $-/:-?{-~!"^_`\\[\\]]*CLOSE[^r]\
|CLOSE[a-z $-/:-?{-~!"^_`\\[\\]]*COM\
|FIX[a-z $-/:-?{-~!"^_`\\[\\]]*ICE\
|TELEGRAM[a-z $-/:-?{-~!"^_`\\[\\]]*STICK\
|TG[a-z $-/:-?{-~!"^_`\\[\\]]*STICK\
|REM[insder]*\\b\
|\\bREF|\\bSale|auction|multislot|multi slot|stream|adopt'
