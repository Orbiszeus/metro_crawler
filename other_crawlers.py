import requests
import logging
import json
import time
import pandas as pd
import random
from selenium_stealth import stealth
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
import os
from Screenshot import Screenshot
import cloudscraper
from curl_cffi import requests
from typing import Union
from pydantic import BaseModel, Field
from RecaptchaSolver import RecaptchaSolver
from utils.proxy import Proxy
from tempfile import NamedTemporaryFile
from uuid import uuid4

GOOGLE_MAPS_QUERY = "https://www.google.com/maps/search/?api=1&query={}&query_place_id={}"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

cached_page_domain = "http://webcache.googleusercontent.com/search?q=cache:"


def driver_options():
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.headless = True
    prefs = {
        "download.default_directory": "/Users/orbiszeus/metro_analyst",
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)

    #path to the local chrome driver
    chromedriver_path = '/Users/orbiszeus/Downloads/chromedriver-mac-x64/chromedriver'
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def stealth_driver():
    try:
        chromedriver_path = '/Users/orbiszeus/Downloads/chromedriver-mac-x64/chromedriver'
        user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',]
        user_agent = random.choice(user_agents)

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--auto-open-devtools-for-tabs") 
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = uc.Chrome(options=chrome_options, use_subprocess=True)
        stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True
            )
        return driver
    except Exception as e:
        print(f"Exception : {e}")

def handle_cookies_and_popups(driver):
    wait = WebDriverWait(driver, 5)
    time.sleep(5)
    try:
        reject_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Reject all"]')))
        reject_button.click()
        print("Cookies rejected")
    except Exception as e:
        print("No cookies banner or unable to click it:", e)

    try:
        close_popup = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="close"] | //button[contains(text(), "Close")]')))
        close_popup.click()
        print("Pop-up closed")
    except Exception as e:
        print("No pop-up or unable to close it:", e)

def verify_links(links):
    for link in links:
        try:
            requests.head(link, timeout=3)
        except requests.RequestException as e:
            print(f"Error checking link {link}: {e}")
                   
def alternate_save_screenshot(driver):
    try:
        current_url = driver.current_url
        driver.get(current_url)
        handle_cookies_and_popups(driver)
        time.sleep(1)
        ob=Screenshot.Screenshot()
        img=ob.full_screenshot(driver,save_path=r'/Users/orbiszeus/metro_analyst',image_name="screenshot_" + str(driver.title) + ".png", load_wait_time=3)
        driver.close()
    except Exception as e:
        print(str(e))
    
def save_screenshot(driver):
    try:
        #driver.maximize_window()
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        current_url = driver.current_url
        driver.get(current_url)
        handle_cookies_and_popups(driver)
        time.sleep(1)
        original_size = driver.get_window_size()
        document_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight);")
        window_height = driver.execute_script("return window.innerHeight;")
        document_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth);")
        window_width = driver.execute_script("return window.innerWidth;")
        num_scrolls = document_height // window_height
        temp_dir = "temp_screenshots"
        os.makedirs(temp_dir, exist_ok=True)
        max_height = max(document_height, window_height)
        max_width = max(document_width, window_width)
        screenshots = []
        for i in range(num_scrolls + 1):
            driver.execute_script(f"window.scrollTo(0, {i * window_height});")
            time.sleep(1)
            screenshot_path = os.path.join(temp_dir, f"screenshot_{i}.png")
            driver.save_screenshot(screenshot_path)
            screenshots.append(screenshot_path)
            
        stitched_image = Image.new('RGB', (document_width, document_height))
        y_offset = 0
        for screenshot in screenshots:
            img = Image.open(screenshot)
            stitched_image.paste(img, (0, y_offset))
            y_offset += img.size[1]
        stitched_image.save("screenshot_" + str(driver.title) + ".png")
        
        for screenshot in screenshots:
            os.remove(screenshot)
        os.rmdir(temp_dir)
        driver.close()
        
        # width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
        # height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        # driver.set_window_size(max_width, max_height)
        # # driver.set_window_size(original_size['width'], original_size['height'])
        # full_page = driver.find_element(By.TAG_NAME, "body")
        # full_page.screenshot("screenshot_" + str(driver.title) + ".png")
        
    except Exception as e:
        print("Exception at: " + str(e))
def get_google_search_results():
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": "Kadiköy'deki en iyi restoranlar."
    })
    
    response = requests.post(url, headers={
    'X-API-KEY': '576de8f38665cad7feb185636d3d3754877a8e61','Content-Type': 'application/json'}, data=payload)
    data = response.json()
    search_results = []
    
    for result in data['organic'][:6]:
        search_results.append(result['link'])
    
    return search_results

def get_google_maps_results():
    search_results = []
    place_id_results = []
    google_maps_results = []
    
    headers = {
  'X-API-KEY': '57f3e816568aee88361f0ec8bf46a98e121ac096',
  'Content-Type': 'application/json'}
    
    url = "https://google.serper.dev/maps"

    payload = json.dumps({"q": "Kadiköy'deki en iyi restoranlar."})
    

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    
    websites = [place.get("website") for place in data["places"] if "website" in place]
    place_ids = [place.get("placeId") for place in data["places"] if "placeId" in place]
    google_maps_urls = [GOOGLE_MAPS_QUERY.format(place["title"].replace(' ', '+'), place["placeId"]) for place in data["places"] if "placeId" in place]
    for url in google_maps_urls:
        google_maps_results.append(url)
    
    for website in websites:
        search_results.append(website)
    
    for place_id in place_ids:
        place_id_results.append(place_id)
        
    return [search_results, place_id_results, google_maps_results]

def extract_restaurant_details(driver, restaurant_url):
    driver.get(restaurant_url)
    handle_cookies_and_popups(driver)
    restaurant_name = driver.title
    time.sleep(3) 
    
    if ('tripadvisor' not in str(restaurant_name)):
        elements = driver.find_elements(By.CLASS_NAME, 'CsEnBe')
        menu_links = [element for element in elements 
                  if element.get_attribute('href') and (
                  'menu' in element.get_attribute('href').lower() or 
                  'menü' in element.get_attribute('href').lower() or 
                  'yemek' in element.get_attribute('href').lower() or (
                  '.com' in element.get_attribute('href').lower() or 
                  '.com.tr' in element.get_attribute('href').lower()))]

        driver.implicitly_wait(5)
        if menu_links:
            for menu_item in menu_links:
                try:
                    print(menu_item)
                    original_window = driver.current_window_handle
                    windows_before = driver.window_handles
                    # window_before = driver.window_handles[0]
                    
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable(menu_item)))
                    WebDriverWait(driver, 20).until(EC.new_window_is_opened(windows_before))
                    new_window = [window for window in driver.window_handles if window not in windows_before][0]
                    # window_after = driver.window_handles[1]
                    time.sleep(1)
                    driver.switch_to.window(new_window)
                    current_url = driver.current_url
                    find_menu_links(driver, current_url)
                    #current_url = driver.execute_script("return document.URL;")
                    time.sleep(2)
                    #save_screenshot(driver)
                    #alternate_save_screenshot(driver)
                    print(f"Current URL: {current_url}")
                    
                    if current_url.endswith('.pdf'):
                        # driver.back()
                        time.sleep(2)
                        download_and_parse_pdf(current_url, driver.title)
                        
                    else:
                        # driver.back()
                        time.sleep(2)
                        # extract_html_content_as_json(driver, driver.title)
                    driver.close()
                    driver.switch_to.window(original_window)
                    
                except Exception as e:
                    print(f"Error navigating to menu: {e}") 
        else: 
             elements = driver.find_elements(By.CLASS_NAME, 'CsEnBe')
             
             

    elif ('tripadvisor' in str(restaurant_name)):

        print(driver.title)
        wait = WebDriverWait(driver, 20)

        try:
            accept_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Accept All"]')))
            accept_cookies.click()
        except Exception as e:
            print("No cookies banner or unable to click it:", e)

        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except Exception as e:
            print("Main content did not load:", e)
  
        links = driver.find_elements(By.XPATH, '//a[contains(@href, ".html")]')
            
        if links:
            for link in links:
                try:
                    print(link)
                    link.click()
                    print("clicked a link..")
                    time.sleep(3)  
                    print(f"Current URL: {current_url}")
                    menu_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="menu"], a[href*="menü"]')
                    for menu_link in menu_links:
                        menu_link.click()
                        time.sleep(5)
                        current_url = driver.current_url
                        if menu_link[0].endswith('.pdf'):
                            download_and_parse_pdf(current_url, driver.title)
                        else:
                            extract_html_content_as_json(driver, driver.title)
                        break
                except Exception as e:
                    print(f"Error navigating to menu: {e}") 


def download_and_parse_pdf(pdf_url, restaurant_name):
    response = requests.get(pdf_url)
    pdf_path = '/Users/orbiszeus/metro_analyst/restaurant_menus/' + str(restaurant_name) + '_menu.pdf' 
    with open(pdf_path, 'wb') as file:
        file.write(response.content)
    print("PDF downloaded successfully.")
    
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    
    print("PDF Content:")
    print(text)



def extract_html_content_as_json(driver, restaurant_name, wait_time=10):
    # Wait for the page to load completely
    WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    page_source = driver.page_source
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Remove header, script, and style elements
    for tag in soup.find_all(['header', 'script', 'style']):
        tag.decompose()
    
    # Convert the cleaned HTML to string
    cleaned_html = str(soup)

    html_content = {'html': cleaned_html}
    html_json = json.dumps(html_content, indent=4)
    
    json_path = f"{restaurant_name}_menu.html.json"
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json_file.write(html_json)
    
    print(f"HTML content saved to {json_path}")


def download_site_content(driver, url, title):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load completely
    page_content = driver.page_source
    file_name = title.replace(" ", "_") + "_menu.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(page_content)
    print(f"Downloaded content from {url} and saved as {file_name}")
        
        
def find_menu_links(driver, url, visited_links=set()):
    driver.get(url)
    handle_cookies_and_popups(driver)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all anchor tags
    links = soup.find_all('a', href=True)
    
    # Define keywords to identify potential menu links
    menu_keywords = [
                "menu", "menü", "breakfast", "kahvaltı", "lunch", "öğle yemeği", 
                "dinner", "akşam yemeği", "drinks", "içecekler", ".pdsf"
                    ]
    for link in links:
        link_text = link.get_text().lower()
        href = link['href']
        if any(keyword in link_text for keyword in menu_keywords) or any(keyword in href for keyword in menu_keywords):
            if href not in visited_links:
                visited_links.add(href)
                full_url = href if href.startswith('http') else driver.current_url + href
                if href.endswith(".pdf"):
                    time.sleep(2)
                    print("PDF Menu found:", full_url)
                    print(download_and_parse_pdf(full_url, driver.title))
                elif href.endswith(".html"):
                    time.sleep(2)
                    extract_html_content_as_json(driver, driver.title)
                else:
                    
                    if any(keyword in href for keyword in menu_keywords):
                        download_site_content(driver, full_url, driver.title)
                    find_menu_links(driver, full_url, visited_links)

def cloudflare_api_bypassers():
    response = requests.get(
    url='https://proxy.scrapeops.io/v1/',
    params={
        'api_key': '4a812244-0e8a-4cb7-a441-847ac56ff995',
        'url': 'https://www.yemeksepeti.com/city/istanbul/area/besiktas-sinanpasa-mah', 
    },
    )

    print('Response Body: ', response.content)


def cloud_scraper(restaurant_url):
    scraper = cloudscraper.create_scraper() 
    print(scraper.get(restaurant_url).text)
    
    
'''
This is for the firewall pop-up
'''
def find_checkbox_element(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, '#content input[type="checkbox"]')
    for element in elements:
        if element.is_displayed():
            return element
    return None

def y_crawler(driver, restaurant_url):
    driver.get(restaurant_url)
    script = f'''window.open("{restaurant_url}", "_blank");'''
    driver.execute_script(script)
    time.sleep(15)
    driver.switch_to.window(driver.window_handles[1])
    # handle_cookies_and_popups(driver)
    # try:
    #     checkbox = find_checkbox_element(driver)
    #     if checkbox:
    #         actions = ActionChains(driver)
    #         actions.move_to_element(checkbox).perform()
    #         time.sleep(1)
    #         actions.click(checkbox).perform()
    #         time.sleep(2)
    #     else:
    #         print("Checkbox element not found.")
    # except Exception as checkbox_ex:
    #     print(f"Exception while clicking checkbox: {checkbox_ex}")
    time.sleep(2)
    restaurant_name = driver.title
    time.sleep(3) 
    buttons_to_rest_links = driver.find_elements(By.CLASS_NAME, 'bds-c-grid-item vendor')
    results = []
    
    try:
        for button in buttons_to_rest_links:
            a_elements = button.find_elements(By.TAG_NAME, 'a')
            for actual_link in a_elements:
                href = actual_link.get_attribute('href')
                if href:
                    print(href)
                    original_window = driver.current_window_handle
                    windows_before = driver.window_handles
                    driver.execute_script("arguments[0].click();", actual_link)
                    WebDriverWait(driver, 20).until(EC.new_window_is_opened(windows_before))
                    new_window = [window for window in driver.window_handles if window not in windows_before][0]
                    driver.switch_to.window(new_window)
                    current_url = driver.current_url
                    # actual_link.click()
                    time.sleep(2)
                    modal = driver.find_element(By.CLASS_NAME, 'bds-c-modal__content-window')
                    if modal.is_displayed():
                        close_button = modal.find_element(By.CSS_SELECTOR, '[aria-label="Close"]')
                        close_button.click()
                        print("Restaurant is closed, no menu details.")
                        time.sleep(2) 
                        break
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    divs = soup.find_all('div', class_='box-flex grow respect-flex-parent-width jc-space-between')
                    for div in divs:
                        menu_item = div.find('span', {'data-testid': 'menu-product-name'}).text.strip()
                        ingredients = div.find('p', {'data-testid': 'menu-product-description'}).text.strip()
                        price = div.find('p', {'data-testid': 'menu-product-price'}).text.strip()
                        item_dict = {
                            'Menu Item': menu_item,
                            'Ingredients': ingredients,
                            'Price': price
                        }
                        results.append(item_dict)                    
                
    except Exception as e:
        print(f"Error: {e}")
        
    json_output = json.dumps(results)    
    print(json_output)

    return 0 