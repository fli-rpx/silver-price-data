# Silver Price Scraper

A Python script to scrape daily silver prices from Kitco and save to CSV with optional GitHub commits.

## Files

- `silver_scraper_clawdbot.py` - Main scraper script with GitHub integration
- `scrape_silver_simple.py` - Simpler version for testing
- `scrape_silver.py` - Original version with BeautifulSoup
- `requirements.txt` - Python dependencies

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make scripts executable:
```bash
chmod +x silver_scraper_clawdbot.py
```

## Usage

### Interactive Mode
```bash
python3 silver_scraper_clawdbot.py
```

### Automated Mode (for cron jobs)
```bash
python3 silver_scraper_clawdbot.py --auto
```

### Manual Run with Git Commit
```bash
# Fetch price and save to CSV
python3 silver_scraper_clawdbot.py

# Then commit manually
git add data/silver_prices.csv
git commit -m "Update silver price"
git push
```

## Output

Data is saved to `data/silver_prices.csv` with columns:
- `timestamp`: ISO format timestamp
- `date`: Date only (YYYY-MM-DD)
- `price_usd`: Price in USD per ounce
- `source`: Data source (Kitco)
- `url`: Source URL

## Cron Job Example

Add to crontab for daily 2 PM execution:
```bash
0 14 * * * cd /path/to/this/directory && python3 silver_scraper_clawdbot.py --auto
```

## Integration with Clawdbot

This can be integrated with Clawdbot's cron system:
1. Create a cron job in Clawdbot
2. Set it to run the script daily
3. Script will automatically commit to GitHub

## GitHub Setup

Ensure:
1. Git is configured with your credentials
2. Repository is initialized
3. Remote origin is set
4. You have push permissions