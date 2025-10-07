import time
import os
from twikit import Client
import asyncio
import random

# --- Configuration ---
USERNAME = '@randomizerguy01'
EMAIL = 'randomizerguy01@gmail.com'
PASSWORD = 'randomguy01'

# Initialize client
client = Client('en-US')

async def main():
    print("Logging in...")
    try:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD,
            cookies_file='cookies.json'
        )
        print("✅ Login successful.")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return # Stop the script if login fails

    # --- Use a known active hashtag for testing ---
    SEARCH_QUERY = '#Python' # Change to a popular hashtag to test
    print(f"\n🔍 Searching for tweets with: {SEARCH_QUERY}...")

    try:
        tweets = await client.search_tweet(SEARCH_QUERY, 'Latest')
        
        # This is the most important debugging step!
        print(f"✅ Search complete. Found {len(tweets)} tweets.")

        if not tweets:
            print("The list of tweets is empty. This is likely due to an API block from X.")
        else:
            for tweet in tweets:
                print('---')
                print(f"User: {tweet.user.name}")
                print(f"Text: {tweet.text}")
                print(f"Date: {tweet.created_at}")
                
                delay = random.uniform(2.5, 5.5)
                print(f"Waiting for {delay:.2f} seconds...")
                await asyncio.sleep(delay)

    except Exception as e:
        print(f"❌ An error occurred during search: {e}")

asyncio.run(main())