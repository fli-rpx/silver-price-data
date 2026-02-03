#!/bin/bash
# Setup script for Silver Price Scraper

set -e

echo "🔧 Setting up Silver Price Scraper"
echo "=================================="

# Make scripts executable
chmod +x silver_scraper_minimal.py
chmod +x run_scraper.sh

# Create data directory
mkdir -p data

# Test the scraper
echo -e "\n🧪 Testing scraper..."
if python3 silver_scraper_minimal.py; then
    echo "✅ Scraper test successful"
else
    echo "❌ Scraper test failed"
    exit 1
fi

# Show created file
echo -e "\n📁 Created files:"
ls -la data/

echo -e "\n📊 Sample data:"
head -5 data/silver_prices.csv

# Instructions
echo -e "\n📋 USAGE INSTRUCTIONS:"
echo "======================"
echo ""
echo "1. DAILY MANUAL RUN:"
echo "   ./run_scraper.sh"
echo ""
echo "2. AUTOMATED RUN (for cron):"
echo "   ./run_scraper.sh --auto"
echo ""
echo "3. CRON JOB EXAMPLE (runs daily at 2 PM):"
echo "   0 14 * * * cd $(pwd) && ./run_scraper.sh --auto"
echo ""
echo "4. MANUAL PYTHON RUN:"
echo "   python3 silver_scraper_minimal.py"
echo "   python3 silver_scraper_minimal.py --auto  # with git commit"
echo ""
echo "5. GIT COMMIT MANUALLY:"
echo "   git add data/silver_prices.csv"
echo "   git commit -m 'Update silver price'"
echo "   git push"
echo ""
echo "✅ Setup complete!"