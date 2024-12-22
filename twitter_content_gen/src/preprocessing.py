# src/preprocessing.py
import re
import pandas as pd
from sklearn.model_selection import train_test_split

def clean_tweet(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def prepare_training_data(df):
    # Clean tweets
    df['cleaned_text'] = df['text'].apply(clean_tweet)
    
    # Remove empty tweets
    df = df[df['cleaned_text'].str.len() > 0]
    
    # Sort by engagement (likes + retweets)
    df['engagement'] = df['likes'] + df['retweets']
    df = df.sort_values('engagement', ascending=False)
    
    return df

def create_training_sets(df):
    texts = df['cleaned_text'].tolist()
    return train_test_split(texts, test_size=0.2, random_state=42)