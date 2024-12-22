# src/generator.py
from data_collection import collect_tweets, save_tweets
from preprocessing import prepare_training_data, create_training_sets
from model import TweetGenerator

def main():
    # 1. Collect data
    usernames = ['Param_eth', 'AayushStack', 'uttam_singhk']  # Add your target accounts
    tweets_df = collect_tweets(usernames)
    save_tweets(tweets_df, 'raw_tweets.csv')
    
    # 2. Preprocess data
    processed_df = prepare_training_data(tweets_df)
    train_texts, test_texts = create_training_sets(processed_df)
    
    # 3. Initialize and train model
    generator = TweetGenerator()
    train_dataset = generator.prepare_data(train_texts)
    generator.train(train_dataset)
    
    # 4. Generate tweets
    for _ in range(5):
        tweet = generator.generate_tweet()
        print(f"Generated Tweet: {tweet}\n")

if __name__ == "__main__":
    main()