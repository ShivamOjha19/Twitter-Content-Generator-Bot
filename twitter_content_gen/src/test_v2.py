from data_collection import collect_tweets, save_tweets
from tweet_generator import TweetGenerator
import time

def test_collection():
    # Test with just one account at a time to avoid rate limits
    test_usernames = ['Param_eth']  # Test with one account first
    max_retries = 3
    
    for retry in range(max_retries):
        try:
            print(f"Attempt {retry + 1} of {max_retries}")
            print("Collecting tweets...")
            
            # Add a longer initial delay
            time.sleep(5)  
            
            tweets_df = collect_tweets(test_usernames, tweet_count=5)  # Reduced tweet count
            
            if not tweets_df.empty:
                save_tweets(tweets_df, 'test_tweets.csv')
                print(f"\nSuccessfully collected {len(tweets_df)} tweets!")
                print("\nSample of collected tweets:")
                print(tweets_df[['username', 'text']].head())

                # Initialize generator
                generator = TweetGenerator()
                
                # Generate some unique tweets
                print("\nGenerating new tweets based on collected data...")
                for i in range(3):
                    new_tweet = generator.generate_tweet(tweets_df)
                    print(f"\nGenerated Tweet {i+1}:")
                    print(new_tweet)
                break
            else:
                print("No tweets were collected. Waiting before retry...")
                time.sleep(15)  # Wait 15 seconds before retry
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if retry < max_retries - 1:
                wait_time = (retry + 1) * 15  # Increase wait time with each retry
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Please try again later.")

if __name__ == "__main__":
    test_collection()