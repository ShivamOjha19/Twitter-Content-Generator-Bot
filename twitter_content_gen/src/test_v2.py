from data_collection import collect_tweets, save_tweets
from tweet_generator import TweetGenerator
import time
import pandas as pd
import os
from datetime import datetime

def test_collection():
    # Test with just one account at a time to avoid rate limits
    test_usernames = ['AayushStack']  # Test with one account first
    max_retries = 3
    generated_tweets = []
    ready_to_post_tweets = []
    
    for retry in range(max_retries):
        try:
            print(f"Attempt {retry + 1} of {max_retries}")
            print("Collecting tweets...")
            
            time.sleep(5)
            
            tweets_df = collect_tweets(test_usernames, tweet_count=5)
            
            if not tweets_df.empty:
                save_tweets(tweets_df, 'test_tweets.csv')
                print(f"\nSuccessfully collected {len(tweets_df)} tweets!")
                print("\nSample of collected tweets:")
                print(tweets_df[['username', 'text']].head())

                # Initialize generator
                generator = TweetGenerator()
                
                # Generate and save new tweets
                print("\nGenerating new tweets based on collected data...")
                print("\n=== READY TO POST TWEETS ===")
                print("(Copy and paste these directly to Twitter)\n")
                
                for i in range(3):
                    result = generator.generate_tweet(tweets_df)
                    
                    if 'error' not in result:
                        # Store analysis version
                        generated_tweets.append({
                            'tweet_number': i + 1,
                            'base_text': result['analysis']['base_text'],
                            'topics': str(result['analysis']['topics']),
                            'hashtags': str(result['analysis']['hashtags']),
                            'timestamp': datetime.now()
                        })
                        
                        # Store and display ready-to-post version
                        ready_to_post_tweets.append({
                            'tweet_number': i + 1,
                            'text': result['ready_to_post'],
                            'timestamp': datetime.now()
                        })
                        
                        print(f"\n🐦 Tweet {i+1}:")
                        print("-" * 40)
                        print(result['ready_to_post'])
                        print("-" * 40)
                    else:
                        print(f"\nError generating tweet {i+1}: {result['error']}")
                
                # Save both versions
                if generated_tweets:
                    os.makedirs('data/generated', exist_ok=True)
                    
                    # Save analysis version
                    analysis_df = pd.DataFrame(generated_tweets)
                    analysis_df.to_csv('data/generated/generated_tweets_analysis.csv', index=False)
                    
                    # Save ready-to-post version
                    ready_df = pd.DataFrame(ready_to_post_tweets)
                    ready_df.to_csv('data/generated/ready_to_post_tweets.csv', index=False)
                    
                    print("\n✅ Generated tweets saved to:")
                    print("- data/generated/generated_tweets_analysis.csv (Analysis version)")
                    print("- data/generated/ready_to_post_tweets.csv (Ready to post version)")
                break
            else:
                print("No tweets were collected. Waiting before retry...")
                time.sleep(15)
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if retry < max_retries - 1:
                wait_time = (retry + 1) * 15
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Please try again later.")

if __name__ == "__main__":
    test_collection()