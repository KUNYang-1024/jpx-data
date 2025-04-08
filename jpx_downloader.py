#!/usr/bin/env python3
"""
JPX Multiple CSV Downloader
--------------------------
This script automatically downloads daily CSV files from multiple JPX sources:
1. Settlement prices from derivatives markets
2. Statistics for Interest Rate Swap(Daily)
3. Settlement Rates for Interest Rate Swap(Daily)

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

def get_interest_rate_swap_links():
    """
    Scrape the JPX website to find both Interest Rate Swap CSV files:
    1. Statistics for Interest Rate Swap(Daily) - usually Excel file
    2. Settlement Rates for Interest Rate Swap(Daily) - usually PDF or CSV
    """
    url = "https://www.jpx.co.jp/jscc/en/interest_rate_swap.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find sections by their headers
        statistics_link = None
        settlement_rates_link = None
        
        # Look for headers containing the specific text
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'p'])
        
        for header in headers:
            header_text = header.get_text().strip()
            
            # Statistics for Interest Rate Swap(Daily)
            if "Statistics for Interest Rate Swap(Daily)" in header_text:
                # Look for the nearest Excel/CSV link after this header
                next_element = header
                while next_element and not statistics_link:
                    next_element = next_element.next_element
                    if next_element and hasattr(next_element, 'name') and next_element.name == 'a':
                        href = next_element.get('href', '')
                        if '.xls' in href.lower() or '.csv' in href.lower():
                            statistics_link = next_element['href']
                            break
            
            # Settlement Rates for Interest Rate Swap(Daily)
            if "Settlement Rates for Interest Rate Swap(Daily)" in header_text:
                # Look for the nearest PDF/CSV link after this header
                next_element = header
                while next_element and not settlement_rates_link:
                    next_element = next_element.next_element
                    if next_element and hasattr(next_element, 'name') and next_element.name == 'a':
                        href = next_element.get('href', '')
                        if '.pdf' in href.lower() or '.csv' in href.lower():
                            settlement_rates_link = next_element['href']
                            break
        
        # Convert to absolute URLs if needed
        base_url = "https://www.jpx.co.jp"
        
        if statistics_link and not statistics_link.startswith('http'):
            statistics_link = base_url + statistics_link if statistics_link.startswith('/') else base_url + '/' + statistics_link
        
        if settlement_rates_link and not settlement_rates_link.startswith('http'):
            settlement_rates_link = base_url + settlement_rates_link if settlement_rates_link.startswith('/') else base_url + '/' + settlement_rates_link
        
        logging.info(f"Found Statistics IRS link: {statistics_link}")
        logging.info(f"Found Settlement Rates IRS link: {settlement_rates_link}")
        
        return {
            'statistics_link': statistics_link,
            'settlement_rates_link': settlement_rates_link
        }
        
    except Exception as e:
        logging.error(f"Error finding Interest Rate Swap links: {str(e)}")
        return {
            'statistics_link': None,
            'settlement_rates_link': None
        }

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

def download_irs_statistics(file_url, download_dir="Statistics for Interest Rate Swap(Daily)"):
    """
    Download the Statistics for Interest Rate Swap(Daily) file.
    """
    if not file_url:
        return False
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        # Determine file extension from URL
        file_extension = 'csv'
        if '.xls' in file_url.lower():
            file_extension = 'xlsx' if '.xlsx' in file_url.lower() else 'xls'
        
        filename = f"irs_statistics_{today}.{file_extension}"
        filepath = os.path.join(download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Downloading IRS Statistics from {file_url}")
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"Successfully downloaded IRS Statistics to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error downloading IRS Statistics: {str(e)}")
        return False

def download_irs_settlement_rates(file_url, download_dir="Settlement Rates for Interest Rate Swap(Daily)"):
    """
    Download the Settlement Rates for Interest Rate Swap(Daily) file.
    """
    if not file_url:
        return False
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        # Determine file extension from URL
        file_extension = 'csv'
        if '.pdf' in file_url.lower():
            file_extension = 'pdf'
        
        filename = f"irs_settlement_rates_{today}.{file_extension}"
        filepath = os.path.join(download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Downloading IRS Settlement Rates from {file_url}")
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"Successfully downloaded IRS Settlement Rates to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error downloading IRS Settlement Rates: {str(e)}")
        return False

def main():
    """
    Main function to execute the file download process for all sources.
    """
    logging.info("Starting JPX Multiple File Downloader")
    
    # Download derivatives settlement prices
    derivatives_csv_url = get_derivatives_csv_link()
    if derivatives_csv_url:
        download_derivatives_csv(derivatives_csv_url)
    else:
        logging.error("Failed to get derivatives CSV link.")
    
    # Download Interest Rate Swap files
    irs_links = get_interest_rate_swap_links()
    
    # Download Statistics for Interest Rate Swap(Daily)
    if irs_links['statistics_link']:
        download_irs_statistics(irs_links['statistics_link'])
    else:
        logging.error("Failed to get Statistics for Interest Rate Swap(Daily) link.")
    
    # Download Settlement Rates for Interest Rate Swap(Daily)
    if irs_links['settlement_rates_link']:
        download_irs_settlement_rates(irs_links['settlement_rates_link'])
    else:
        logging.error("Failed to get Settlement Rates for Interest Rate Swap(Daily) link.")

if __name__ == "__main__":
    main()
