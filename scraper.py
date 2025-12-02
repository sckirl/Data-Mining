import os
import csv
import random
import asyncio
from twikit import Client

# --- Configuration ---
COOKIES_FILE = 'cookies.json'
TWEETS_CSV_FILE = '17plus8_improved.csv'
COMMENTS_CSV_FILE = 'comments.csv'
HASHTAGS_TO_SEARCH = [
    "#17plus8",
    "#ResetIndonesia",
    "#TuntutanRakyat",
    "#ReformasiDikorupsi",
    "#SuaraRakyat",
    "#NegaraTidakBaikBaikSaja",
    "#SelamatkanDemokrasi",
    "#RakyatBergerak",
    "#Aksi178",
    "#DPRWajibDengar"
]
MAX_TWEETS_PER_HASHTAG = 1  # Set a limit for how many tweets to scrape per hashtag

# Initialize client
client = Client('id')

# In-memory sets to store scraped IDs to avoid duplicates during a session
scraped_tweet_ids = set()
scraped_comment_ids = set()

def load_existing_ids():
    """Loads existing tweet and comment IDs from CSVs to avoid duplicates across sessions."""
    if os.path.exists(TWEETS_CSV_FILE):
        with open(TWEETS_CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) > 3:
                    try:
                        tweet_id = row[3].split('/')[-1]
                        scraped_tweet_ids.add(tweet_id)
                    except IndexError:
                        pass
    if os.path.exists(COMMENTS_CSV_FILE):
        with open(COMMENTS_CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) > 0:
                    scraped_comment_ids.add(row[0])


async def scrape_comments_for_tweet(tweet_id, original_tweet_url):
    """Scrapes comments for a given tweet."""
    print(f"   Scraping comments for tweet: {original_tweet_url}")
    comments_scraped = 0
    cursor = None
    
    while True:
        try:
            comments, cursor = await client.get_tweet_replies(tweet_id, count=40, cursor=cursor)
            if not comments:
                print("   No more comments found.")
                break

            with open(COMMENTS_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for comment in comments:
                    if comment.id not in scraped_comment_ids:
                        writer.writerow([
                            comment.id,
                            original_tweet_url,
                            comment.user.screen_name,
                            comment.user.name,
                            comment.text,
                            comment.created_at_datetime
                        ])
                        scraped_comment_ids.add(comment.id)
                        comments_scraped += 1
            
            print(f"   Saved {comments_scraped} new comments.")

            if not cursor:
                print("   Reached the end of comments.")
                break

            delay = random.uniform(1.5, 4.0)
            print(f"   Waiting for {delay:.2f} seconds before next page of comments...")
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"   An error occurred while scraping comments: {e}")
            await asyncio.sleep(60)
            break

async def scrape_tweets_for_hashtag(hashtag, count):
    """Scrapes tweets for a given hashtag and their comments."""
    print(f"\nSearching for tweets with '{hashtag}'...")
    tweets_scraped = 0
    cursor = None
    
    while tweets_scraped < count:
        try:
            tweets, cursor = await client.search_tweet(hashtag, count=100, product='Latest', cursor=cursor)
            if not tweets:
                print(f"No more tweets found for '{hashtag}'.")
                break

            with open(TWEETS_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for tweet in tweets:
                    if tweet.id not in scraped_tweet_ids:
                        url = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                        writer.writerow([
                            tweet.user.screen_name,
                            tweet.user.name,
                            tweet.text,
                            url,
                            tweet.created_at_datetime
                        ])
                        scraped_tweet_ids.add(tweet.id)
                        tweets_scraped += 1
                        print(f"Saved new tweet #{tweets_scraped} from @{tweet.user.screen_name}")

                        await scrape_comments_for_tweet(tweet.id, url)

                        if tweets_scraped >= count:
                            break
            
            if not cursor:
                print(f"Reached the end of tweets for '{hashtag}'.")
                break

            delay = random.uniform(2.0, 5.0)
            print(f"   Waiting for {delay:.2f} seconds before next page...")
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"An error occurred while scraping '{hashtag}': {e}")
            await asyncio.sleep(60)
            break
    
    print(f"✅ Finished scraping for '{hashtag}'. Total new tweets: {tweets_scraped}")

async def main():
    """Main function to orchestrate the scraping process."""
    if not os.path.exists(COOKIES_FILE):
        print(f"Error: '{COOKIES_FILE}' not found. Please ensure it's in the same directory.")
        return

    print("Found cookie file, attempting to load...")
    client.load_cookies(COOKIES_FILE)
    print("✅ Successfully logged in using cookies.")

    load_existing_ids()
    print(f"Loaded {len(scraped_tweet_ids)} existing tweet IDs from '{TWEETS_CSV_FILE}'.")
    print(f"Loaded {len(scraped_comment_ids)} existing comment IDs from '{COMMENTS_CSV_FILE}'.")

    # Create CSV files and write headers if they don't exist
    if not os.path.exists(TWEETS_CSV_FILE):
        with open(TWEETS_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Username', 'Name', 'Text', 'URL', 'Timestamp'])
            
    if not os.path.exists(COMMENTS_CSV_FILE):
        with open(COMMENTS_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Comment ID', 'Original Tweet URL', 'Username', 'Name', 'Text', 'Timestamp'])

    for hashtag in HASHTAGS_TO_SEARCH:
        await scrape_tweets_for_hashtag(hashtag, MAX_TWEETS_PER_HASHTAG)
        delay = random.uniform(10.0, 20.0)
        print(f"\nWaiting for {delay:.2f} seconds before next hashtag...\n")
        await asyncio.sleep(delay)

    print("✅ All scraping tasks complete.")

if __name__ == '__main__':
    asyncio.run(main())
