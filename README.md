# Sec-News

## Overview

Sec-News is a Python-based application designed to fetch and aggregate security-related articles from various RSS feeds. The application checks active feed links, retrieves today's articles, and presents them in a user-friendly format. This tool is particularly useful for security professionals, researchers, and enthusiasts who want to stay updated on the latest news in cybersecurity.

## Features

- Fetches RSS feed links from a CSV file.
- Checks the status of feed links and filters out inactive ones.
- Retrieves articles published today from active feeds.
- Generates a Markdown report of the articles.

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps to Install

1. Clone this repository:

   ```bash
   git clone https://github.com/darpan-97/sec-news.git
   cd sec-news
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your CSV file containing RSS feed links in the project directory. Ensure that the CSV has a column named `Feed Link`.

2. Run the script:

   ```bash
   python sec-news.py
   ```

3. The output will be saved as `threat-intel-list.md` in the same directory.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please create an issue or submit a pull request.
