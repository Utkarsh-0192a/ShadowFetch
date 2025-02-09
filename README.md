# Fuckingfast Downloader

A Python script to download files from "fuckingfast" website URLs listed in a text file. It uses multithreading to download multiple files concurrently.

## Features

-   Downloads files from URLs specified in a text file.
-   Uses multithreading for concurrent downloads.
-   Handles dynamic download links found within `<script>` tags.
-   Sanitizes filenames to remove invalid characters.
-   Creates a download directory if it doesn't exist.
-   Handles file naming conflicts by appending a counter.

## Requirements

-   Python 3.x
-   `requests` library
-   `beautifulsoup4` library

You can install the required libraries using pip:

```bash
pip install requests beautifulsoup4
```

## Usage

1.  Save the script to a file, for example, `shadowfetch.py`.
2.  Create a text file (e.g., `urls.txt`) with a list of URLs to download, one URL per line.
3.  Run the script from the command line, providing the URL file as an argument:

    ```bash
    python shadowfetch.py urls.txt
    ```

    You can optionally specify the number of threads to use and the download directory:

    ```bash
    python shadowfetch.py urls.txt -t 10 -d downloads
    ```

    Where:
    - `-t` specifies the number of threads (default is 5).
    - `-d` specifies the download directory (default is "downloads").

## Example `urls.txt`

```text
https://fuckingfast.com/file1
https://fuckingfast.com/file2
https://fuckingfast.com/file3
```

## Notes

-   Ensure that the URLs in the `urls.txt` file are correct and accessible.
-   The script will create the download directory if it does not exist.
-   Filenames are sanitized to remove invalid characters.
-   If a file with the same name already exists in the download directory, a counter will be appended to the filename to avoid overwriting.

