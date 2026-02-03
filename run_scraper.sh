#!/bin/bash
# Silver Price Scraper Runner
# Run with: ./run_scraper.sh [--auto]

set -e

# Use absolute path to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting silver price scraper..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check if in git repository (for auto-commit)
if [[ "$1" == "--auto" ]]; then
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
        echo "Warning: Not in a git repository, auto-commit disabled"
        AUTO_MODE=""
    else
        AUTO_MODE="--auto"
    fi
else
    AUTO_MODE=""
fi

# Run the scraper
python3 silver_scraper_clawdbot.py $AUTO_MODE

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Scraper completed successfully"
else
    echo "❌ Scraper failed"
    exit 1
fi