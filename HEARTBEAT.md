# HEARTBEAT.md

## Silver Price Check - WEEKDAYS ONLY
# Check silver price Monday-Friday, skip Saturday-Sunday
# Today is Wednesday 2026-02-19 - should check
# Last checked: 2026-02-19 04:24:28 (price: $77.555)

# Run weekday silver check (once per day is sufficient)
cd /Users/fudongli/clawd && python3 silver_check_weekdays.py

# If it's a weekday and check succeeded, send to Telegram
# The script handles Telegram sending internally

## Travel Development Ideas Checker - EVERY 30 MINUTES
# Check travel_development_ideas table for pending tasks
# Complete any image optimization tasks
# Check in changes to GitHub automatically
cd /Users/fudongli/clawd && python3 travel_development_checker.py