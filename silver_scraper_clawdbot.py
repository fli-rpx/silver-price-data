#!/usr/bin/env python3
"""
Silver Price Scraper for Clawdbot
Fetches silver price and saves to CSV, with GitHub commit option.
Designed to run as a cron job or Clawdbot task.
"""

import os
import csv
import json
import re
from datetime import datetime
import subprocess
import sys

def get_silver_price():
    """
    Get silver price using Clawdbot's web_fetch tool.
    Returns price in USD/ounce or None if failed.
    """
    try:
        # This would be called via Clawdbot's web_fetch tool
        # For now, we'll simulate or use direct HTTP request
        
        # Option 1: Use requests if available
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = "https://www.kitco.com/charts/livesilver.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for price in page text
            page_text = soup.get_text()
            
            # Try multiple extraction methods
            patterns = [
                r'Bid\s*[\n\s]*\$?(\d+\.\d+)',  # Bid 85.03
                r'ounce(\d+\.\d+)',             # ounce85.03
                r'gram(\d+\.\d+)',              # gram2.73
                r'Kilo([\d,]+\.\d+)',           # Kilo2,733.82
                r'\$(\d+\.\d+)\s*USD.*oz',      # $85.03 USD/oz
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    price_str = matches[0].replace(',', '')
                    price = float(price_str)
                    
                    # Convert if needed
                    if 'gram' in pattern:
                        price = price * 28.3495  # grams to ounces
                    elif 'Kilo' in pattern:
                        price = price * 0.0311035  # kilos to ounces
                    
                    return price
            
            return None
            
        except ImportError:
            # Fallback to simple regex extraction
            print("⚠️ requests/BeautifulSoup not available, using fallback")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None

def save_price_to_csv(price, csv_path='data/silver_prices.csv'):
    """
    Save price to CSV file.
    Creates data directory if needed.
    """
    try:
        # Create data directory
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # Prepare data
        timestamp = datetime.now().isoformat()
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        data = {
            'timestamp': timestamp,
            'date': date_str,
            'price_usd': f"{price:.2f}",
            'source': 'Kitco',
            'url': 'https://www.kitco.com/charts/livesilver.html'
        }
        
        # Check if file exists
        file_exists = os.path.exists(csv_path)
        
        # Write to CSV
        with open(csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        
        print(f"✅ Saved ${price:.2f} to {csv_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return False

def commit_to_github(csv_path='data/silver_prices.csv'):
    """
    Commit CSV file to GitHub.
    Returns True if successful.
    """
    try:
        # Check if git is available and we're in a repo
        git_status = subprocess.run(['git', 'status'], 
                                   capture_output=True, text=True)
        if git_status.returncode != 0:
            print("⚠️ Not in a git repository or git not available")
            return False
        
        # Add file
        subprocess.run(['git', 'add', csv_path], check=True)
        
        # Commit
        commit_msg = f"Update silver price - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Changes committed and pushed to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with GitHub operations: {e}")
        return False

def main():
    """Main execution function."""
    print("=" * 50)
    print("SILVER PRICE SCRAPER")
    print("=" * 50)
    
    # Get current price
    print("\n🔄 Fetching current silver price...")
    price = get_silver_price()
    
    if not price:
        print("❌ Failed to fetch silver price")
        return 1
    
    print(f"💰 Current price: ${price:.2f} USD/oz")
    
    # Save to CSV
    csv_path = 'data/silver_prices.csv'
    if not save_price_to_csv(price, csv_path):
        return 1
    
    # Ask about GitHub commit
    print("\n📊 Data saved. Commit to GitHub?")
    print("Options:")
    print("1. Yes, commit and push now")
    print("2. No, just save locally")
    print("3. Auto-commit (for cron jobs)")
    
    # For cron/automated use, auto-commit
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("\n🤖 Auto-commit mode enabled")
        if commit_to_github(csv_path):
            print("✅ Automated commit successful")
        else:
            print("⚠️ Automated commit failed")
    else:
        # Interactive mode
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            if choice == '1':
                if commit_to_github(csv_path):
                    print("✅ Manual commit successful")
                else:
                    print("❌ Manual commit failed")
            elif choice == '3':
                print("🔧 Use '--auto' flag for cron jobs")
        except EOFError:
            # Non-interactive environment
            print("\n📝 Run with '--auto' flag for automated GitHub commits")
    
    print("\n" + "=" * 50)
    print("COMPLETE")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    # Check for auto-commit flag
    auto_mode = '--auto' in sys.argv
    
    if auto_mode:
        # Run in automated mode
        price = get_silver_price()
        if price and save_price_to_csv(price):
            commit_to_github()
        sys.exit(0)
    else:
        sys.exit(main())