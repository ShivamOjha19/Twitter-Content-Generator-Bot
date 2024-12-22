import tweepy
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from typing import List, Dict

def setup_twitter_client():
    """
    Set up and return the Twitter API v2 client using credentials from .env file
    """
    load_dotenv()
    return tweepy.Client(
        bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET')
    )

def collect_tweets(usernames: List[str], tweet_count: int = 10) -> pd.DataFrame:
    """
    Collect tweets from specified usernames with rate limit handling
    
    Args:
        usernames: List of Twitter usernames to collect tweets from
        tweet_count: Number of tweets to collect per user (default: 10)
        
    Returns:
        pandas.DataFrame containing collected tweets
    """
    client = setup_twitter_client()
    all_tweets = []
    
    for username in usernames:
        try:
            # Add delay between requests to avoid rate limits
            time.sleep(2)  # Wait 2 seconds between requests
            
            # Get user ID (required for v2 API)
            user = client.get_user(username=username)
            if not user.data:
                print(f"Could not find user: {username}")
                continue
                
            user_id = user.data.id
            
            # Add another small delay before fetching tweets
            time.sleep(1)
            
            # Fetch tweets with public metrics
            tweets = client.get_users_tweets(
                id=user_id,
                max_results=tweet_count,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                exclude=['retweets', 'replies']  # Only get original tweets
            )
            
            if tweets.data:
                for tweet in tweets.data:
                    tweet_data = {
                        'username': username,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'likes': tweet.public_metrics['like_count'],
                        'retweets': tweet.public_metrics['retweet_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count']
                    }
                    
                    # Extract hashtags if available
                    if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                        tweet_data['hashtags'] = [tag['tag'] for tag in tweet.entities['hashtags']]
                    else:
                        tweet_data['hashtags'] = []
                        
                    # Extract topics if available
                    if hasattr(tweet, 'context_annotations'):
                        tweet_data['topics'] = [
                            annotation['domain']['name']
                            for annotation in tweet.context_annotations
                            if 'domain' in annotation
                        ]
                    else:
                        tweet_data['topics'] = []
                        
                    all_tweets.append(tweet_data)
                    
            print(f"Successfully collected tweets from {username}")
                    
        except Exception as e:
            print(f"Error collecting tweets from {username}: {str(e)}")
            time.sleep(5)  # Wait longer if we hit an error
            
    # Create DataFrame
    tweets_df = pd.DataFrame(all_tweets)
    
    # Add basic preprocessing
    if not tweets_df.empty:
        # Convert timestamps to datetime if needed
        if 'created_at' in tweets_df.columns:
            tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'])
            
        # Sort by engagement (likes + retweets)
        tweets_df['engagement'] = tweets_df['likes'] + tweets_df['retweets']
        tweets_df = tweets_df.sort_values('engagement', ascending=False)
    
    return tweets_df

def save_tweets(df: pd.DataFrame, filename: str) -> None:
    """
    Save collected tweets to a CSV file
    
    Args:
        df: DataFrame containing tweets
        filename: Name of the file to save to
    """
    # Create data directory if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)
    
    # Save to CSV
    file_path = f'data/raw/{filename}'
    df.to_csv(file_path, index=False)
    print(f"Saved {len(df)} tweets to {file_path}")

def get_user_info(username: str) -> Dict:
    """
    Get detailed information about a Twitter user
    
    Args:
        username: Twitter username
        
    Returns:
        Dictionary containing user information
    """
    client = setup_twitter_client()
    try:
        user = client.get_user(
            username=username,
            user_fields=['description', 'public_metrics', 'created_at']
        )
        
        if user.data:
            return {
                'id': user.data.id,
                'username': username,
                'description': user.data.description,
                'followers_count': user.data.public_metrics['followers_count'],
                'following_count': user.data.public_metrics['following_count'],
                'tweet_count': user.data.public_metrics['tweet_count'],
                'created_at': user.data.created_at
            }
            
    except Exception as e:
        print(f"Error getting info for user {username}: {str(e)}")
        
    return None

if __name__ == "__main__":
    # Test the functionality
    test_usernames = ['Twitter']
    tweets_df = collect_tweets(test_usernames)
    if not tweets_df.empty:
        save_tweets(tweets_df, 'test_tweets.csv')
        print("\nSample of collected tweets:")
        print(tweets_df[['username', 'text', 'engagement']].head())