#!/usr/bin/env python3
"""
JPX Multiple CSV Downloader
--------------------------
This script automatically downloads daily CSV files from multiple JPX sources:
1. Settlement prices from derivatives markets
2. Settlement rates for Interest Rate Swap

Files are saved to separate folders with appropriate naming.
"""

import os
import datetime
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jpx_downloader.log"),
        logging.StreamHandler()
    ]
)

def get_derivatives_csv_link():
    """
    Scrape the JPX website to find the latest derivatives settlement price CSV link.
    """
    url = "https://www.jpx.co.jp/english/markets/derivatives/settlement-price/index.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csv_links = soup.find_all('a', href=lambda href: href and '.csv' in href.lower())
        
        if not csv_links:
            logging.error("No CSV links found on the derivatives settlement page.")
            return None
        
        csv_url = csv_links[0]['href']
        
        if not csv_url.startswith('http'):
            base_url = "https://www.jpx.co.jp"
            csv_url = base_url + csv_url if csv_url.startswith('/') else base_url + '/' + csv_url
            
        logging.info(f"Found derivatives CSV link: {csv_url}")
        return csv_url
        
    except Exception as e:
        logging.error(f"Error finding derivatives CSV link: {str(e)}")
        return None

def get_interest_rate_swap_csv_link():
    """
    Scrape the JPX website to find the latest Interest Rate Swap settlement rates CSV link.
    """
    url = "https://www.jpx.co.jp/jscc/en/interest_rate_swap.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links containing "Daily" and "CSV" or just CSV files
        daily_csv_links = []
        
        # First try to find links with text containing "Daily" and href containing ".csv"
        for link in soup.find_all('a'):
            link_text = link.get_text().strip()
            href = link.get('href', '')
            if ('Daily' in link_text or 'daily' in link_text.lower()) and '.csv' in href.lower():
                daily_csv_links.append(link)
        
        # If no specific links found, fall back to all CSV links
        if not daily_csv_links:
            daily_csv_links = soup.find_all('a', href=lambda href: href and '.csv' in href.lower())
        
        if not daily_csv_links:
            logging.error("No CSV links found on the Interest Rate Swap page.")
            return None
        
        # Get the first link (most likely the daily rates)
        csv_url = daily_csv_links[0]['href']
        
        if not csv_url.startswith('http'):
            base_url = "https://www.jpx.co.jp"
            csv_url = base_url + csv_url if csv_url.startswith('/') else base_url + '/' + csv_url
            
        logging.info(f"Found Interest Rate Swap CSV link: {csv_url}")
        return csv_url
        
    except Exception as e:
        logging.error(f"Error finding Interest Rate Swap CSV link: {str(e)}")
        return None

def download_derivatives_csv(csv_url, download_dir="jpx_data"):
    """
    Download the derivatives settlement price CSV file from the provided URL.
    """
    if not csv_url:
        return False
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"jpx_settlement_prices_{today}.csv"
        filepath = os.path.join(download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Downloading derivatives CSV from {csv_url}")
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"Successfully downloaded derivatives CSV to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error downloading derivatives CSV: {str(e)}")
        return False

def download_interest_rate_swap_csv(csv_url, download_dir="Settlement Rates for Interest Rate Swap(Daily)"):
    """
    Download the Interest Rate Swap settlement rates CSV file from the provided URL.
    """
    if not csv_url:
        return False
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"interest_rate_swap_settlement_rates_{today}.csv"
        filepath = os.path.join(download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Downloading Interest Rate Swap CSV from {csv_url}")
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"Successfully downloaded Interest Rate Swap CSV to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error downloading Interest Rate Swap CSV: {str(e)}")
        return False

def main():
    """
    Main function to execute the CSV download process for both sources.
    """
    logging.info("Starting JPX Multiple CSV downloader")
    
    # Download derivatives settlement prices
    derivatives_csv_url = get_derivatives_csv_link()
    if derivatives_csv_url:
        download_derivatives_csv(derivatives_csv_url)
    else:
        logging.error("Failed to get derivatives CSV link.")
    
    # Download Interest Rate Swap settlement rates
    swap_csv_url = get_interest_rate_swap_csv_link()
    if swap_csv_url:
        download_interest_rate_swap_csv(swap_csv_url)
    else:
        logging.error("Failed to get Interest Rate Swap CSV link.")

if __name__ == "__main__":
    main()
