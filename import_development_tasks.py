#!/usr/bin/env python3
"""
Import development tasks from SQL files into the database
"""

import os
import subprocess
import re

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def extract_ideas_from_sql(filepath):
    """Extract development ideas from SQL file."""
    ideas = []
    
    if not os.path.exists(filepath):
        return ideas
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all INSERT statements
    insert_pattern = r"INSERT INTO.*VALUES\s*\(('[^']+')\)"
    matches = re.findall(insert_pattern, content, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        # Remove quotes and clean up
        idea = match.strip("'")
        ideas.append(idea)
    
    return ideas

def check_if_idea_exists(idea):
    """Check if an idea already exists in the database."""
    # Escape single quotes for SQL
    escaped_idea = idea.replace("'", "''")
    
    cmd = f"""
    psql -d travel_website -U fudongli -h localhost -c "
    SELECT COUNT(*) 
    FROM travel.travel_development_ideas 
    WHERE idea = '{escaped_idea}';" -t -A
    """
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0 and stdout.strip().isdigit():
        return int(stdout.strip()) > 0
    return False

def import_idea_to_database(idea):
    """Import a single idea into the database."""
    # Escape single quotes for SQL
    escaped_idea = idea.replace("'", "''")
    
    cmd = f"""
    psql -d travel_website -U fudongli -h localhost -c "
    INSERT INTO travel.travel_development_ideas (idea) 
    VALUES ('{escaped_idea}');"
    """
    
    returncode, stdout, stderr = run_command(cmd)
    return returncode == 0

def main():
    print("📥 IMPORTING DEVELOPMENT TASKS FROM SQL FILES")
    print("=" * 50)
    
    # SQL files to check
    sql_files = [
        "/Users/fudongli/clawd/travel-website/insert_layout_tasks.sql",
        "/Users/fudongli/clawd/travel-website/insert_new_ideas.sql",
        "/Users/fudongli/clawd/travel-website/insert_more_new_ideas.sql",
        "/Users/fudongli/clawd/travel-website/insert_beijing_layout_ideas.sql"
    ]
    
    total_imported = 0
    total_skipped = 0
    
    for sql_file in sql_files:
        if not os.path.exists(sql_file):
            print(f"❌ File not found: {sql_file}")
            continue
        
        print(f"\n📋 Processing: {os.path.basename(sql_file)}")
        ideas = extract_ideas_from_sql(sql_file)
        
        if not ideas:
            print("   No ideas found in file")
            continue
        
        print(f"   Found {len(ideas)} idea(s)")
        
        for idea in ideas:
            # Check if already exists
            if check_if_idea_exists(idea):
                print(f"   ⏭️  Skipping (already in DB): {idea[:60]}...")
                total_skipped += 1
            else:
                # Import to database
                if import_idea_to_database(idea):
                    print(f"   ✅ Imported: {idea[:60]}...")
                    total_imported += 1
                else:
                    print(f"   ❌ Failed to import: {idea[:60]}...")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print(f"✅ Imported: {total_imported} new idea(s)")
    print(f"⏭️  Skipped: {total_skipped} existing idea(s)")
    
    # Show current database status
    print("\n📊 DATABASE STATUS AFTER IMPORT:")
    cmd = """
    psql -d travel_website -U fudongli -h localhost -c "
    SELECT 
        COUNT(*) as total_tasks,
        COUNT(CASE WHEN is_fixed THEN 1 END) as completed,
        COUNT(CASE WHEN NOT is_fixed THEN 1 END) as pending
    FROM travel.travel_development_ideas;"
    """
    
    returncode, stdout, stderr = run_command(cmd)
    if returncode == 0:
        print(stdout.strip())
    
    print("=" * 50)

if __name__ == "__main__":
    main()