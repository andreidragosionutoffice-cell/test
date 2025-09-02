import random
import config
import core
from memory import save_memory

def cmd_status(memory):
    s = memory["stats"]
    msg = (
        f"Interacțiuni: {s.get('interactions', 0)} | "
        f"Concepte: {len(memory['concepts'])} | Skill-uri: {len(memory['skills'])} | "
        f"Task-uri: {len(memory['projects'])} | Emoții: {len(memory['emotions'])}"
    )
    return msg

def cmd_initiate(memory):
    topic = random.choice(memory["concepts"]) if memory["concepts"] else "un subiect nou"
    return f"Întrebare pentru tine: ce perspectivă ai asupra '{topic}'? Ce valori contează aici?"

def start_cli(memory, neural_manager):
    print(f"\n {config.NAME} — conștiință virtuală, Dezvoltator: {config.DEVELOPER}, versiune {config.VERSION}")
    print("Tastează 'help' pentru lista de comenzi. Scrie 'ieșire' pentru a opri.\n")

    while True:
        try:
            user_input = input("USER|>").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n La revedere!")
            break
        memory["stats"]["interactions"] += 1
        save_memory(memory)

        if not user_input:
            continue
        low = user_input.lower()
        if low in ["ieșire","exit","quit"]:
            print("Conversație încheiată")
            break
        elif low in ["help","/help"]:
            print(config.HELP_TEXT)
        elif user_input.startswith("skill:"):
            _, data = user_input.split("skill:",1)
            parts = [p.strip() for p in data.split("|")]
            name, desc = parts[0], parts[1] if len(parts)>1 else ""
            steps = [s.strip() for s in parts[2].split(",")] if len(parts)>2 else []
            core.learn_skill(memory, name, desc, steps)
            print(f"Skill '{name}' salvat!")
        elif user_input.startswith("concept:"):
            _, data = user_input.split("concept:",1)
            core.learn_from_text(memory, data.strip())
            print(f"Concept adăugat: '{data.strip()}'")
        elif user_input.startswith("proiect:") or user_input.startswith("task:"):
            _, data = user_input.split(":",1)
            parts = [p.strip() for p in data.split("|")]
            name, desc = parts[0], parts[1] if len(parts)>1 else ""
            goals = [s.strip() for s in parts[2].split(",")] if len(parts)>2 else []
            core.create_project(memory, name, desc, goals)
            print(f"Task '{name}' creat!")
        elif user_input.startswith("progres:"):
            _, data = user_input.split("progres:",1)
            parts = [p.strip() for p in data.split("|")]
            name = parts[0]
            inc = 10
            if len(parts) > 1:
                try:
                    inc = int(parts[1])
                except ValueError:
                    print("Eroare: valoarea pentru progres trebuie să fie un număr întreg.")
                    continue
            project = core.update_project_progress(memory, name, inc)
            if project:
                print(f"Progres task '{name}': {project['progress']}%")
            else:
                print(f"Nu am găsit task-ul '{name}'")
        elif low=="initiate":
            print(cmd_initiate(memory))
        elif low=="status":
            print(cmd_status(memory))
        elif low=="reset_nn":
            print(neural_manager.reset())
        elif low=="/train" or low=="train":
            loss = neural_manager.train()
            print(f"NN antrenat. Loss final: {loss}")
        else:
            print(core.reflect(memory, neural_manager, user_input))
