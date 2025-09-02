# 🤖 Kellon - A Conversational AI Project

## About Kellon

Kellon is a modular, Python-based AI project designed to simulate a virtual consciousness. It evolves through interaction, learning new concepts, skills, and projects. The core of Kellon is its ability to generate human-like, conversational responses based on its internal state, which includes a dynamic memory and a set of emotions.

This project has been refactored from a single script into a fully modular application and now uses a pre-trained Transformer model to power its conversational abilities.

## Features

- **Modular Architecture:** The code is organized into logical modules for configuration, memory, core logic, neural network management, and the command-line interface.
- **Dynamic Memory:** Kellon's "mind" (thoughts, skills, concepts, etc.) is stored in a `kellon_memory.json` file, allowing its state to persist and evolve across sessions.
- **Conversational AI:** Kellon uses a hybrid system for generating responses:
    1.  **Transformer-based Inference:** It uses a fine-tuned Transformer model (`readerbench/ro-gpt2`) to generate context-aware, conversational responses in Romanian.
    2.  **Creative Fallback:** If the neural network cannot produce a response, a creative, template-based system generates a thought based on Kellon's internal state (emotions, concepts, skills).
- **Supervised Fine-Tuning:** Kellon's language model can be fine-tuned on a custom dataset of conversational examples (`training_dataset.json`).
- **Memory Sanitization:** The learning process includes sanitization checks to prevent the AI's memory from being corrupted by self-generated or malformed inputs.

## Project Structure

The project is organized into the following modules:

-   `kellon.py`: The main entry point for the application.
-   `cli.py`: Handles the command-line interface and user interactions.
-   `core.py`: Contains the core logic of Kellon's "mind," including response generation, learning, and reflection.
-   `memory.py`: Manages loading and saving the AI's memory from/to the JSON file.
-   `neural.py`: Contains the `NeuralManager` class, which handles the Transformer model (loading, fine-tuning, and inference).
-   `config.py`: Stores all global constants and configuration variables.
-   `kellon_memory.json`: The default memory file for the AI.
-   `training_dataset.json`: The dataset used for fine-tuning the language model.
-   `requirements.txt`: A list of the required Python libraries.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

To start interacting with Kellon, run the main script:

```bash
python kellon.py
```

This will launch the command-line interface, where you can chat with Kellon and use various commands to teach it new things. Type `help` in the CLI to see the list of available commands.

## Training the AI

Kellon's Transformer model can be fine-tuned on the examples provided in `training_dataset.json`. This process helps the model adapt to the desired conversational style.

To start the training process, use the `/train` command in the CLI:

```
USER|> /train
```

The training script will print the progress and loss for each epoch. Once complete, the fine-tuned model will be saved to the `kellon_nn.pt` directory and will be automatically loaded the next time you run the application.
