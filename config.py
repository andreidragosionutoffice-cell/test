import random

USE_TORCH = True
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except Exception:
    USE_TORCH = False
    torch = None
    nn = None
    optim = None

NAME = "🤖Kellon"
VERSION = "1.5"
DEVELOPER = "ANDRO"
MEMORY_FILE = "kellon_memory.json"
NN_WEIGHTS_FILE = "kellon_nn.pt"
TRAINING_DATA_FILE = "training_dataset.json"
RANDOM_SEED = 42
SHOW_DEBUG = False
random.seed(RANDOM_SEED)

HELP_TEXT = """
Comenzi disponibile:
  skill: Nume | Descriere | Pas1,Pas2,...
  concept: Orice text/idee
  proiect: Nume | Descriere | Goal1,Goal2,...
  progres: NumeProiect | +10
  initiate
  status
  reset_nn
  /train
  ieșire / exit / quit
"""
