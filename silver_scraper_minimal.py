#!/usr/bin/env python3
"""
Minimal Silver Price Scraper
Uses curl and grep to extract price, no external dependencies.
"""

import os
import csv
import re
import subprocess
from datetime import datetime
import sys

def get_silver_price_curl():
    """Get silver price using curl and grep."""
    try:
        url = "https://www.kitco.com/charts/livesilver.html"
        
        # Use curl to fetch the page
        cmd = ['curl', '-s', '-L', '-H', 'User-Agent: Mozilla/5.0', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Curl failed: {result.stderr}")
            return None
        
        html = result.stdout
        
        # Try multiple extraction patterns
        patterns = [
            r'Bid\s*[\n\s]*\$?(\d+\.\d+)',      # Bid 85.03
            r'ounce(\d+\.\d+)',                 # ounce85.03
            r'gram(\d+\.\d+)',                  # gram2.73
            r'Kilo([\d,]+\.\d+)',               # Kilo2,733.82
            r'\$(\d+\.\d+)\s*USD.*oz',          # $85.03 USD/oz
            r'(\d+\.\d+)\s*USD.*ounce',         # 85.03 USD/ounce
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                price_str = matches[0].replace(',', '')
                price = float(price_str)
                
                # Convert if needed
                if 'gram' in pattern:
                    price = price * 28.3495  # grams to ounces
                elif 'Kilo' in pattern:
                    price = price * 0.0311035  # kilos to ounces
                
                return price
        
        # Fallback: look for any number that looks like a silver price
        all_numbers = re.findall(r'\b(\d+\.\d+)\b', html)
        for num in all_numbers:
            price = float(num)
            if 50 < price < 150:  # Reasonable silver price range
                return price
        
        return None
        
    except subprocess.TimeoutExpired:
        print("❌ Request timeout")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_to_csv(price, primary_filename='/Users/fudongli/data/silver_prices.csv', repo_filename='data/silver_prices.csv'):
    """Save price to CSV file in both locations."""
    try:
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
        
        # Save to primary location
        os.makedirs(os.path.dirname(primary_filename), exist_ok=True)
        primary_exists = os.path.exists(primary_filename)
        
        with open(primary_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not primary_exists:
                writer.writeheader()
            writer.writerow(data)
        
        print(f"✅ Saved ${price:.2f} to {primary_filename}")
        
        # Also save to repository location
        os.makedirs(os.path.dirname(repo_filename), exist_ok=True)
        repo_exists = os.path.exists(repo_filename)
        
        with open(repo_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not repo_exists:
                writer.writeheader()
            writer.writerow(data)
        
        print(f"✅ Also saved to repository: {repo_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return False

def git_commit_and_push(repo_filename='data/silver_prices.csv'):
    """Commit and push repository file to GitHub."""
    try:
        # Check if we're in a git repo
        if subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                         capture_output=True).returncode != 0:
            return False
        
        # Add the repository file
        subprocess.run(['git', 'add', repo_filename], check=True)
        
        # Commit
        date = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f"Update silver price - {date}"
        subprocess.run(['git', 'commit', '-m', msg], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Committed and pushed to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git error: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

def main():
    """Main function."""
    print("🔄 Fetching silver price...")
    
    # Get price
    price = get_silver_price_curl()
    
    if not price:
        print("❌ Could not fetch price")
        return 1
    
    print(f"💰 Silver price: ${price:.2f} USD/oz")
    
    # Save to CSV in both locations
    primary_file = '/Users/fudongli/data/silver_prices.csv'
    repo_file = 'data/silver_prices.csv'
    if not save_to_csv(price, primary_file, repo_file):
        return 1
    
    # Auto-commit if requested
    if '--auto' in sys.argv:
        git_commit_and_push(repo_file)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())