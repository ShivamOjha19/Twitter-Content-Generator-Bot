from transformers import pipeline, set_seed
import random
import re
from typing import List

class TweetGenerator:
    def __init__(self):
        # Initialize the GPT-2 model for text generation
        self.generator = pipeline('text-generation', model='gpt2')
        set_seed(42)  # For reproducibility
        
    def clean_tweet(self, tweet: str) -> str:
        # Remove URLs
        tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet)
        # Remove mentions
        tweet = re.sub(r'@\w+', '', tweet)
        # Clean up extra spaces
        tweet = ' '.join(tweet.split())
        return tweet.strip()
    
    def extract_topics(self, tweets_df) -> List[str]:
        # Extract main topics/keywords from existing tweets
        topics = []
        for tweet in tweets_df['text']:
            # Remove URLs and mentions
            clean_text = self.clean_tweet(tweet)
            # Split into words and get unique ones
            words = set(clean_text.lower().split())
            # Filter out common words (you can expand this list)
            stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
            topics.extend([w for w in words if w not in stop_words and len(w) > 3])
        return list(set(topics))
    
    def generate_tweet(self, tweets_df, max_length: int = 280) -> str:
        # Get topics from existing tweets
        topics = self.extract_topics(tweets_df)
        
        if not topics:
            return "Could not generate tweet: No topics found"
            
        # Create a prompt using random topics
        selected_topics = random.sample(topics, min(3, len(topics)))
        prompt = f"Write a tweet about {', '.join(selected_topics)}"
        
        # Generate new tweet
        try:
            generated = self.generator(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.9,  # Higher temperature for more creativity
                do_sample=True
            )[0]['generated_text']
            
            # Clean the generated tweet
            cleaned_tweet = self.clean_tweet(generated)
            
            # Ensure it's not too long
            if len(cleaned_tweet) > 280:
                cleaned_tweet = cleaned_tweet[:277] + "..."
                
            return cleaned_tweet
            
        except Exception as e:
            return f"Error generating tweet: {str(e)}"