from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_edc_data(start_date, end_date):
    driver = None
    try:
        driver = setup_driver()
        url = "https://okte.sk/sk/edc/zverejnovanie-udajov/aktivovana-agregovana-flexibilita-a-zdielanie-elektriny/"
        
        # Navigate to the page
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Convert dates to required format
        start_date_str = start_date.strftime("%d.%m.%Y")
        end_date_str = end_date.strftime("%d.%m.%Y")
        
        # Find and fill date inputs
        # Note: You'll need to adjust these selectors based on the actual website structure
        try:
            start_date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='date']"))
            )
            start_date_input.clear()
            start_date_input.send_keys(start_date_str)
            
            # If there's a submit button, click it
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
        except Exception as e:
            logging.error(f"Error interacting with date inputs: {str(e)}")
            return []
        
        # Get the page source after JavaScript execution
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the table with data
        table = soup.find('table')
        if not table:
            logging.error("Table not found")
            return []
        
        data = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                try:
                    time_period = cols[0].text.strip()
                    # Handle potential empty or invalid values
                    positive_flex = float(cols[1].text.strip().replace(',', '.')) if cols[1].text.strip() else 0.0
                    negative_flex = float(cols[2].text.strip().replace(',', '.')) if cols[2].text.strip() else 0.0
                    shared_elec = float(cols[3].text.strip().replace(',', '.')) if cols[3].text.strip() else 0.0
                    
                    data.append({
                        'date': start_date,
                        'time_period': time_period,
                        'positive_flexibility': positive_flex,
                        'negative_flexibility': negative_flex,
                        'shared_electricity': shared_elec
                    })
                except (ValueError, IndexError) as e:
                    logging.error(f"Error parsing row: {str(e)}")
                    continue
        
        if not data:
            logging.error("No data found in table")
            return []
        
        logging.info(f"Successfully scraped {len(data)} rows of data")
        return data
        
    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit() 