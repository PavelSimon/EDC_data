import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import current_app

def scrape_edc_data(start_date, end_date):
    """
    Scrape EDC data from OKTE.sk for a given date range.
    Returns a list of dictionaries containing the scraped data.
    """
    all_data = []
    current_date = start_date
    base_url = "https://okte.sk/sk/edc/zverejnovanie-udajov/aktivovana-agregovana-flexibilita-a-zdielanie-elektriny/"
    
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    while current_date <= end_date:
        try:
            # Format date for the form (DD.MM.YYYY format as required by the website)
            date_str = current_date.strftime('%d.%m.%Y')
            current_app.logger.info(f"Attempting to scrape data for date: {date_str}")
            
            # First, get the initial page to get any necessary cookies/tokens
            response = session.get(base_url, headers=headers)
            response.raise_for_status()
            
            # Prepare the form data for the date selection
            form_data = {
                'date': date_str,
                'submit': 'Zobraziť'  # The submit button value
            }
            
            print(f"form_data: {form_data}")
            current_app.logger.info(f"Submitting form with data: {form_data}")
            
            # Submit the form with the date
            response = session.post(base_url, data=form_data, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the data table
            table = soup.find('table')
            if not table:
                current_app.logger.warning(f"No data table found for date {date_str}")
                current_date += timedelta(days=1)
                continue
            
            # Extract data from table rows
            rows = table.find_all('tr')[1:]  # Skip header row
            day_data = []
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    try:
                        time_period = cols[0].text.strip()
                        positive_flexibility = float(cols[1].text.strip().replace(',', '.'))
                        negative_flexibility = float(cols[2].text.strip().replace(',', '.'))
                        shared_electricity = float(cols[3].text.strip().replace(',', '.'))
                        
                        day_data.append({
                            'date': current_date,
                            'time_period': time_period,
                            'positive_flexibility': positive_flexibility,
                            'negative_flexibility': negative_flexibility,
                            'shared_electricity': shared_electricity
                        })
                    except (ValueError, IndexError) as e:
                        current_app.logger.error(f"Error parsing row for date {date_str}: {str(e)}")
                        continue
            
            if day_data:
                all_data.extend(day_data)
                current_app.logger.info(f"Successfully scraped {len(day_data)} records for {date_str}")
            else:
                current_app.logger.warning(f"No valid data found for date {date_str}")
            
        except requests.RequestException as e:
            current_app.logger.error(f"Request error for date {date_str}: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Error scraping data for date {date_str}: {str(e)}")
        
        # Move to next day
        current_date += timedelta(days=1)
    
    if not all_data:
        current_app.logger.warning("No data was collected for the entire date range")
    else:
        current_app.logger.info(f"Total records collected: {len(all_data)}")
    
    return all_data 