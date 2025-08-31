import os
import config

class NeuralManager:
    def __init__(self, memory):
        self.memory = memory
        self.vocab = self._SimpleVocab()
        self.kellon_nn = None
        self.optimizer = None
        self.loss_fn = None
        self._kellon_input_size = None

        self._update_vocab_from_memory()
        if config.USE_TORCH:
            self._build_nn()

    # --- "Private" Classes ---
    class _SimpleVocab:
        def __init__(self):
            self.word2idx = {}
            self.idx2word = []

        def add_words(self, words):
            for w in words:
                w = str(w).strip()
                if w and w not in self.word2idx:
                    self.word2idx[w] = len(self.idx2word)
                    self.idx2word.append(w)

        def encode_dense(self, words):
            vec = [0.0]*len(self.idx2word)
            for w in words:
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
                self._input_size = input_size
                self._output_size = output_size

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

    def _update_vocab_from_memory(self):
        words = []
        words += self.memory.get("concepts", [])
        words += [s["name"] for s in self.memory.get("skills", []) if isinstance(s, dict)]
        words += self.memory.get("history", [])
        self.vocab.add_words(words)
        return words

    def _memory_to_vector(self):
        words = self._update_vocab_from_memory()
        return self.vocab.encode_dense(words)

    # --- Public API Methods ---
    def train(self, epochs=3):
        if not config.USE_TORCH:
            return None

        self._update_vocab_from_memory()

        input_size = max(1, self.vocab.size())
        if self._kellon_input_size != input_size:
            self._build_nn(rebuild=True)

        x = self._memory_to_vector()
        if x.numel() == 0:
            if self._kellon_input_size is None:
                self._build_nn(rebuild=True)
            if self._kellon_input_size is None:
                return None
            x = config.torch.zeros(self._kellon_input_size)

        x_t = x.unsqueeze(0)
        target = x_t.clone()
        last_loss = None
        for _ in range(max(1, epochs)):
            self.optimizer.zero_grad()
            out = self.kellon_nn(x_t)
            loss = self.loss_fn(out, target)
            loss.backward()
            self.optimizer.step()
            last_loss = float(loss.item())
        try:
            config.torch.save(self.kellon_nn.state_dict(), config.NN_WEIGHTS_FILE)
        except Exception:
            pass
        return last_loss

    def reset(self):
        if os.path.exists(config.NN_WEIGHTS_FILE):
            try:
                os.remove(config.NN_WEIGHTS_FILE)
                self._build_nn(rebuild=True)
                return "Greutățile NN au fost șterse. Rețeaua va reîncepe să învețe incremental."
            except Exception as e:
                return f"Nu am putut șterge greutățile NN: {e}"
        return "Nu există fișier de greutăți NN."
