import os
import csv
import random
from twikit import Client
import asyncio

# --- Configuration ---
COOKIES_FILE = 'cookies.json'
OUTPUT_CSV_FILE = '17plus8.csv'

HASHTAG_TO_SEARCH = [# "17plus8", 
                     # "ResetIndonesia",
                     # "TuntutanRakyat",
                     # "ReformasiDikorupsi",
                     # "SuaraRakyat",
                     # "NegaraTidakBaikBaikSaja",
                     # "SelamatkanDemokrasi",
                     # "RakyatBergerak",
                     # "Aksi178",
                     "DPRWajibDengar"]

# Initialize client
client = Client('id')

async def main():
    # Try to log in with cookies first
    for HASHTAG in HASHTAG_TO_SEARCH:

        if os.path.exists(COOKIES_FILE):
            print("Found cookie file, attempting to load...")
            client.load_cookies(COOKIES_FILE)
            print("✅ Successfully logged in using cookies.")
            
            
            print(f"\nSearching for tweets with '{HASHTAG}'...")
            tweets = await client.search_tweet(HASHTAG, count=100, product='Top')
            
            if not tweets:
                print(f"No tweets found for '{HASHTAG}'.")
                continue

            print(f"✅ Found {len(tweets)} tweets. Checking against '{OUTPUT_CSV_FILE}'...")

            # Read existing tweet URLs to avoid duplicates
            existing_urls = set()
            file_exists = os.path.exists(OUTPUT_CSV_FILE)
            if file_exists:
                with open(OUTPUT_CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    # Skip header and read URLs from the 4th column (index 3)
                    next(reader, None) 
                    for row in reader:
                        if len(row) > 3:
                            existing_urls.add(row[3])

            # Open the file in append mode ('a')
            with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write the header only if the file is new
                if not file_exists:
                    writer.writerow(['Username', 'Name', 'Tweet Text', 'Tweet URL', "Created at"])
                
                new_tweets_saved = 0
                # Write tweet data if it's not a duplicate
                for tweet in tweets:
                    url = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                    
                    if url not in existing_urls:
                        writer.writerow([
                            tweet.user.screen_name,
                            tweet.user.name,
                            tweet.text,
                            url,
                            tweet.created_at_datetime
                        ])
                        new_tweets_saved += 1
                        print(f"Saved new tweet #{new_tweets_saved} from @{tweet.user.screen_name}")
                        
                        # Add a random delay
                        delay = random.uniform(1.5, 4.0)
                        print(f"   Waiting for {delay:.2f} seconds...")
                        await asyncio.sleep(delay)

            print('--------------------')
            print(f"✅ Scrape complete. Added {new_tweets_saved} new tweets to '{OUTPUT_CSV_FILE}'.")

        else:
            print(f"Error: '{COOKIES_FILE}' not found. Please ensure it's in the same directory.")

        # Add a random delay
        delay = random.uniform(3.5, 10.0)
        print(f"   Waiting for {delay:.2f} seconds...")
        await asyncio.sleep(delay)

if __name__ == '__main__':
    asyncio.run(main())