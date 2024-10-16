import os
import pandas as pd
import requests
import feedparser
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import gdown
import warnings

# Suppress gdown warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Define the Google Sheets URL and the destination filename
url = "https://docs.google.com/spreadsheets/d/11ebsrFeCaoSup9V3n01tGw4h8vmlVhyQz0kn2EVHM-M/export?format=csv"
destination = "threat-intel-list.csv"

# Check if the file already exists
if not os.path.exists(destination):
    print("Downloading file...")
    gdown.download(url, destination, quiet=False)
    print(f"File downloaded and saved as {destination}")
else:
    print(f"{destination} already exists, skipping download.")

# Fetch today's date in a readable format
today_date = datetime.today().strftime('%B %d, %Y')  # e.g., "October 16, 2024"

# Fetch RSS feed links from CSV
def fetch_rss_links_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'Feed Link' in df.columns:
            feed_links = df['Feed Link'].dropna().tolist()  
            return feed_links
        else:
            return "Feed Link column not found."
    except Exception as e:
        return f"Error fetching data: {e}"

# Check if the feed link is active
def check_feed_link(link):
    try:
        response = requests.head(link, timeout=5)
        return (link, response.status_code)
    except requests.exceptions.RequestException:
        return (link, None)

# Check all feed links and filter out inactive ones
def check_feed_links(feed_links, max_workers=20):
    active_links = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_feed_link, link): link for link in feed_links}
        for future in as_completed(futures):
            link, status = future.result()
            if status == 200:
                active_links.append(link)
    return active_links

# Fetch today's articles from active feed links concurrently
def fetch_todays_articles(feed_link):
    try:
        response = requests.get(feed_link, timeout=5)
        feed = feedparser.parse(response.content)
        today = datetime.today().date()
        todays_articles = []
        
        for entry in feed.entries:
            title = entry.get('title')
            link = entry.get('link')
            published = entry.get('published', entry.get('updated'))

            try:
                published_date = datetime(*entry.published_parsed[:6]).date()
            except:
                continue  # Skip articles without valid date

            if title and link and published_date == today:
                todays_articles.append({'title': title, 'link': link, 'published_date': published_date})
                
                # Limit the articles to only 5
                if len(todays_articles) >= 5:
                    break  # Exit if we have enough articles
        
        return todays_articles
    except Exception:
        return []

# Fetch all feeds in parallel and aggregate results
def fetch_all_todays_articles(feed_links, max_workers=20):
    articles = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_todays_articles, link): link for link in feed_links}
        for future in as_completed(futures):
            articles.extend(future.result())
    return articles

# Write results to a Markdown file
def write_results_to_md(articles, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# Articles Published Today - {today_date}\n\n")
        
        # Loop through articles and add serial numbers
        for index, article in enumerate(articles, start=1):  # Start numbering from 1
            f.write(f"{index}. [{article['title']}]({article['link']})\n")
        
# Example usage
file_path = destination  # Use the downloaded CSV file
results_file_path = 'README.md'  # Output file for results
feed_links = fetch_rss_links_from_csv(file_path)

if isinstance(feed_links, list) and feed_links:
    total_feeds = len(feed_links)
    print(f"Total Feeds: {total_feeds}")

    print("Checking feed links...")
    active_links = check_feed_links(feed_links)
    active_count = len(active_links)

    print(f"Live Feeds: {active_count}/{total_feeds} (Active links checked)")

    print(f"\nFetching articles published on {today_date} from active feeds...")
    todays_articles = fetch_all_todays_articles(active_links)

    if todays_articles:
        print(f"\nArticles published on {today_date}:")  # Updated print statement to include date
        for article in todays_articles:
            print(f"Title: {article['title']}, Link: {article['link']}, Date: {article['published_date']}")
        
        # Write the results to a Markdown file
        write_results_to_md(todays_articles, results_file_path)
        print(f"\nResults saved to {results_file_path}")
    else:
        print("No articles published today.")
else:
    print(feed_links)
