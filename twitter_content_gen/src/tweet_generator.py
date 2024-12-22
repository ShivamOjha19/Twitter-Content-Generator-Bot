from transformers import pipeline, set_seed
import random
import re
from typing import List, Dict
import pandas as pd

class TweetGenerator:
    def __init__(self):
        self.generator = pipeline('text-generation', model='gpt2')
        set_seed(42)
        
    def clean_tweet(self, tweet: str) -> str:
        # Remove URLs
        tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet)
        # Remove mentions
        tweet = re.sub(r'@\w+', '', tweet)
        # Clean up extra spaces
        tweet = ' '.join(tweet.split())
        return tweet.strip()
    
    def extract_topics_and_hashtags(self, tweets_df) -> Dict[str, List[str]]:
        topics = []
        hashtags = []
        
        for _, row in tweets_df.iterrows():
            # Extract topics from tweet text
            clean_text = self.clean_tweet(row['text'])
            words = set(clean_text.lower().split())
            stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
            topics.extend([w for w in words if w not in stop_words and len(w) > 3])
            
            # Extract hashtags if available
            if 'hashtags' in row and row['hashtags']:
                if isinstance(row['hashtags'], list):
                    hashtags.extend(row['hashtags'])
                elif isinstance(row['hashtags'], str):
                    # Handle case where hashtags might be a string
                    tags = eval(row['hashtags']) if row['hashtags'].startswith('[') else [row['hashtags']]
                    hashtags.extend(tags)
        
        return {
            'topics': list(set(topics)),
            'hashtags': list(set(hashtags))
        }
    
    def generate_tweet(self, tweets_df, max_length: int = 280) -> Dict:
        # Extract topics and hashtags
        content = self.extract_topics_and_hashtags(tweets_df)
        topics = content['topics']
        hashtags = content['hashtags']
        
        if not topics:
            return {"error": "No topics found"}
            
        # Create a prompt using random topics
        selected_topics = random.sample(topics, min(3, len(topics)))
        prompt = f"Write an engaging tweet about {', '.join(selected_topics)}"
        
        try:
            # Generate base tweet
            generated = self.generator(
                prompt,
                max_length=max_length - 30,  # Leave room for hashtags
                num_return_sequences=1,
                temperature=0.9,
                do_sample=True
            )[0]['generated_text']
            
            # Clean the generated tweet
            cleaned_tweet = self.clean_tweet(generated)
            
            # Select random hashtags (if available)
            selected_hashtags = []
            if hashtags:
                num_hashtags = min(3, len(hashtags))
                selected_hashtags = random.sample(hashtags, num_hashtags)
            
            # Create two versions: analysis version and ready-to-post version
            analysis_tweet = {
                'base_text': cleaned_tweet,
                'topics': selected_topics,
                'hashtags': selected_hashtags
            }
            
            # Create ready-to-post version
            ready_to_post = cleaned_tweet
            if selected_hashtags:
                hashtag_text = ' ' + ' '.join([f'#{tag}' for tag in selected_hashtags])
                ready_to_post += hashtag_text
            
            # Ensure final tweet isn't too long
            if len(ready_to_post) > 280:
                ready_to_post = ready_to_post[:277] + "..."
            
            return {
                'analysis': analysis_tweet,
                'ready_to_post': ready_to_post
            }
            
        except Exception as e:
            return {"error": f"Error generating tweet: {str(e)}"}