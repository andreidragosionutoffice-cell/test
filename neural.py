import os
import json
import config

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoModelForCausalLM, AutoTokenizer, AdamW
except ImportError:
    if config.USE_TORCH:
        print("Warning: `transformers` library not found, but torch is available. Please install `transformers`.")
    config.USE_TORCH = False


class NeuralManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None

        if not config.USE_TORCH:
            print("PyTorch or transformers not found. Neural features will be disabled.")
            return

        model_name = "readerbench/ro-gpt2"
        # Load fine-tuned model if it exists, otherwise load base model
        model_path = config.NN_WEIGHTS_FILE
        if os.path.exists(model_path):
            print(f"Loading fine-tuned model from '{model_path}'...")
            model_to_load = model_path
        else:
            print(f"Loading base model '{model_name}'...")
            model_to_load = model_name

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_to_load)
            self.model = AutoModelForCausalLM.from_pretrained(model_to_load)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            print(f"Transformer model loaded successfully.")

        except Exception as e:
            print(f"Error loading Transformer model: {e}")
            self.model = None
            self.tokenizer = None

    class _ConversationDataset(Dataset):
        def __init__(self, tokenizer, data, block_size=128):
            self.tokenizer = tokenizer
            self.examples = []
            for item in data:
                # Format as "input <|endoftext|> output <|endoftext|>"
                text = f"{item['input']}{tokenizer.eos_token}{item['output']}{tokenizer.eos_token}"
                tokenized_text = tokenizer.encode(text)

                if len(tokenized_text) > block_size:
                    tokenized_text = tokenized_text[:block_size]

                self.examples.append(torch.tensor(tokenized_text, dtype=torch.long))

        def __len__(self):
            return len(self.examples)

        def __getitem__(self, i):
            return self.examples[i]

    def _load_training_data(self):
        if os.path.exists(config.TRAINING_DATA_FILE):
            with open(config.TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def train(self, epochs=3):
        if not self.model or not self.tokenizer:
            print("Model or tokenizer not available. Skipping training.")
            return None

        training_data = self._load_training_data()
        if not training_data:
            print("No training data found. Skipping training.")
            return None

        dataset = self._ConversationDataset(self.tokenizer, training_data)
        if len(dataset) == 0:
            print("Dataset is empty. Skipping training.")
            return None

        dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
        optimizer = AdamW(self.model.parameters(), lr=5e-5)

        self.model.train()
        print("Starting fine-tuning...")

        total_loss = 0
        for epoch in range(epochs):
            epoch_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()

                outputs = self.model(batch, labels=batch)
                loss = outputs.loss

                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            avg_loss = epoch_loss / len(dataloader)
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
            total_loss = avg_loss

        try:
            self.model.save_pretrained(config.NN_WEIGHTS_FILE)
            self.tokenizer.save_pretrained(config.NN_WEIGHTS_FILE)
            print(f"Fine-tuning complete. Model saved to '{config.NN_WEIGHTS_FILE}'.")
        except Exception as e:
            print(f"Error saving model: {e}")

        return total_loss

    def generate_response_from_prompt(self, prompt):
        if not self.model or not self.tokenizer:
            return None

        input_text = f"{prompt}{self.tokenizer.eos_token}"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")

        device = self.model.device
        input_ids = input_ids.to(device)

        output_sequences = self.model.generate(
            input_ids,
            max_length=60,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True,
            pad_token_id=self.tokenizer.eos_token_id,
            temperature=0.7,
            top_k=50
        )

        response_text = self.tokenizer.decode(output_sequences[0], skip_special_tokens=True)

        clean_response = response_text.replace(prompt, "").strip()

        if not clean_response:
            return None

        return clean_response

    def reset(self):
        # This method is now more complex as it would involve deleting the saved model directory
        # For now, we can just re-initialize from the base model
        model_name = "readerbench/ro-gpt2"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            return "Transformer model has been reset to the base pre-trained version."
        except Exception as e:
            return f"Error resetting model: {e}"
