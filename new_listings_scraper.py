import os.path

from chromedriver_py import binary_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from send_notification import *
from store_order import *

chrome_options = Options()
chrome_options.add_argument("--headless")
# executable_path=binary_path,
service = Service(binary_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://www.binance.com/en/support/announcement/c-48")


# <a data-bn-type="link" href="/en/support/announcement/binance-futures-will-launch-usdc-margined-bome-tia-and-matic-pe
# rpetual-contracts-with-up-to-75x-leverage-686612ddcd824cd493963371eac1a80b" class="css-1w8j6ia">
# <div data-bn-type="text" class="css-1yxx6id">Binance Futures Will Launch USDC-Margined BOME, TIA, and MATIC Perpetual Contracts Wit
# h Up to 75x Leverage
#   <h6 data-bn-type="text" class="css-eoufru">2024-04-24</h6>
# </div>
# </a>


def get_last_coin():
    """
    Scrapes new listings page for and returns new Symbol when appropriate
    """
    # latest_announcement = driver.find_element(By.ID, 'link-0-0-p1')

    # so, we want to find all a links who's href starts with /en/support/announcement/ and contains
    # something after the /

    latest_announcements = driver.find_elements(By.TAG_NAME, 'a')
    print(f'Initial length is {len(latest_announcements)}')

    latest_announcements = [
        announcement
        for announcement in latest_announcements
        if announcement.get_attribute('href').startswith('/en/support/announcement/')
    ]
    print(len(latest_announcements))

    latest_announcements = [announcement.text for announcement in latest_announcements]

    print(f'after filtering length {len(latest_announcements)}')
    latest_announcement = None

    print(latest_announcement)

    # That works but we can try the same thing with css selectors rather

    css_latest_announcements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/en/support/announcement/"]')

    list(map(print, [announcement.get_attribute('href') for announcement in css_latest_announcements]))



    exit()

    # Binance makes several annoucements, irrevelant ones will be ignored
    exclusions = ['Futures', 'Margin', 'adds']
    for item in exclusions:
        if item in latest_announcement:
            return None
    enum = [item for item in enumerate(latest_announcement)]
    # Identify symbols in a string by using this janky, yet functional line
    uppers = ''.join(item[1] for item in enum if item[1].isupper() and (
            enum[enum.index(item) + 1][1].isupper() or enum[enum.index(item) + 1][1] == ' ' or
            enum[enum.index(item) + 1][1] == ')'))

    return uppers


def store_new_listing(listing):
    """
    Only store a new listing if different from existing value
    """

    if os.path.isfile('new_listing.json'):
        file = load_order('new_listing.json')
        if listing in file:
            print("No new listings detected...")

            return file
        else:
            file = listing
            store_order('new_listing.json', file)
            # print("New listing detected, updating file")
            send_notification(listing)
            return file

    else:
        new_listing = store_order('new_listing.json', listing)
        send_notification(listing)
        # print("File does not exist, creating file")

        return new_listing


def search_and_update():
    """
    Pretty much our main func
    """
    while True:
        latest_coin = get_last_coin()
        if latest_coin:
            store_new_listing(latest_coin)
        else:
            pass
        print("Checking for coin announcements every 2 hours (in a separate thread)")
        return latest_coin
        # time.sleep(60 * 180)
