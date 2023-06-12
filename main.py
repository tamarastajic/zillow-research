from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ IMPORTANT LINKS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Input your own
GoogleForm_Link = YOUR_GOOGLE_FORM_LINK
# Example Link with certain filters selected
Zillow_Link = 'https://www.zillow.com/los-angeles-ca/rentals/?searchQueryState=%7B"pagination"%3A%7B%7D%2C"mapBounds"%3A%7B"north"%3A34.4728733332929%2C"east"%3A-117.63650972167969%2C"south"%3A33.566849486905525%2C"west"%3A-119.18695527832031%7D%2C"isMapVisible"%3Atrue%2C"filterState"%3A%7B"price"%3A%7B"max"%3A872627%7D%2C"beds"%3A%7B"min"%3A1%7D%2C"fore"%3A%7B"value"%3Afalse%7D%2C"mp"%3A%7B"max"%3A3000%7D%2C"auc"%3A%7B"value"%3Afalse%7D%2C"nc"%3A%7B"value"%3Afalse%7D%2C"fr"%3A%7B"value"%3Atrue%7D%2C"fsbo"%3A%7B"value"%3Afalse%7D%2C"cmsn"%3A%7B"value"%3Afalse%7D%2C"fsba"%3A%7B"value"%3Afalse%7D%7D%2C"isListVisible"%3Atrue%2C"regionSelection"%3A%5B%7B"regionId"%3A12447%2C"regionType"%3A6%7D%5D%7D'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ACQUIRE HTML WITH SELENIUM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GOING THROUGH ALL ZILLOW PAGES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
page_number = 1
while True:
    if page_number == 1:
        driver.get(Zillow_Link)
    else:
        # This will be different based on the link provided before
        driver.get(f'https://www.zillow.com/los-angeles-ca/rentals/{page_number}_p/?searchQueryState=%7B"mapBounds"%3A%7B"north"%3A34.46947686448171%2C"east"%3A-118.01485139648437%2C"south"%3A33.5634165703522%2C"west"%3A-118.80312043945312%7D%2C"regionSelection"%3A%5B%7B"regionId"%3A12447%2C"regionType"%3A6%7D%5D%2C"isMapVisible"%3Atrue%2C"filterState"%3A%7B"price"%3A%7B"max"%3A872627%7D%2C"beds"%3A%7B"min"%3A1%7D%2C"fore"%3A%7B"value"%3Afalse%7D%2C"mp"%3A%7B"max"%3A3000%7D%2C"auc"%3A%7B"value"%3Afalse%7D%2C"nc"%3A%7B"value"%3Afalse%7D%2C"fr"%3A%7B"value"%3Atrue%7D%2C"fsbo"%3A%7B"value"%3Afalse%7D%2C"cmsn"%3A%7B"value"%3Afalse%7D%2C"fsba"%3A%7B"value"%3Afalse%7D%7D%2C"isListVisible"%3Atrue%2C"pagination"%3A%7B"currentPage"%3A2%7D%7D')

    time.sleep(1)

    # To scrape, Zillow may require verification
    answer = input("Verifying done? ")

    # Acquire HTML
    page = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(''.join(page), 'html.parser')

    # Check If We Scraped All Pages
    last_page = int(driver.find_elements(By.CSS_SELECTOR, 'ul.PaginationList-c11n-8-85-1__sc-14rlw6v-0 li')[-1].text)
    if page_number > last_page:
        break

    # List of Adresses
    addresses = [address.text for address in soup.find_all('address', attrs={'data-test': "property-card-addr"})]

    # List of Prices
    unformatted_prices = [price.text for price in soup.find_all('span', attrs={'data-test': 'property-card-price'})]
    prices = []
    for price in unformatted_prices:
        new_price = price
        for i, letter in enumerate(price):
            if letter == "+" or letter == "/":
                new_price = price[:i]
                break
        prices.append(new_price)

    # List of Links
    link_elements = [link["href"] for link in soup.find_all('a', attrs={'data-test': 'property-card-link'})]
    # Links were doubled so the list had to be halved appropriately
    unformatted_prices = []
    for i, link in enumerate(link_elements):
        if i % 2 != 0:
            unformatted_prices.append(link)
    links = []
    for link in unformatted_prices:
        if link[0] == "/":
            new_link = "https://www.zillow.com/" + link
            links.append(new_link)
        else:
            links.append(link)

    # Fill Out Forms
    time.sleep(1)
    for property in range(len(addresses)):
        driver.get(GoogleForm_Link)
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"].whsOnd.zHQkBf')
        for i in range(len(inputs)):
            if i == 0:
                inputs[i].click()
                inputs[i].send_keys(addresses[property])
            elif i == 1:
                inputs[i].click()
                inputs[i].send_keys(prices[property])
            else:
                inputs[i].click()
                inputs[i].send_keys(links[property])
        submit = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
        submit.click()
        time.sleep(1)
    # Change Variables For The Next Itiration (aka Page)
    page_number += 1
    addresses = []
    links = []
    prices = []

print("Scraping Completed")