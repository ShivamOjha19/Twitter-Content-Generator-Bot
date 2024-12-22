# src/model.py
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

class TweetGenerator:
    def __init__(self, model_name=config.MODEL_NAME):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Add padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def prepare_data(self, texts):
        # Tokenize texts
        encodings = self.tokenizer(texts, truncation=True, padding=True)
        
        # Create dataset
        dataset = TextDataset(
            tokenizer=self.tokenizer,
            file_path=texts,
            block_size=128
        )
        
        return dataset
        
    def train(self, dataset):
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=config.EPOCHS,
            per_device_train_batch_size=config.BATCH_SIZE,
            save_steps=500,
            save_total_limit=2,
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
        )
        
        trainer.train()
        
    def generate_tweet(self, prompt="", max_length=config.MAX_LENGTH):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)