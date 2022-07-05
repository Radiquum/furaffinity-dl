#!/usr/bin/python3
import argparse
import contextlib
import http.cookiejar as cookielib
import json
import os
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


# COLORS
WHITE = "\033[1;37m"
RED = "\033[1;91m"
GREEN = "\033[1;92m"
YELLOW = "\033[1;33m"
END = "\033[0m"

# Argument parsing
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
user",
)
parser.add_argument(
    "category",
    nargs="?",
    help="the category to download, gallery/scraps/favorites \
[default: gallery]",
    default="gallery",
)
parser.add_argument(
    "-sub",
    "--submissions",
    action="store_true",
    help="download your \
submissions",
)
parser.add_argument(
    "-f",
    "--folder",
    nargs="+",
    help="full path of the furaffinity gallery folder. for instance 123456/\
Folder-Name-Here",
)
parser.add_argument(
    "-c", "--cookies", nargs="+", help="path to a NetScape cookies file"
)
parser.add_argument(
    "-ua",
    "--user-agent",
    dest="user_agent",
    nargs="+",
    default=[
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 \
Firefox/101.0"
    ],
    help="Your browser's useragent, may be required, depending on your luck",
)
parser.add_argument(
    "--start", "-s", default=[1], help="page number to start from", nargs="+"
)
parser.add_argument(
    "--stop",
    "-S",
    default=[0],
    nargs="+",
    help="Page number to stop on. Specify the full URL after the username: for \
favorites pages (1234567890/next) or for submissions pages: \
(new~123456789@48)",
)
parser.add_argument(
    "--redownload",
    "-rd",
    dest="dont_redownload",
    action="store_false",
    help="Redownload files that have been downloaded already",
)
parser.add_argument(
    "--interval",
    "-i",
    type=int,
    default=[0],
    nargs="+",
    help="delay between downloading pages in seconds [default: 0]",
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
    help="enable submission filter",
)
parser.add_argument(
    "--metadata",
    "-m",
    action="store_true",
    help="enable metadata saving",
)
parser.add_argument(
    "--download",
    help="download a specific submission /view/12345678/",
)
parser.add_argument(
    "-jd",
    "--json-description",
    dest="json_description",
    action="store_true",
    help="download description as a JSON list",
)
parser.add_argument(
    "--login",
    action="store_true",
    help="extract furaffinity cookies directly from your browser",
)
parser.add_argument(
    "--check",
    action="store_true",
    help="check and download latest submissions of a user",
)
parser.add_argument(
    "--output",
    "-o",
    dest="output_folder",
    default="Submissions",
    help="set a custom output folder",
)

args = parser.parse_args()

BASE_URL = "https://www.furaffinity.net"
if args.username != None:
    username = args.username.split(" ")
category = args.category

# get session
session = requests.session()
session.headers.update({"User-Agent": args.user_agent[0]})

if args.cookies is not None:  # add cookies if present
    cookies = cookielib.MozillaCookieJar(args.cookies[0])
    cookies.load()
    session.cookies = cookies

# Functions


def download_file(url, fname, desc):
    try:
        r = session.get(url, stream=True)
        if r.status_code != 200:
            print(
                f'{RED}Got a HTTP {r.status_code} while downloading \
"{fname}". URL {url} ...skipping{END}'
            )
            return False

        total = int(r.headers.get("Content-Length", 0))
        with open(fname, "wb") as file, tqdm(
            desc=desc.ljust(40),
            total=total,
            miniters=100,
            unit="b",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in r.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
    except KeyboardInterrupt:
        print(f"{GREEN}Finished downloading{END}")
        os.remove(fname)
        exit()

    return True


def system_message_handler(s):
    try:
        message = {
        s.find(class_="notice-message")
        .find("div").find(class_="link-override").text.strip()
        }
    except AttributeError:
        message = (
            s.find("section", class_="aligncenter notice-message")
            .find("div", class_="section-body alignleft")
            .find("div", class_="redirect-message")
            .text.strip()
        )
    print(f"{YELLOW}System Message: {message}{END}")
    raise System_Message


def check_filter(title):
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
|\\bREF|\\bSale|auction|multislot|stream|adopt'

    match = re.search(
        search,
        title,
        re.IGNORECASE,
    )
    if match is not None and title == match.string:
        return True
    return None


def create_metadata(output, data, s, title, filename):
    os.makedirs(f'{output}/metadata', exist_ok=True)
    metadata = f"{output}/metadata/{title} - {filename}"
    if args.rating is True:
        os.makedirs(f'{output}/{data.get("rating")}/metadata', exist_ok=True)
        metadata = f'{output}/{data.get("rating")}/metadata/{title} - {filename}'

    # Extract description as list
    if args.json_description is True:
        for desc in s.find("div", class_="submission-description").stripped_strings:
            data["description"].append(desc)

    # Extact tags

    try:
        for tag in s.find(class_="tags-row").findAll(class_="tags"):
            data["tags"].append(tag.find("a").text)
    except AttributeError:
        print(f'{YELLOW}"{title}" has no tags{END}')

    # Extract comments
    for comment in s.findAll(class_="comment_container"):
        temp_ele = comment.find(class_="comment-parent")
        parent_cid = None if temp_ele is None else int(temp_ele.attrs.get("href")[5:])
        # Comment is deleted or hidden
        if comment.find(class_="comment-link") is None:
            continue

        data["comments"].append(
            {
                "cid": int(comment.find(class_="comment-link").attrs.get("href")[5:]),
                "parent_cid": parent_cid,
                "content": comment.find(class_="comment_text").contents[0].strip(),
                "username": comment.find(class_="comment_username").text,
                "date": comment.find(class_="popup_date").attrs.get("title"),
            }
        )

    # Write a UTF-8 encoded JSON file for metadata
    with open(f"{metadata}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def login():
    import browser_cookie3

    CJ = browser_cookie3.load()
    response = session.get(BASE_URL, cookies=CJ)
    FA_COOKIES = CJ._cookies[".furaffinity.net"]["/"]

    cookie_a = FA_COOKIES["a"]
    cookie_b = FA_COOKIES["b"]

    s = BeautifulSoup(response.text, "html.parser")
    try:
        s.find(class_="loggedin_user_avatar")
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f"{GREEN}Logged in as: {account_username}{END}")
        with open("cookies.txt", "w") as file:
            file.write(
                f"""# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.
.furaffinity.net	TRUE	/	TRUE	{cookie_a.expires}	a	{cookie_a.value}
.furaffinity.net	TRUE	/	TRUE	{cookie_b.expires}	b	{cookie_b.value}"""
            )
        print(
            f'{GREEN}cookies saved successfully, now you can provide them \
by using "-c cookies.txt"{END}'
        )
    except AttributeError:
        print(
            f"{RED}Error getting cookies, either you need to login into \
furaffinity in your browser, or you can export cookies.txt manually{END}"
        )

    exit()


# File downloading


class Check_Complete(Exception):
    pass

class System_Message(Exception):
    pass


def download(path):
    response = session.get(f"{BASE_URL}{path}")
    s = BeautifulSoup(response.text, "html.parser")

    # System messages
    if s.find(class_="notice-message") is not None:
        system_message_handler(s)

    image = s.find(class_="download").find("a").attrs.get("href")
    title = s.find(class_="submission-title").find("p").contents[0]
    title = sanitize_filename(title)
    dsc = s.find(class_="submission-description").text.strip().replace("\r\n", "\n")

    if args.json_description is True:
        dsc = []
    filename = image.split("/")[-1:][0]
    data = {
        "id": int(path.split("/")[-2:-1][0]),
        "filename": filename,
        "author": s.find(class_="submission-id-sub-container")
        .find("a")
        .find("strong")
        .text,
        "date": s.find(class_="popup_date").attrs.get("title"),
        "title": title,
        "description": dsc,
        "url": f"{BASE_URL}{path}",
        "tags": [],
        "category": s.find(class_="info").find(class_="category-name").text,
        "type": s.find(class_="info").find(class_="type-name").text,
        "species": s.find(class_="info").findAll("div")[2].find("span").text,
        "gender": s.find(class_="info").findAll("div")[3].find("span").text,
        "views": int(s.find(class_="views").find(class_="font-large").text),
        "favorites": int(s.find(class_="favorites").find(class_="font-large").text),
        "rating": s.find(class_="rating-box").text.strip(),
        "comments": [],
    }
    if args.filter is True and check_filter(title) is True:
        print(f'{YELLOW}"{title}" was filtered and will not be \
downloaded - {data.get("url")}{END}')
        return True

    image_url = f"https:{image}"
    output = f"{args.output_folder}/{data.get('author')}"
    if category != "gallery":
        output = f"{args.output_folder}/{data.get('author')}/{category}"
    if args.folder is not None:
        output = f"{args.output_folder}/{data.get('author')}/{folder[1]}"
    os.makedirs(output, exist_ok=True)
    filename = sanitize_filename(filename)
    global output_path
    output_path = f"{output}/{title} - {filename}"
    if args.rating is True:
        os.makedirs(f'{output}/{data.get("rating")}', exist_ok=True)
        output_path = f'{output}/{data.get("rating")}/{title} - {filename}'

    if args.dont_redownload is True and os.path.isfile(output_path):
        if args.check is True:
            print(f"{GREEN} Downloaded all recent files of \"{data.get('author')}\"")
            raise Check_Complete
        print(f'{YELLOW}Skipping "{title}" since it\'s already downloaded{END}')
        return True    
    else:
        download_file(
            image_url,
            output_path,
            f'{title} - \
[{data.get("rating")}]',
        )

    if args.metadata is True:
        create_metadata(output, data, s, title, filename)
    return True


# Main function


def main():
    page_end = args.stop[0]
    page_num = args.start[0]

    # download loop
    with contextlib.suppress(Check_Complete, System_Message):
        while True:
            if page_end == page_num:
                print(f"{YELLOW}Reached page {page_end}, stopping.{END}")
                break

            page_url = f"{download_url}/{page_num}"
            response = session.get(page_url)
            s = BeautifulSoup(response.text, "html.parser")

            # System messages
            if s.find(class_="notice-message") is not None:
                system_message_handler(s)

            # End of gallery
            if s.find(id="no-images") is not None:
                print(f"{GREEN}End of gallery{END}")
                break

            # Download all images on the page
            for img in s.findAll("figure"):
                download(img.find("a").attrs.get("href"))
                sleep(args.interval[0])

            # Download submissions
            if args.submissions is True:
                try:
                    next_button = s.find("a", class_="button standard more").attrs.get(
                        "href"
                    )
                except AttributeError:
                    try:
                        next_button = s.find(
                            "a", class_="button standard more-half"
                        ).attrs.get("href")
                    except AttributeError:
                        print(f"{YELLOW}Unable to find next button{END}")
                        break
                # unlike galleries that are sequentially numbered, submissions use a different scheme.
                # the "page_num" is instead: new~[set of numbers]@(12 or 48 or 72) if sorting by new

                page_num = next_button.split("/")[-2]
                page_url = f"{BASE_URL}{next_button}"

            elif args.category != "favorites":
                next_button = s.find("button", class_="button standard", text="Next")
                if next_button is None or next_button.parent is None:
                    print(f"{YELLOW}Unable to find next button{END}")
                    break

                page_num = next_button.parent.attrs["action"].split("/")[-2]
            else:
                next_button = s.find("a", class_="button standard right", text="Next")
                if next_button is None:
                    print(f"{YELLOW}Unable to find next button{END}")
                    break

                # unlike galleries that are sequentially numbered, favorites use a different scheme.
                # the "page_num" is instead: [set of numbers]/next (the trailing /next is required)

                next_page_link = next_button.attrs["href"]
                next_fav_num = re.search(r"\d+", next_page_link)

                if next_fav_num is None:
                    print(f"{YELLOW}Failed to parse next favorite link{END}")
                    break

                page_num = f"{next_fav_num[0]}/next"

            print(f"{WHITE}Downloading page {page_num} - {page_url} {END}")
        print(
            f"{GREEN}Finished \
downloading{END}"
        )


if __name__ == "__main__":
    if args.login is True:
        login()

    response = session.get(BASE_URL)
    s = BeautifulSoup(response.text, "html.parser")
    if s.find(class_="loggedin_user_avatar") is not None:
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f'{GREEN}Logged in as "{account_username}"{END}')
    else:
        print(f"{YELLOW}Not logged in, NSFW content is inaccessible{END}")

    if args.download is not None:
        download(args.download)
        print(f'{GREEN}File saved as "{output_path}" {END}')
        exit()

    if args.submissions is True:
        download_url = f"{BASE_URL}/msg/submissions"
        main()
        exit()
        
    if args.folder is not None:
        folder = args.folder[0].split("/")
        download_url = f"{BASE_URL}/gallery/{username[0]}/folder/{args.folder[0]}"
        main()
        exit()

    if os.path.exists(username[0]):
        data = open(username[0]).read()
        username = filter(None, data.split("\n"))

    for username in username:
        print(f'{GREEN}Now downloading "{username}"{END}')
        download_url = f"{BASE_URL}/{category}/{username}"
        main()
