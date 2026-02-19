#!/usr/bin/env python3
"""
Fix carousel cities - add Tianjin and Xi'an, create new slide 6
"""

import re

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def create_tianjin_card():
    """Create HTML for Tianjin city card."""
    return '''                        <!-- Tianjin -->
                        <div class="city-card" onclick="window.location.href='cities/city-template.html?city=tianjin'" style="cursor: pointer;">
                            <div class="city-header" style="background-image: url('images/user_photos/beijing_hero_bg.jpg?v=1771184412');">
                                <div class="city-name">Tianjin</div>
                                <div class="city-tag">Port City & Architecture</div>
                            </div>
                            <div class="city-details">
                                <p>🏛️ Five Great Avenues - European architecture</p>
                                <p>🎡 Tianjin Eye - Ferris wheel on bridge</p>
                                <p>🥟 Goubuli buns - famous local specialty</p>
                                
                            </div>
                        </div>'''

def create_xian_card():
    """Create HTML for Xi'an city card."""
    return '''                        <!-- Xi'an -->
                        <div class="city-card" onclick="window.location.href='cities/city-template.html?city=xian'" style="cursor: pointer;">
                            <div class="city-header" style="background-image: url('images/user_photos/beijing_hero_bg.jpg?v=1771184412');">
                                <div class="city-name">Xi'an</div>
                                <div class="city-tag">Ancient Capital & History</div>
                            </div>
                            <div class="city-details">
                                <p>🗿 Terracotta Army - 8,000+ soldiers</p>
                                <p>🏯 Ancient City Wall - 14km circumference</p>
                                <p>🍜 Roujiamo - Chinese hamburger</p>
                                
                            </div>
                        </div>'''

def fix_carousel(content):
    """Fix the carousel by adding Tianjin and Xi'an in new slide 6."""
    
    # 1. Update title from 25 to 28 China Cities
    content = content.replace(
        '<h2 class="section-title">Explore 25 China Cities</h2>',
        '<h2 class="section-title">Explore 28 China Cities</h2>'
    )
    
    # 2. Find slide 5 and remove Kaifeng from it
    # Slide 5 starts with: "<!-- SLIDE -->" then "<div class="carousel-slide">"
    # We need to find the Kaifeng card and remove it from slide 5
    
    # First, let's find the position of the Kaifeng card in slide 5
    kaifeng_pattern = r'(<!-- Kaifeng -->\s*<div class="city-card" onclick="window\.location\.href=\'cities/city-template\.html\?city=kaifeng\'.*?</div>\s*</div>\s*</div>\s*)'
    
    # Remove Kaifeng from slide 5
    content = re.sub(kaifeng_pattern, '', content, flags=re.DOTALL)
    
    # 3. Find where to insert new slide 6 (after slide 5, before navigation)
    # Look for the closing div of slide 5 and the navigation section
    slide_5_end_pattern = r'(</div>\s*</div>\s*</div>\s*</div>\s*\s*<!-- Navigation -->)'
    
    # Create new slide 6 with Kaifeng, Tianjin, and Xi'an
    new_slide_6 = '''                    <!-- SLIDE -->
                    <div class="carousel-slide">
                        <!-- Kaifeng -->
                        <div class="city-card" onclick="window.location.href='cities/city-template.html?city=kaifeng'" style="cursor: pointer;">
                            <div class="city-header" style="background-image: url('images/user_photos/kaifeng_hero_bg.jpg?v=1771184412');">
                                <div class="city-name">Kaifeng</div>
                                <div class="city-tag">Ancient Capital & Culture</div>
                            </div>
                            <div class="city-details">
                                <p>🏮 Ancient capital of seven dynasties</p>
                                <p>🕍 Daxiangguo Temple - Buddhist heritage</p>
                                <p>🏰 Iron Pagoda - 900+ years old</p>
                                
                            </div>
                        </div>
''' + create_tianjin_card() + '\n' + create_xian_card() + '''
                    </div>
                
                <!-- Navigation -->'''
    
    # Replace the pattern with new slide 6
    content = re.sub(slide_5_end_pattern, new_slide_6, content, flags=re.DOTALL)
    
    # 4. Update slide counter from "1 / 5" to "1 / 6"
    content = content.replace('1 / 5</div>', '1 / 6</div>')
    
    return content

def main():
    input_file = '/Users/fudongli/clawd/travel-website/index.html'
    output_file = '/Users/fudongli/clawd/travel-website/index.html'
    
    print("📝 Fixing carousel cities...")
    print("  - Adding Tianjin and Xi'an")
    print("  - Creating new slide 6 with Kaifeng, Tianjin, Xi'an")
    print("  - Updating title to '28 China Cities'")
    print("  - Updating slide counter to '1 / 6'")
    
    # Read the file
    content = read_file(input_file)
    
    # Fix the carousel
    fixed_content = fix_carousel(content)
    
    # Write the file
    write_file(output_file, fixed_content)
    
    print("✅ Carousel fixed successfully!")
    
    # Verify the changes
    print("\n🔍 Verifying changes:")
    
    # Check title
    if 'Explore 28 China Cities' in fixed_content:
        print("  ✓ Title updated to '28 China Cities'")
    else:
        print("  ✗ Title not updated")
    
    # Check slide counter
    if '1 / 6</div>' in fixed_content:
        print("  ✓ Slide counter updated to '1 / 6'")
    else:
        print("  ✗ Slide counter not updated")
    
    # Check for Tianjin
    if "city=kaifeng" in fixed_content and "city=tianjin" in fixed_content and "city=xian" in fixed_content:
        print("  ✓ All three cities (Kaifeng, Tianjin, Xi'an) added")
    else:
        print("  ✗ Not all cities were added")
    
    print("\n📊 Final carousel should have:")
    print("  - Slide 1-4: 5 cities each")
    print("  - Slide 5: 5 cities (Taiyuan, Urumqi, Wuhan, Wuxi, Xiamen)")
    print("  - Slide 6: 3 cities (Kaifeng, Tianjin, Xi'an)")
    print("  - Total: 28 cities")

if __name__ == "__main__":
    main()