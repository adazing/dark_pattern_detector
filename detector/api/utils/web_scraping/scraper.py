import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import requests
import csv

img_reader_api_key = 'insert api key here'
img_reader_api_url = 'https://api.ocr.space/parse/image'


random.seed(0)

# Define selectors
popup_selectors = [
    ".modal",
    ".popup",
    ".overlay",
    "[role='dialog']",
    ".newsletter-popup",
    "#popup",
]

element_selectors = {
    'buttons': ['button', "a.button", "a.btn"],
    'paragraphs': ['p', 'span'],
    'headings': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    'labels': ['label', 'span.label']
}

# Initialize WebDriver
driver = webdriver.Firefox()
# driver = webdriver.Chrome(executable_path='path_to_chromedriver')
wait = WebDriverWait(driver, 10)  # Adjust wait time as needed

# Load URLs
# urls = pd.read_csv('sites.csv')['url'].tolist()
urls = pd.read_csv('ranked_sites.csv')
# urls = urls['url'].tolist()
urls = urls.loc[(urls["dp"]==True) & (urls["deceptive"]==True)]['url'].tolist()


# Functions
def find_popups():
    popups = []
    for selector in popup_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        popups.extend(elements)
    return popups

def extract_text_from_elements(scope):
    extracted_text = []
    for element_type, selector_list in element_selectors.items():
        texts = []
        for selector in selector_list:
            elements = scope.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    text = element.text.strip()
                    if len(text.split())>1:
                        texts.append(text)
                except:
                    continue
        extracted_text.extend(texts)
    return extracted_text

def scrape_images(scope):
    try:
        extracted_text = []
        for elem in scope.find_elements(By.XPATH, "//img[@src]"):
            img_url = elem.get_attribute("src")
            payload = {
                'url': img_url,
                'isOverlayRequired': False,
                'apikey': img_reader_api_key,
                'language': 'eng',  # Specify the language
            }
            try:
                response = requests.post(img_reader_api_url, data=payload, timeout =30)
                result = response.json()
                if result['IsErroredOnProcessing'] == False:
                    text_detected = result['ParsedResults'][0]['ParsedText'].strip()
                    if len(text_detected.split())>1:
                        extracted_text.append(text_detected)
            except:
                pass
                # print('Detected Text:')
                # print(text_detected)
            # else:
                # print('Error:', result['ErrorMessage'])
    except:
        pass
    return extracted_text

def scrape_site(url):
    site_data = []
    if not url.startswith("http"):
        url = 'https://' + url
    driver.get(url)
    main_url = driver.current_url
    time.sleep(3)  # Allow time for the initial page to load
    all_links = []
    for page_num in range(1, 16):  # Navigate through 15 pages
        print(f"Scraping {driver.current_url} - Page {page_num}")
        # page_info = {'url': url, 'page_number': page_num}
        
        # Extract texts from the current page
        page_texts = extract_text_from_elements(driver)
        site_data.extend(page_texts)
        
        # img_texts = scrape_images(driver)
        # site_data.extend(img_texts)
        # page_info.update(page_texts)
        
        # Look for popups
        # popups = find_popups()
        # popup_texts = []
        # for popup in popups:
        #     popup_data = extract_text_from_elements(popup)
        #     popup_texts.extend(popup_data)
        
        # site_data.extend(popup_texts)
        
        # Attempt to navigate to next page
        
        try:
            links = []
            for elem in driver.find_elements(By.XPATH, "//a[@href]"):
                href = elem.get_attribute("href")
                # print(href)
                # print(url)
                if main_url in href and href not in links:
                    # print("yay")
                    links.append(href)
            # links = [elem.get_attribute("href") if url in elem.get_attribute("href") for elem in driver.find_elements(By.XPATH, "//a[@href]")]
            all_links.extend(links)
        except NoSuchElementException:
            print(f"No links on page {page_num}. Going to choose random link found from previous pages on site.")

        if all_links:
            # random.shuffle(all_links)
            new_link = all_links.pop(random.randint(0, len(all_links)-1))
            # print(new_link)
            driver.get(new_link)
            time.sleep(2)  # Wait for next page to load
        else:# no next page, exit loop
            break
    return site_data

# header
with open("new_data.csv", 'w+', newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Text"])

# Main scraping loop
for url in urls:
    try:
        site_data = scrape_site(url)
        print(site_data)
        with open("new_data.csv", 'a', newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL) # quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL
            for t in site_data: 
                writer.writerow([t])
            
        # all_site_data.extend(site_data)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        continue

# Save data to CSV

# df = pd.DataFrame(all_site_data, columns = ["text"])
# df.to_csv('scraped_ecommerce_data.csv', index=False)

# Close the driver
driver.quit()
