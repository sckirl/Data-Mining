import snscrape.modules.twitter as sntwitter

query = '#17plus8'
tweets = []

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    tweets.append(tweet.content)
    if len(tweets) >= 10:
        break

for t in tweets:
    print(t)