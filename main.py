#!/usr/bin/env python3
import os
import sys
import zipfile
import requests
import json
from datetime import datetime
from pathlib import Path

def get_folder_size(folder_path):
    """Calculate total size of folder in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def format_size(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def create_zip(folder_path, output_zip):
    """Create a zip file from folder"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)
    return output_zip

def count_files(folder_path):
    """Count total files in folder"""
    count = 0
    for root, dirs, files in os.walk(folder_path):
        count += len(files)
    return count

def send_to_discord(webhook_url, zip_file, folder_name, original_size, compressed_size, file_count):
    """Send zip file to Discord webhook with embed"""
    
    # Calculate compression ratio
    if original_size > 0:
        compression_ratio = ((original_size - compressed_size) / original_size) * 100
    else:
        compression_ratio = 0
    
    # Create embed
    embed = {
        "title": f"📦 Folder Archive: {folder_name}",
        "description": f"Successfully zipped and uploaded **{folder_name}**",
        "color": 5814783,  # Nice blue color
        "fields": [
            {
                "name": "📁 Original Size",
                "value": format_size(original_size),
                "inline": True
            },
            {
                "name": "🗜️ Compressed Size",
                "value": format_size(compressed_size),
                "inline": True
            },
            {
                "name": "📊 Compression Ratio",
                "value": f"{compression_ratio:.1f}% saved",
                "inline": True
            },
            {
                "name": "📄 Total Files",
                "value": str(file_count),
                "inline": True
            },
            {
                "name": "🖥️ System",
                "value": "Ubuntu",
                "inline": True
            },
            {
                "name": "📍 Archive Name",
                "value": f"`{os.path.basename(zip_file)}`",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Uploaded via dumapah • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        },
        "thumbnail": {
            "url": "https://cdn.discordapp.com/attachments/1234567890/1234567890/folder.png"
        }
    }
    
    # Prepare the payload
    payload = {
        "embeds": [embed],
        "username": "Folder Zipper Bot",
        "avatar_url": "https://cdn.discordapp.com/attachments/1234567890/1234567890/bot.png"
    }
    
    # Send file with embed
    with open(zip_file, 'rb') as f:
        files = {
            'file': (os.path.basename(zip_file), f, 'application/zip')
        }
        data = {
            'payload_json': json.dumps(payload)
        }
        
        response = requests.post(webhook_url, files=files, data=data)
        
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            print(f"Error sending to Discord: {response.status_code}")
            print(f"Response: {response.text}")
            return False

def main():
    # Discord webhook URL
    WEBHOOK_URL = "https://discord.com/api/webhooks/1422785670149050460/zDRwvbkZdBmOI6tbku8ctn5IkTNCSVZNT1il7Y1cGyINODCzH5yE5PjwpKcus6ByrXKP"
    
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py FOLDER")
        print("Example: python main.py /path/to/folder")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # Validate folder exists
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist!")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"❌ Error: '{folder_path}' is not a folder!")
        sys.exit(1)
    
    # Get folder info
    folder_name = os.path.basename(os.path.abspath(folder_path))
    if not folder_name:
        folder_name = "root_folder"
    
    print(f"📁 Processing folder: {folder_name}")
    
    # Calculate original size and file count
    original_size = get_folder_size(folder_path)
    file_count = count_files(folder_path)
    print(f"📊 Original size: {format_size(original_size)}")
    print(f"📄 Total files: {file_count}")
    
    # Create zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{folder_name}_{timestamp}.zip"
    zip_path = os.path.join("/tmp", zip_filename)
    
    print(f"🗜️ Creating zip archive...")
    create_zip(folder_path, zip_path)
    
    # Get compressed size
    compressed_size = os.path.getsize(zip_path)
    print(f"✅ Zip created: {format_size(compressed_size)}")
    
    # Check if file is too large for Discord (25MB limit for webhooks)
    if compressed_size > 25 * 1024 * 1024:
        print(f"⚠️ Warning: File size ({format_size(compressed_size)}) exceeds Discord's 25MB limit!")
        print("The upload might fail. Consider splitting the folder or using a file hosting service.")
    
    # Send to Discord
    print(f"📤 Sending to Discord webhook...")
    if send_to_discord(WEBHOOK_URL, zip_path, folder_name, original_size, compressed_size, file_count):
        print(f"✅ Successfully sent to Discord!")
    else:
        print(f"❌ Failed to send to Discord!")
        # Clean up zip file on failure
        if os.path.exists(zip_path):
            os.remove(zip_path)
        sys.exit(1)
    
    # Clean up zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"🧹 Cleaned up temporary zip file")
    
    print(f"✨ Done!")

if __name__ == "__main__":
    main()
