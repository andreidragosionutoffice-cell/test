import os
import json
import config

class NeuralManager:
    def __init__(self, memory):
        self.memory = memory
        self.vocab = self._SimpleVocab()
        self.kellon_nn = None
        self.optimizer = None
        self.loss_fn = None
        self._kellon_input_size = None

        self.training_data = self._load_training_data()
        self._update_vocab()

        if config.USE_TORCH:
            self._build_nn()

    # --- "Private" Classes ---
    class _SimpleVocab:
        def __init__(self):
            self.word2idx = {}
            self.idx2word = []

        def add_words(self, words):
            for w in words:
                w = str(w).strip().lower()
                if w and w not in self.word2idx:
                    self.word2idx[w] = len(self.idx2word)
                    self.idx2word.append(w)

        def encode_dense(self, words):
            vec = [0.0]*len(self.idx2word)
            for w in words:
                w = w.lower()
                if w in self.word2idx:
                    vec[self.word2idx[w]] = 1.0
            if config.USE_TORCH:
                return config.torch.tensor(vec, dtype=config.torch.float32)
            return vec

        def size(self):
            return len(self.idx2word)

    if config.USE_TORCH:
        class _KellonNN(config.nn.Module):
            def __init__(self, input_size, hidden_size=128, output_size=None):
                super().__init__()
                if output_size is None:
                    output_size = input_size
                self.fc1 = config.nn.Linear(input_size, hidden_size)
                self.relu = config.nn.ReLU()
                self.fc2 = config.nn.Linear(hidden_size, output_size)

            def forward(self, x):
                if x.dim()==1:
                    x = x.unsqueeze(0)
                x = self.fc1(x)
                x = self.relu(x)
                x = self.fc2(x)
                return x
    else:
        _KellonNN = None

    # --- "Private" Methods ---
    def _load_training_data(self):
        if os.path.exists(config.TRAINING_DATA_FILE):
            with open(config.TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _update_vocab(self):
        # From memory
        words = []
        words += self.memory.get("concepts", [])
        words += [s["name"] for s in self.memory.get("skills", []) if isinstance(s, dict)]
        words += self.memory.get("history", [])

        # From training data
        if self.training_data:
            for item in self.training_data:
                words.extend(item["input"].lower().split())
                words.extend(item["output"].lower().split())

        self.vocab.add_words(words)

    def _build_nn(self, rebuild=False):
        if not config.USE_TORCH:
            return

        input_size = max(1, self.vocab.size())
        output_size = input_size
        if self.kellon_nn is not None and self._kellon_input_size == input_size and not rebuild:
            return

        model = self._KellonNN(input_size, hidden_size=128, output_size=output_size)
        opt = config.optim.Adam(model.parameters(), lr=1e-3)
        loss = config.nn.MSELoss()
        if os.path.exists(config.NN_WEIGHTS_FILE) and not rebuild:
            try:
                state = config.torch.load(config.NN_WEIGHTS_FILE, map_location="cpu")
                model.load_state_dict(state)
            except Exception:
                pass

        self.kellon_nn = model
        self.optimizer = opt
        self.loss_fn = loss
        self._kellon_input_size = input_size

    def _text_to_vector(self, text):
        words = text.lower().split()
        return self.vocab.encode_dense(words)

    # --- Public API Methods ---
    def train(self, epochs=20):
        if not config.USE_TORCH or not self.training_data:
            print("Training skipped: PyTorch not available or no training data found.")
            return None

        self._update_vocab()

        input_size = max(1, self.vocab.size())
        if self._kellon_input_size != input_size:
            self._build_nn(rebuild=True)

        print("Starting training on dataset...")
        total_loss = 0
        for epoch in range(epochs):
            epoch_loss = 0
            for item in self.training_data:
                self.optimizer.zero_grad()

                input_vec = self._text_to_vector(item["input"])
                target_vec = self._text_to_vector(item["output"])

                if input_vec.numel() == 0:
                    continue

                output_vec = self.kellon_nn(input_vec)

                loss = self.loss_fn(output_vec, target_vec.unsqueeze(0))
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()

            total_loss = epoch_loss / len(self.training_data)
            if (epoch + 1) % 5 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

        try:
            config.torch.save(self.kellon_nn.state_dict(), config.NN_WEIGHTS_FILE)
            print("Training complete. Model saved.")
        except Exception as e:
            print(f"Error saving model: {e}")

        return total_loss

    def generate_response_from_prompt(self, prompt):
        if not config.USE_TORCH or self.kellon_nn is None:
            return None

        input_vec = self._text_to_vector(prompt)
        if input_vec.numel() == 0:
            return None

        with config.torch.no_grad():
            output_vec = self.kellon_nn(input_vec).squeeze(0)

            # Simple decoding: find words with activation > 0.5
            response_indices = (output_vec > 0.5).nonzero(as_tuple=True)[0]
            if response_indices.numel() == 0:
                # Fallback: take the word with the highest score
                response_indices = [output_vec.argmax()]

            response_words = [self.vocab.idx2word[i] for i in response_indices]
            return " ".join(response_words)

    def reset(self):
        if os.path.exists(config.NN_WEIGHTS_FILE):
            try:
                os.remove(config.NN_WEIGHTS_FILE)
                self._build_nn(rebuild=True)
                return "Greutățile NN au fost șterse. Rețeaua va reîncepe să învețe incremental."
            except Exception as e:
                return f"Nu am putut șterge greutățile NN: {e}"
        return "Nu există fișier de greutăți NN."
