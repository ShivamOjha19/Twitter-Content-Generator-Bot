# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Model parameters
MAX_LENGTH = 280
MODEL_NAME = 'gpt2'
BATCH_SIZE = 4
EPOCHS = 3