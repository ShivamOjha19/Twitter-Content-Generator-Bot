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
        # Remove the prompt text if present
        tweet = re.sub(r'^Write.*?about.*?:', '', tweet)
        # Remove URLs
        tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet)
        # Remove mentions
        tweet = re.sub(r'@\w+', '', tweet)
        # Clean up extra spaces
        tweet = ' '.join(tweet.split())
        # Ensure the tweet ends with proper punctuation
        if tweet and not tweet[-1] in '.!?':
            tweet += '.'
        return tweet.strip()
    
    def ensure_complete_sentence(self, text: str) -> str:
        """Ensure the text ends with a complete sentence"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 1:
            # Keep complete sentences only
            complete_sentences = [s.strip() for s in sentences[:-1] if s.strip()]
            if complete_sentences:
                return '. '.join(complete_sentences) + '.'
        return text

    def extract_topics_and_hashtags(self, tweets_df) -> Dict[str, List[str]]:
        topics = []
        hashtags = []
        
        for _, row in tweets_df.iterrows():
            clean_text = self.clean_tweet(row['text'])
            words = set(clean_text.lower().split())
            stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'write', 'tweet', 'about'}
            topics.extend([w for w in words if w not in stop_words and len(w) > 3])
            
            if 'hashtags' in row and row['hashtags']:
                if isinstance(row['hashtags'], list):
                    hashtags.extend(row['hashtags'])
                elif isinstance(row['hashtags'], str):
                    tags = eval(row['hashtags']) if row['hashtags'].startswith('[') else [row['hashtags']]
                    hashtags.extend(tags)
        
        return {
            'topics': list(set(topics)),
            'hashtags': list(set(hashtags))
        }
    
    def generate_tweet(self, tweets_df, max_length: int = 280) -> Dict:
        content = self.extract_topics_and_hashtags(tweets_df)
        topics = content['topics']
        hashtags = content['hashtags']
        
        if not topics:
            return {"error": "No topics found"}
            
        selected_topics = random.sample(topics, min(3, len(topics)))
        prompt = f"Generate a tweet: {', '.join(selected_topics)}"
        
        try:
            # Generate base tweet with more space for processing
            generated = self.generator(
                prompt,
                max_length=max_length - 50,  # Leave more room for processing
                num_return_sequences=1,
                temperature=0.9,
                do_sample=True
            )[0]['generated_text']
            
            # Clean and format the tweet
            cleaned_tweet = self.clean_tweet(generated)
            complete_tweet = self.ensure_complete_sentence(cleaned_tweet)
            
            # Select and format hashtags
            selected_hashtags = []
            if hashtags:
                num_hashtags = min(3, len(hashtags))
                selected_hashtags = random.sample(hashtags, num_hashtags)
            
            # Create analysis version
            analysis_tweet = {
                'base_text': complete_tweet,
                'topics': selected_topics,
                'hashtags': selected_hashtags
            }
            
            # Create ready-to-post version
            ready_to_post = complete_tweet
            if selected_hashtags:
                hashtag_text = ' ' + ' '.join([f'#{tag}' for tag in selected_hashtags])
                if len(ready_to_post + hashtag_text) <= 280:
                    ready_to_post += hashtag_text
                else:
                    # If adding all hashtags would make it too long, add as many as will fit
                    for tag in selected_hashtags:
                        if len(ready_to_post + f' #{tag}') <= 276:
                            ready_to_post += f' #{tag}'
                        else:
                            break
            
            # Final check for length and completeness
            if len(ready_to_post) > 280:
                # Find the last complete sentence that fits
                sentences = re.split(r'([.!?]+)', ready_to_post)
                ready_to_post = ''
                for i in range(0, len(sentences)-1, 2):
                    if len(ready_to_post + sentences[i] + sentences[i+1]) <= 280:
                        ready_to_post += sentences[i] + sentences[i+1]
                    else:
                        break
            
            return {
                'analysis': analysis_tweet,
                'ready_to_post': ready_to_post.strip()
            }
            
        except Exception as e:
            return {"error": f"Error generating tweet: {str(e)}"}