from data_collection import collect_tweets, save_tweets
from tweet_generator import TweetGenerator
import time
import pandas as pd
import os
from datetime import datetime

def test_collection():
    # Test with just one account at a time to avoid rate limits
    test_usernames = ['']  # Testing with one account first
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
                # Create directories if they don't exist
                os.makedirs('data/raw', exist_ok=True)
                os.makedirs('data/generated', exist_ok=True)
                
                # Save collected tweets
                save_tweets(tweets_df, 'test_tweets.csv')
                print(f"\nSuccessfully collected {len(tweets_df)} tweets!")
                print("\nSample of collected tweets:")
                print(tweets_df[['username', 'text']].head())

                # Initialize generator
                generator = TweetGenerator()
                
                # Generate and save new tweets
                print("\nGenerating new tweets based on collected data...")
                print("\n📱 READY TO POST TWEETS 📱")
                print("(Copy any of these tweets below and paste directly to Twitter)\n")
                
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
                        ready_to_post = result['ready_to_post']
                        ready_to_post_tweets.append({
                            'tweet_number': i + 1,
                            'text': ready_to_post,
                            'timestamp': datetime.now()
                        })
                        
                        print(f"\n🐦 Tweet {i+1}:")
                        print("─" * 60)
                        print(ready_to_post)
                        print("─" * 60)
                    else:
                        print(f"\nError generating tweet {i+1}: {result['error']}")
                
                # Save both versions
                if generated_tweets:
                    # Save analysis version
                    analysis_df = pd.DataFrame(generated_tweets)
                    analysis_df.to_csv('data/generated/generated_tweets_analysis.csv', 
                                     index=False, encoding='utf-8')
                    
                    # Save ready-to-post version
                    ready_df = pd.DataFrame(ready_to_post_tweets)
                    ready_df.to_csv('data/generated/ready_to_post_tweets.csv', 
                                  index=False, encoding='utf-8')
                    
                    print("\n✅ Generated tweets saved to:")
                    print("- data/generated/generated_tweets_analysis.csv (Analysis version)")
                    print("- data/generated/ready_to_post_tweets.csv (Ready to post version)")
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

def main():
    try:
        test_collection()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        print("\nProcess completed. Check the 'data' folder for generated tweets.")

if __name__ == "__main__":
    main()