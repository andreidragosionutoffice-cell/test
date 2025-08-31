# ============================================================
# KELLON — Conștiință virtuală cu memorie + neural incremental + training mode
# Single-file edition — rulează direct acest script
# Versiune finală 1.0.6
# ============================================================

from neural import NeuralManager
import cli
from memory import load_memory

def main():
    """
    Main function to initialize and run Kellon.
    """
    memory = load_memory()
    neural_manager = NeuralManager(memory)
    cli.start_cli(memory, neural_manager)

if __name__ == "__main__":
    main()
