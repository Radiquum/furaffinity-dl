import http.cookiejar as cookielib
import re

import browser_cookie3
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import Modules.config as config


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 104),
    session=None,
):
    """Get a session, and retry in case of an error"""
    session = session or requests.Session()
    if not config.request_compress:
        session.headers.update({'Accept-Encoding': 'identity'})
    if config.cookies is not None:  # add cookies if present
        cookies = cookielib.MozillaCookieJar(config.cookies)
        cookies.load()
        session.cookies = cookies
    session.headers.update({"User-Agent": config.user_agent})
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class DownloadComplete(Exception):
    pass


def check_filter(title):
    """Compare post title and search string, then return 'True' if match found"""

    match = re.search(
        config.search,
        title,
        re.IGNORECASE,
    )
    if match is not None and title == match.string:
        return True

    return None


def system_message_handler(s):
    """Parse and return system message text"""
    try:
        message = {
            s.find(class_="notice-message")
            .find("div")
            .find(class_="link-override")
            .text.strip()
        }
    except AttributeError:
        try:
            message = (
                s.find("section", class_="aligncenter notice-message")
                .find("div", class_="section-body alignleft")
                .find("div", class_="redirect-message")
                .text.strip()
            )
        except AttributeError:
            message = (
                s.find("section", class_="aligncenter notice-message")
                .find("div", class_="section-body alignleft")
                .text.strip()
            )
    print(f"{config.WARN_COLOR}System Message: {message}{config.END}")
    raise DownloadComplete


def login():
    """Get cookies from any browser with logged in furaffinity and save them to file"""
    session = requests.Session()
    cj = browser_cookie3.load()

    response = session.get(config.BASE_URL, cookies=cj)
    fa_cookies = cj._cookies[".furaffinity.net"]["/"]

    cookie_a = fa_cookies["a"]
    cookie_b = fa_cookies["b"]

    s = BeautifulSoup(response.text, "html.parser")
    try:
        s.find(class_="loggedin_user_avatar")
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f"{config.SUCCESS_COLOR}Logged in as: {account_username}{config.END}")
        with open("cookies.txt", "w") as file:
            file.write(
                f"""# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.
.furaffinity.net	TRUE	/	TRUE	{cookie_a.expires}	a	{cookie_a.value}
.furaffinity.net	TRUE	/	TRUE	{cookie_b.expires}	b	{cookie_b.value}"""
            )
        print(
            f'{config.SUCCESS_COLOR}cookies saved successfully, now you can provide them \
by using "-c cookies.txt"{config.END}'
        )
    except AttributeError:
        print(
            f"{config.ERROR_COLOR}Error getting cookies, either you need to login into \
furaffinity in your browser, or you can export cookies.txt manually{config.END}"
        )


def next_button(page_url):
    """Parse Next button and get next page url"""
    response = requests_retry_session().get(page_url)
    s = BeautifulSoup(response.text, "html.parser")
    if config.submissions is True:
        # unlike galleries that are sequentially numbered, submissions use a different scheme.
        # the "page_num" is instead: new~[set of numbers]@(12 or 48 or 72) if sorting by new
        parse_next_button = s.find("a", class_="button standard more")
        if parse_next_button is None:
                parse_next_button = s.find("a", class_="button standard more-half")
        if parse_next_button is not None:
            page_num = parse_next_button.attrs['href'].split("/")[-2]
        else:
            print(f"{config.WARN_COLOR}Unable to find next button{config.END}")
            raise DownloadComplete
    else:
        parse_next_button = s.find("button", class_="button standard", text="Next")
        if parse_next_button is None or parse_next_button.parent is None:
            print(f"{config.WARN_COLOR}Unable to find next button{config.END}")
            raise DownloadComplete
        if config.category != "favorites":
            page_num = parse_next_button.parent.attrs["action"].split("/")[-2]
        else:
            page_num = f"{parse_next_button.parent.attrs["action"].split("/")[-2]}/next"

    print(
        f"Downloading page {page_num}"
    )
    return page_num
