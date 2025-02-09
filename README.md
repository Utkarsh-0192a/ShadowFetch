# ShadowFetch Downloader

A specialized Python downloader for fuckingfast.co URLs with multi-threaded capabilities.

## Features

- Multi-threaded downloads with configurable batch size
- Auto-retry mechanism for failed downloads
- Progress tracking with ETA
- Intelligent filename handling
- Timeout protection
- Content validation

## Requirements

Python 3.6 or higher and the following packages:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py -f urls.txt -d downloads -b 3
```

Arguments:
- `-f, --file`: URL file (default: urls.txt)
- `-d, --dir`: Download directory (default: download)
- `-b, --batch`: Concurrent downloads (default: 3)

## URL File Format

Each line should contain one fuckingfast.co URL:
```
https://fuckingfast.co/XXXXX#filename.rar
https://fuckingfast.co/YYYYY#filename2.rar
```

## Error Handling

- Validates URL format
- Handles network timeouts
- Retries failed downloads
- Validates content types
- Manages disk space errors

## Notes

- Default timeout: 30 seconds
- Automatic file renaming for conflicts
- Progress updates every second

