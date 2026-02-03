#!/usr/bin/env python3
"""
Simple Silver Price Scraper
Uses web_fetch output format to extract silver price.
"""

import json
import csv
import os
from datetime import datetime
import re
import sys

def extract_price_from_web_fetch_output(content):
    """
    Extract silver price from web_fetch output.
    The content should be markdown/text from Kitco silver page.
    """
    try:
        # Look for price patterns in the text
        # Kitco format: Bid\n\n### 85.03\n+5.91 (+7.47%)
        
        # Method 1: Look for Bid followed by price
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Bid' in line and i + 2 < len(lines):
                # Next lines might contain the price
                for j in range(1, 4):
                    if i + j < len(lines):
                        price_line = lines[i + j].strip()
                        # Look for number with decimal
                        match = re.search(r'(\d+\.\d+)', price_line)
                        if match:
                            return float(match.group(1))
        
        # Method 2: Look for any dollar amount in reasonable range
        all_matches = re.findall(r'\$?(\d+\.\d+)', content)
        for match in all_matches:
            price = float(match)
            if 10 < price < 200:  # Reasonable silver price range
                return price
        
        # Method 3: Look for specific patterns
        patterns = [
            r'ounce(\d+\.\d+)',  # ounce85.03
            r'gram(\d+\.\d+)',   # gram2.73
            r'Kilo([\d,]+\.\d+)' # Kilo2,733.82
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                price_str = matches[0].replace(',', '')
                price = float(price_str)
                if pattern == r'gram(\d+\.\d+)':
                    # Convert gram to ounce (1 oz = 28.3495 g)
                    price = price * 28.3495
                elif pattern == r'Kilo([\d,]+\.\d+)':
                    # Convert kilo to ounce (1 oz = 0.0311035 kg)
                    price = price * 0.0311035
                return price
        
        return None
        
    except Exception as e:
        print(f"Error extracting price: {e}")
        return None

def save_to_csv(price, filename='data/silver_prices.csv'):
    """Save price data to CSV file."""
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    price_data = {
        'timestamp': timestamp,
        'date': date_str,
        'price_usd': price,
        'source': 'Kitco',
        'url': 'https://www.kitco.com/charts/livesilver.html'
    }
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'date', 'price_usd', 'source', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write price data
            writer.writerow(price_data)
            
        print(f"✅ Price ${price:.2f} saved to {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return False

def load_web_fetch_output():
    """
    Load web_fetch output from file or simulate it.
    In production, this would be replaced with actual web_fetch call.
    """
    # For testing, you can save web_fetch output to a file
    test_file = 'kitco_silver_sample.txt'
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            return f.read()
    
    # Sample data structure similar to web_fetch output
    sample_data = """## Live Charts

## /

Bid

### 85.03
+5.91 (+7.47%)

Ask
85.28

- ounce85.03+5.91
- gram2.73+0.19
- Kilo2,733.82+190.11
- pennyweight4.25+0.30
- tola31.89+2.22
- tael103.34+7.19

79.17
89.20

Day's Range"""
    
    return sample_data

def main():
    """Main function."""
    print("🔄 Starting silver price extraction...")
    
    # Get web_fetch content (in real use, call web_fetch tool)
    content = load_web_fetch_output()
    
    # Extract price
    price = extract_price_from_web_fetch_output(content)
    
    if price:
        print(f"💰 Silver price extracted: ${price:.2f} USD/oz")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Save to CSV
        if save_to_csv(price):
            print("✅ Data saved successfully")
            
            # Note: GitHub commit would be handled separately
            # or integrated with existing cron/Clawdbot system
            print("\n📝 To commit to GitHub, run:")
            print("git add data/silver_prices.csv")
            print(f'git commit -m "Update silver price: ${price:.2f}"')
            print("git push")
            
            return 0
        else:
            print("❌ Failed to save data")
            return 1
    else:
        print("❌ Could not extract silver price from content")
        return 1

if __name__ == "__main__":
    sys.exit(main())