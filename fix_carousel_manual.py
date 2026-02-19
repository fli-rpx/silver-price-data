#!/usr/bin/env python3
"""
Manually fix carousel - add Tianjin and Xi'an in new slide 6
"""

def read_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()

def write_file(filename, lines):
    with open(filename, 'w') as f:
        f.writelines(lines)

def main():
    input_file = '/Users/fudongli/clawd/travel-website/index.html'
    lines = read_file(input_file)
    
    print("📝 Manually fixing carousel...")
    
    # Find and update the title
    for i, line in enumerate(lines):
        if 'Explore 25 China Cities</h2>' in line:
            lines[i] = line.replace('25', '28')
            print(f"  ✓ Updated title at line {i+1}")
            break
    
    # Find the slide counter
    for i, line in enumerate(lines):
        if '1 / 5</div>' in line:
            lines[i] = line.replace('1 / 5', '1 / 6')
            print(f"  ✓ Updated slide counter at line {i+1}")
            break
    
    # Find where to insert new slide 6
    # We need to find the closing of slide 5 and insert before navigation
    in_slide_5 = False
    slide_5_end = -1
    
    for i, line in enumerate(lines):
        if '<!-- SLIDE -->' in line and '<!-- Taiyuan -->' in lines[i+2]:
            in_slide_5 = True
            print(f"  Found slide 5 start at line {i+1}")
        
        if in_slide_5 and '<!-- Xiamen -->' in line:
            # Find the closing divs after Xiamen
            for j in range(i, min(i+20, len(lines))):
                if '</div>' in lines[j] and '</div>' in lines[j+1] and '</div>' in lines[j+2]:
                    slide_5_end = j + 3  # After the third closing div
                    print(f"  Found slide 5 end at line {slide_5_end+1}")
                    break
            break
    
    if slide_5_end > 0:
        # Create new slide 6
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
                        <!-- Tianjin -->
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
                        </div>
                        <!-- Xi'an -->
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
                        </div>
                    </div>
                
'''
        
        # Insert new slide 6
        lines.insert(slide_5_end, new_slide_6)
        print(f"  ✓ Inserted new slide 6 after line {slide_5_end+1}")
        
        # Now we need to remove Kaifeng from slide 5
        # Find Kaifeng in slide 5
        kaifeng_start = -1
        kaifeng_end = -1
        in_kaifeng = False
        
        for i, line in enumerate(lines):
            if '<!-- Kaifeng -->' in line:
                kaifeng_start = i
                in_kaifeng = True
                print(f"  Found Kaifeng start at line {i+1}")
            
            if in_kaifeng and '</div>' in line and '</div>' in lines[i+1] and '</div>' in lines[i+2]:
                kaifeng_end = i + 3
                print(f"  Found Kaifeng end at line {kaifeng_end+1}")
                break
        
        if kaifeng_start > 0 and kaifeng_end > 0:
            # Remove Kaifeng from slide 5
            del lines[kaifeng_start:kaifeng_end]
            print(f"  ✓ Removed Kaifeng from slide 5")
    
    # Write the file
    write_file(input_file, lines)
    print("\n✅ Carousel fixed successfully!")
    
    # Verify
    print("\n🔍 Verification:")
    with open(input_file, 'r') as f:
        content = f.read()
        
        if 'Explore 28 China Cities' in content:
            print("  ✓ Title: Explore 28 China Cities")
        else:
            print("  ✗ Title not updated")
            
        if '1 / 6</div>' in content:
            print("  ✓ Slide counter: 1 / 6")
        else:
            print("  ✗ Slide counter not updated")
            
        # Count cities
        city_count = content.count('city-template.html?city=')
        print(f"  ✓ Total city links: {city_count}")
        
        # Check for our new cities
        if 'city=tianjin' in content:
            print("  ✓ Tianjin added")
        else:
            print("  ✗ Tianjin not found")
            
        if 'city=xian' in content:
            print("  ✓ Xi'an added")
        else:
            print("  ✗ Xi'an not found")

if __name__ == "__main__":
    main()