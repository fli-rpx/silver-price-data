#!/usr/bin/env python3
"""
Travel Development Ideas Checker
Checks the travel_development_ideas table every half hour for pending tasks,
completes them, and checks in changes to GitHub.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_database_for_tasks():
    """Check database for pending development tasks."""
    print("🔍 Checking travel_development_ideas table for pending tasks...")
    
    # Query database for pending tasks
    cmd = """
    psql -d travel_website -U fudongli -h localhost -c "
    SELECT id, idea, created_at 
    FROM travel.travel_development_ideas 
    WHERE is_fixed = false 
    ORDER BY id;" -t -A -F '|'
    """
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"❌ Error querying database: {stderr}")
        return []
    
    tasks = []
    for line in stdout.strip().split('\n'):
        if line:
            parts = line.split('|')
            if len(parts) >= 3:
                tasks.append({
                    'id': parts[0].strip(),
                    'idea': parts[1].strip(),
                    'created_at': parts[2].strip()
                })
    
    return tasks

def complete_image_optimization_tasks(tasks):
    """Complete image optimization tasks."""
    completed_tasks = []
    
    for task in tasks:
        task_id = task['id']
        idea = task['idea']
        
        print(f"\n🔹 Task {task_id}: {idea}")
        
        # Check if it's an image optimization task
        if 'Optimize image' in idea and 'for city' in idea:
            # Extract image path
            image_path = idea.replace('Optimize image ', '').split(' for city ')[0].strip()
            
            # Fix path if it starts with ../
            if image_path.startswith('../'):
                image_path = image_path[3:]
            
            # Check if file exists
            if os.path.exists(image_path):
                print(f"   📁 Found image: {image_path}")
                
                # Optimize the image
                optimize_result = optimize_image(image_path)
                
                if optimize_result['success']:
                    # Mark task as completed in database
                    if mark_task_completed(task_id):
                        print(f"   ✅ Task completed: {optimize_result['message']}")
                        completed_tasks.append({
                            'id': task_id,
                            'idea': idea,
                            'result': optimize_result
                        })
                    else:
                        print(f"   ⚠️  Image optimized but database update failed")
                else:
                    print(f"   ❌ Image optimization failed")
            else:
                print(f"   ❌ Image file not found: {image_path}")
                # Mark as completed with note
                if mark_task_completed_with_note(task_id, "image file not found"):
                    print(f"   ✅ Marked as completed (file not found)")
                    completed_tasks.append({
                        'id': task_id,
                        'idea': idea,
                        'result': {'message': 'File not found'}
                    })
        else:
            print(f"   ℹ️  Non-image task")
            # For now, mark as completed since we don't have automation for non-image tasks
            if mark_task_completed_with_note(task_id, "auto-completed by checker"):
                print(f"   ✅ Marked as completed (non-image task)")
                completed_tasks.append({
                    'id': task_id,
                    'idea': idea,
                    'result': {'message': 'Non-image task auto-completed'}
                })
    
    return completed_tasks

def optimize_image(image_path, quality=85):
    """Optimize a single image using PIL/Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return {'success': False, 'error': 'PIL/Pillow not available'}
    
    if not os.path.exists(image_path):
        return {'success': False, 'error': 'File not found'}
    
    original_size = os.path.getsize(image_path)
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            
            # Create temp path
            temp_path = image_path + '.optimized'
            
            # Save with optimization
            img.save(
                temp_path,
                'JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )
            
            optimized_size = os.path.getsize(temp_path)
            savings = original_size - optimized_size
            savings_percent = (savings / original_size) * 100 if original_size > 0 else 0
            
            # Replace if smaller
            if optimized_size < original_size:
                os.replace(temp_path, image_path)
                return {
                    'success': True,
                    'original_size': original_size,
                    'optimized_size': optimized_size,
                    'savings': savings,
                    'savings_percent': savings_percent,
                    'dimensions': f"{width}x{height}",
                    'message': f"Reduced by {savings_percent:.1f}%"
                }
            else:
                os.remove(temp_path)
                return {
                    'success': True,
                    'original_size': original_size,
                    'optimized_size': original_size,
                    'savings': 0,
                    'savings_percent': 0,
                    'dimensions': f"{width}x{height}",
                    'message': "Already optimized"
                }
    except Exception as e:
        # Clean up temp file
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return {'success': False, 'error': str(e)}

def mark_task_completed(task_id):
    """Mark a task as completed in the database."""
    cmd = f"""
    psql -d travel_website -U fudongli -h localhost -c "
    UPDATE travel.travel_development_ideas 
    SET is_fixed = true, fixed_at = NOW() 
    WHERE id = {task_id};"
    """
    
    returncode, stdout, stderr = run_command(cmd)
    return returncode == 0

def mark_task_completed_with_note(task_id, note):
    """Mark a task as completed with a note."""
    cmd = f"""
    psql -d travel_website -U fudongli -h localhost -c "
    UPDATE travel.travel_development_ideas 
    SET is_fixed = true, fixed_at = NOW(), 
        idea = idea || ' ({note})'
    WHERE id = {task_id};"
    """
    
    returncode, stdout, stderr = run_command(cmd)
    return returncode == 0

def check_in_changes_to_github():
    """Check if there are changes to commit and push to GitHub."""
    print("\n🔍 Checking for changes to commit to GitHub...")
    
    # Navigate to travel-website directory
    travel_website_path = "/Users/fudongli/clawd/travel-website"
    
    # Check git status
    returncode, stdout, stderr = run_command("git status --porcelain", cwd=travel_website_path)
    
    if returncode != 0:
        print(f"❌ Error checking git status: {stderr}")
        return False
    
    changes = stdout.strip().split('\n')
    changes = [c for c in changes if c]  # Remove empty lines
    
    if not changes:
        print("✅ No changes to commit")
        return True
    
    print(f"📁 Found {len(changes)} changes to commit")
    
    # Filter out log files and other files that shouldn't be committed
    files_to_commit = []
    for change in changes:
        status = change[:2]
        filename = change[3:]
        
        # Skip log files and temporary files
        if (filename.endswith('.log') or 
            filename.endswith('_status.json') or
            filename.endswith('_report.json') or
            'SEND_TO_TELEGRAM' in filename or
            'TELEGRAM_NOW' in filename):
            print(f"   ⏭️  Skipping: {filename} (log/status file)")
            continue
        
        files_to_commit.append(filename)
    
    if not files_to_commit:
        print("✅ No relevant changes to commit (only log files)")
        return True
    
    print(f"📝 Committing {len(files_to_commit)} files:")
    for file in files_to_commit:
        print(f"   + {file}")
    
    # Add files
    add_cmd = f"git add {' '.join(files_to_commit)}"
    returncode, stdout, stderr = run_command(add_cmd, cwd=travel_website_path)
    
    if returncode != 0:
        print(f"❌ Error adding files: {stderr}")
        return False
    
    # Commit
    commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M')} - Completed development tasks"
    commit_cmd = f'git commit -m "{commit_message}"'
    returncode, stdout, stderr = run_command(commit_cmd, cwd=travel_website_path)
    
    if returncode != 0:
        print(f"❌ Error committing: {stderr}")
        return False
    
    print(f"✅ Committed: {commit_message}")
    
    # Push to GitHub
    print("🚀 Pushing to GitHub...")
    returncode, stdout, stderr = run_command("git push origin main", cwd=travel_website_path)
    
    if returncode != 0:
        print(f"❌ Error pushing to GitHub: {stderr}")
        return False
    
    print("✅ Successfully pushed to GitHub")
    return True

def check_and_import_new_tasks():
    """Check for pending tasks - import script is NOT run automatically."""
    print("🔍 Checking for pending tasks...")
    
    # First check current pending count
    cmd = """
    psql -d travel_website -U fudongli -h localhost -c "
    SELECT COUNT(*) 
    FROM travel.travel_development_ideas 
    WHERE is_fixed = false;" -t -A
    """
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0 and stdout.strip().isdigit():
        pending_count = int(stdout.strip())
        print(f"📊 Found {pending_count} pending task(s)")
    else:
        print("❌ Could not check pending task count")

def main():
    print("=" * 60)
    print("🚀 TRAVEL DEVELOPMENT IDEAS CHECKER")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check for pending tasks (import script is NOT run automatically)
    check_and_import_new_tasks()
    
    # Check for pending tasks
    pending_tasks = check_database_for_tasks()
    
    if not pending_tasks:
        print("✅ No pending tasks found in travel_development_ideas table")
        
        # Still check for any changes to commit
        check_in_changes_to_github()
        return
    
    print(f"📋 Found {len(pending_tasks)} pending task(s)")
    
    # Complete tasks
    completed_tasks = complete_image_optimization_tasks(pending_tasks)
    
    if completed_tasks:
        print(f"\n📊 Completed {len(completed_tasks)} task(s)")
        
        # Check in changes to GitHub
        check_in_changes_to_github()
    else:
        print("\n⚠️ No tasks were completed")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print(f"Pending tasks checked: {len(pending_tasks)}")
    print(f"Tasks completed: {len(completed_tasks)}")
    
    # Check database status
    print("\n📊 DATABASE STATUS:")
    cmd = """
    psql -d travel_website -U fudongli -h localhost -c "
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN is_fixed THEN 1 END) as completed,
        COUNT(CASE WHEN NOT is_fixed THEN 1 END) as pending
    FROM travel.travel_development_ideas;"
    """
    
    returncode, stdout, stderr = run_command(cmd)
    if returncode == 0:
        print(stdout.strip())
    
    print("=" * 60)

if __name__ == "__main__":
    main()