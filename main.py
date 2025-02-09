import requests
import re
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
import argparse


headers = {"User-Agent": "Mozilla/5.0"}

def sanitize_filename(filename):
    """Sanitizes a filename by removing or replacing invalid characters."""
    filename = re.sub(r"[^a-zA-Z0-9_\-.]", "_", filename)
    return filename


def download_file(url):
    try:
        semaphore.acquire()  # Acquire semaphore before downloading
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.fragment:
            filename = parsed_url.fragment
        else:
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "default_filename.rar"
        filename, ext = os.path.splitext(filename)
        filename = sanitize_filename(filename) + ext

        print(f"Downloading {filename}")
        filepath = os.path.join(download_dir, filename)

        counter = 1
        while os.path.exists(filepath):
            filename_no_ext, ext = os.path.splitext(filename)
            filepath = os.path.join(download_dir, f"{filename_no_ext}_{counter}{ext}")
            counter += 1

        with requests.get(url, headers=headers) as response:
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            script_tags = soup.find_all("script")

            for script in script_tags:
                match = re.search(r'window\.open\("([^"]+)"\)', script.text)
                if match:
                    download_link = match.group(1)

                    try:
                        with requests.get(download_link, stream=True) as file_response:
                            file_response.raise_for_status()

                            with open(filepath, "wb") as file:
                                for chunk in file_response.iter_content(chunk_size=8192):
                                    file.write(chunk)
                            print(filepath, "downloaded successfully!")
                            return
                    except requests.exceptions.RequestException as e:
                        print(f"Download failed: {e}")
                        return
            else:
                print("No download link found in <script> tags.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        semaphore.release()  # Release semaphore after downloading




def main():
    try:
        with open(url_file, "r") as file:
            urls = file.readlines()

        threads = []
        for url in urls:
            url = url.strip()
            thread = threading.Thread(target=download_file, args=(url,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("All downloads completed.")

    except FileNotFoundError:
        print(f"Error: {url_file} not found.")
    except Exception as e:
        print(f"An error occurred while reading the URL file: {e}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Download files from fuckingfast website URLs in a text file.")
    parser.add_argument("-f", "--file", help="Specify the URL file to read from.", default="urls.txt")
    parser.add_argument("-d", "--dir", help="Specify the download directory.", default="download")
    parser.add_argument("-b", "--batch", help="Specify the number of concurrent downloads (file downloading parrallel).", type=int, default=3)

    args = parser.parse_args()
    download_dir = args.dir
    batch_size = args.batch
    url_file = args.file


    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating download directory: {e}")
            exit()

    semaphore = threading.Semaphore(batch_size)

    main()
