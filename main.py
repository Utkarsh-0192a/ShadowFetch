import requests
import re
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
import argparse
import time  # Import time module

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
TIMEOUT = 30  # Add timeout constant
CHUNK_SIZE = 8192  # Standardize chunk size

download_statuses = {}  # Global dictionary to store download statuses
status_lock = threading.Lock()  # Lock for synchronizing access to statuses
UPDATE_INTERVAL = 1  # Update interval in seconds


def sanitize_filename(filename):
    """Sanitizes a filename by removing or replacing invalid characters."""
    filename = re.sub(r"[^a-zA-Z0-9_\-.]", "_", filename)
    return filename


def print_download_statuses():
    with status_lock:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        for filename, status in download_statuses.items():
            if 'percent_complete' in status:
                print(f"{filename}: {status['percent_complete']:.2f}% downloaded, "
                      f"Elapsed Time: {status['elapsed_time']:.2f}s, "
                      f"ETA: {status['estimated_remaining_time']:.2f}s")
            else:
                print(f"{filename}: Downloaded {status['downloaded_size']} bytes, "
                      f"Elapsed Time: {status['elapsed_time']:.2f}s")


def download_file(url):
    try:
        semaphore.acquire()  # Acquire semaphore before downloading
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")

        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.fragment:
            filename = parsed_url.fragment
        else:
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "default_filename.rar"
        filename, ext = os.path.splitext(filename)
        filename = sanitize_filename(filename) + ext

        filepath = os.path.join(download_dir, filename)

        counter = 1
        while os.path.exists(filepath):
            filename_no_ext, ext = os.path.splitext(filename)
            filepath = os.path.join(download_dir, f"{filename_no_ext}_{counter}{ext}")
            counter += 1
        
        start_time = time.time()  # Record start time
        downloaded_size = 0
        last_update_time = start_time  # Initialize last update time
        
        with status_lock:
            download_statuses[filename] = {'downloaded_size': 0, 'elapsed_time': 0}

        with requests.get(url, headers=headers, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            
            # Add content type validation
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                raise ValueError(f"Unexpected content type: {content_type}")

            soup = BeautifulSoup(response.text, "html.parser")

            script_tags = soup.find_all("script")

            for script in script_tags:
                match = re.search(r'window\.open\("([^"]+)"\)', script.text)
                if match:
                    download_link = match.group(1)

                    try:
                        with requests.get(download_link, stream=True, timeout=TIMEOUT) as file_response:
                            # Add retry mechanism
                            retries = 3
                            while retries > 0:
                                try:
                                    file_response.raise_for_status()
                                    total_size = int(file_response.headers.get('content-length', 0))
                                    
                                    with open(filepath, "wb") as file:
                                        for chunk in file_response.iter_content(chunk_size=CHUNK_SIZE):
                                            file.write(chunk)
                                            downloaded_size += len(chunk)
                                            elapsed_time = time.time() - start_time
                                            download_speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                                            
                                            with status_lock:
                                                if total_size > 0:
                                                    percent_complete = (downloaded_size / total_size) * 100
                                                    remaining_bytes = total_size - downloaded_size
                                                    estimated_remaining_time = remaining_bytes / download_speed if download_speed > 0 else 0
                                                    download_statuses[filename] = {
                                                        'percent_complete': percent_complete,
                                                        'elapsed_time': elapsed_time,
                                                        'estimated_remaining_time': estimated_remaining_time
                                                    }
                                                else:
                                                    download_statuses[filename] = {
                                                        'downloaded_size': downloaded_size,
                                                        'elapsed_time': elapsed_time
                                                    }
                                            
                                            current_time = time.time()
                                            if current_time - last_update_time >= UPDATE_INTERVAL:
                                                print_download_statuses()
                                                last_update_time = current_time

                                    total_time = time.time() - start_time
                                    with status_lock:
                                        del download_statuses[filename]
                                    print_download_statuses()
                                    print(f"{filepath} downloaded successfully in {total_time:.2f} seconds!")
                                    return
                                except requests.exceptions.RequestException:
                                    retries -= 1
                                    if retries == 0:
                                        raise
                                    time.sleep(1)
                    
                    except requests.exceptions.Timeout:
                        print(f"Download timeout for {filename}")
                    except requests.exceptions.RequestException as e:
                        print(f"Download failed: {e}")
                        return
            else:
                print("No download link found in <script> tags.")

    except ValueError as e:
        print(f"Validation error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        semaphore.release()  # Release semaphore after downloading


def main():
    if not os.path.isfile(url_file):
        print(f"Error: URL file '{url_file}' not found")
        return

    try:
        with open(url_file, "r") as file:
            urls = [url.strip() for url in file if url.strip()]
        
        if not urls:
            print("Error: No valid URLs found in the file")
            return

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
