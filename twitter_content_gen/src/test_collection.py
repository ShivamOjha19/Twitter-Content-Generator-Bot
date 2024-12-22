# src/test_collection.py
import tweepy
from dotenv import load_dotenv
import os

def test_twitter_connection():
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Print first few characters of credentials (for verification)
    print("API Key starts with:", api_key[:5] if api_key else "Not found")
    print("API Secret starts with:", api_secret[:5] if api_secret else "Not found")
    
    try:
        # Initialize Twitter client
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        # Test the connection by fetching your own account details
        user = api.verify_credentials()
        print("\nSuccessfully connected to Twitter API!")
        print(f"Authenticated as: @{user.screen_name}")
        
        # Test tweet collection from a public account (e.g., Twitter)
        test_username = "Twitter"
        tweets = api.user_timeline(screen_name=test_username, count=5, tweet_mode="extended")
        
        print(f"\nSuccessfully fetched {len(tweets)} tweets from @{test_username}")
        print("\nSample tweet:")
        print(tweets[0].full_text[:100] + "...")
        
        return True
        
    except Exception as e:
        print("\nError occurred:", str(e))
        return False

if __name__ == "__main__":
    test_twitter_connection()