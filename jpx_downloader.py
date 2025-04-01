#!/usr/bin/env python3
import os
import datetime
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_csv_link():
    """Scrape the JPX website to find the latest CSV download link."""
    url = "https://www.jpx.co.jp/english/markets/derivatives/settlement-price/index.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csv_links = soup.find_all('a', href=lambda href: href and '.csv' in href.lower())
        
        if not csv_links:
            logging.error("No CSV links found on the page.")
            return None
        
        csv_url = csv_links[0]['href']
        
        if not csv_url.startswith('http'):
            base_url = "https://www.jpx.co.jp"
            csv_url = base_url + csv_url if csv_url.startswith('/') else base_url + '/' + csv_url
            
        return csv_url
        
    except Exception as e:
        logging.error(f"Error finding CSV link: {str(e)}")
        return None

def download_csv(csv_url, download_dir="jpx_data"):
    """Download the CSV file from the provided URL."""
    if not csv_url:
        return False
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"jpx_settlement_prices_{today}.csv"
        filepath = os.path.join(download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        logging.info(f"Downloading from {csv_url}")
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"Successfully downloaded to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error downloading CSV: {str(e)}")
        return False

def main():
    """Main function to execute the CSV download process."""
    logging.info("Starting JPX CSV downloader")
    
    csv_url = get_latest_csv_link()
    if csv_url:
        download_csv(csv_url)
    else:
        logging.error("Failed to get CSV link.")

if __name__ == "__main__":
    main()
