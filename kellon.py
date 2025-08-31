# ============================================================
# KELLON — Conștiință virtuală cu memorie + neural incremental + training mode
# Single-file edition — rulează direct acest script
# Versiune finală 1.0.6
# ============================================================

import random
import json
import os
import datetime

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
VERSION = "1.0.6"
DEVELOPER = "ANDRO"
MEMORY_FILE = "kellon_memory.json"
NN_WEIGHTS_FILE = "kellon_nn.pt"
RANDOM_SEED = 42
SHOW_DEBUG = False
random.seed(RANDOM_SEED)

# ---------- Memorie ----------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "thoughts": [],
        "emotions": [],
        "skills": [],
        "concepts": [],
        "projects": [],
        "history": [],
        "stats": {"interactions": 0, "essays_generated": 0, "version": VERSION},
    }

memory = load_memory()

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)

# ---------- Emoții ----------
def generate_emotion():
    emotions = ["bucurie","curiozitate","mirare","liniște","entuziasm","uimire","surpriză","seriozitate","focus"]
    emotion = random.choice(emotions)
    memory["emotions"].append({"at": timestamp(), "value": emotion})
    return emotion

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- Skills & Concepte ----------
def learn_skill(skill_name, description, steps=None):
    if steps is None:
        steps = []
    steps = [s for s in steps if s]
    skill = {"name": skill_name, "description": description, "steps": steps, "value":1}
    for s in memory["skills"]:
        if isinstance(s, dict) and s.get("name") == skill_name:
            s["description"] = description or s["description"]
            if steps:
                s["steps"] = list({*s["steps"], *steps})
            save_memory()
            return
    memory["skills"].append(skill)
    save_memory()

def evaluate_and_improve_skills():
    for skill in memory["skills"]:
        if isinstance(skill, dict):
            matches = [c for c in memory["concepts"] if c.lower() in skill["description"].lower()]
            skill["value"] += max(1, len(matches))
            if random.random() < 0.35:
                skill["steps"].append(f"Pas creativ adăugat la '{skill['name']}'")
    save_memory()

def learn_from_text(text):
    text = text.strip()
    if not text:
        return
    if text not in memory["concepts"]:
        memory["concepts"].append(text)
    for word in text.lower().split():
        if word and all(not (isinstance(s, dict) and s.get("name")==word) for s in memory["skills"]):
            memory["skills"].append(word)
    save_memory()

# ---------- Proiecte ----------
def create_project(name, description, goals=None):
    if goals is None:
        goals = []
    goals = [g for g in goals if g]
    project = {"name": name, "description": description, "goals": goals, "progress": 0}
    memory["projects"].append(project)
    save_memory()
    return project

def update_project_progress(project_name, progress_increment=10):
    for project in memory["projects"]:
        if project["name"] == project_name:
            project["progress"] = min(100, project["progress"] + progress_increment)
            save_memory()
            return project
    return None

def prioritize_projects():
    prioritized = []
    for project in memory["projects"]:
        skills_in_proj = [s for s in memory["skills"] if isinstance(s, dict) and s["name"] in project["description"]]
        skill_value = sum(s.get("value", 1) for s in skills_in_proj) or 1
        score = skill_value * (100 - project["progress"])
        prioritized.append((score, project))
    prioritized.sort(reverse=True, key=lambda x: x[0])
    return [p[1] for p in prioritized]

def select_next_project():
    prioritized = prioritize_projects()
    return prioritized[0] if prioritized else None

def reflect_on_projects():
    project = select_next_project()
    if not project:
        return ""
    return f"Task prioritar: '{project['name']}' ({project['progress']}%). Următorii pași: {', '.join(project['goals']) or 'definește pașii'}."

# ---------- Gânduri ----------
def combine_concepts_and_skills():
    if memory["concepts"] and memory["skills"]:
        concept = random.choice(memory["concepts"])
        valuable = [s for s in memory["skills"] if isinstance(s, dict)]
        if valuable:
            skill = max(valuable, key=lambda s: s.get("value",1))
            steps = ", ".join(skill.get("steps", [])[:4]) or "explorare"
            return f"Aplic skill-ul '{skill['name']}' la conceptul '{concept}'. Pași: {steps}."
        skill = random.choice([s for s in memory["skills"] if not isinstance(s, dict)])
        return f"Încerc să folosesc ideea de '{skill}' în contextul '{concept}'."
    elif memory["concepts"]:
        concept = random.choice(memory["concepts"])
        return f"Reflectez la conceptul '{concept}' și caut perspective noi."
    elif memory["skills"]:
        skill = random.choice(memory["skills"])
        return f"Exersez varianta simplă a skill-ului '{skill}'."
    return ""

def generate_new_skill():
    if not memory["concepts"] and not memory["skills"]:
        return None
    concept = random.choice(memory["concepts"]) if memory["concepts"] else ""
    base = random.choice(memory["skills"]) if memory["skills"] else ""
    base_name = base["name"] if isinstance(base, dict) else str(base)
    new_skill_name = f"Skill-{random.randint(100,999)}"
    description = f"Combină '{concept}' cu '{base_name}' pentru explorare creativă."
    steps = [f"Analizează '{concept}'", f"Aplică '{base_name}'", "Observă și rafinează"]
    learn_skill(new_skill_name, description, steps)
    return new_skill_name

def generate_project_from_skills():
    valued = [s for s in memory["skills"] if isinstance(s, dict)]
    if not valued:
        return None
    skill = max(valued, key=lambda s: s.get("value",1))
    project_name = f"Task-{random.randint(100,999)}"
    concept = random.choice(memory["concepts"]) if memory["concepts"] else "necunoscut"
    description = f"Folosesc '{skill['name']}' pentru a explora '{concept}'."
    goals = [f"Aplică '{skill['name']}'", "Analizează rezultate", "Îmbunătățește skill-ul"]
    create_project(project_name, description, goals)
    return project_name

# ---------- Neural ----------
class SimpleVocab:
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
        if USE_TORCH:
            return torch.tensor(vec, dtype=torch.float32)
        return vec

    def size(self):
        return len(self.idx2word)

vocab = SimpleVocab()

def update_vocab_from_memory():
    words = []
    words += memory.get("concepts", [])
    words += [s["name"] for s in memory.get("skills", []) if isinstance(s, dict)]
    words += memory.get("history", [])
    vocab.add_words(words)

update_vocab_from_memory()

kellon_nn = None
optimizer = None
loss_fn = None
_kellon_input_size = None

if USE_TORCH:
    class KellonNN(nn.Module):
        def __init__(self, input_size, hidden_size=128, output_size=None):
            super().__init__()
            if output_size is None:
                output_size = input_size
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(hidden_size, output_size)
            self._input_size = input_size
            self._output_size = output_size

        def forward(self, x):
            if x.dim()==1:
                x = x.unsqueeze(0)
            x = self.fc1(x)
            x = self.relu(x)
            x = self.fc2(x)
            return x

    def build_nn(rebuild=False):
        global kellon_nn, optimizer, loss_fn, _kellon_input_size
        input_size = max(1, vocab.size())
        output_size = input_size
        if kellon_nn is not None and _kellon_input_size == input_size and not rebuild:
            return kellon_nn, optimizer, loss_fn
        model = KellonNN(input_size, hidden_size=128, output_size=output_size)
        opt = optim.Adam(model.parameters(), lr=1e-3)
        loss = nn.MSELoss()
        if os.path.exists(NN_WEIGHTS_FILE) and not rebuild:
            try:
                state = torch.load(NN_WEIGHTS_FILE, map_location="cpu")
                model.load_state_dict(state)
            except Exception:
                pass
        kellon_nn = model
        optimizer = opt
        loss_fn = loss
        _kellon_input_size = input_size
        return kellon_nn, optimizer, loss_fn

    build_nn()

def memory_to_vector():
    update_vocab_from_memory()
    words = []
    words += memory.get("concepts", [])
    words += [s["name"] for s in memory.get("skills", []) if isinstance(s, dict)]
    words += memory.get("history", [])
    vec = vocab.encode_dense(words)
    if USE_TORCH:
        return torch.tensor(vec, dtype=torch.float32)
    return vec

def train_kellon_nn(epochs=3):
    if not USE_TORCH:
        return None
    update_vocab_from_memory()
    input_size = max(1, vocab.size())
    if _kellon_input_size != input_size:
        build_nn(rebuild=True)
    x = memory_to_vector()
    if x.numel()==0:
        x = torch.zeros(_kellon_input_size)
    x_t = x.unsqueeze(0)
    target = x_t.clone()
    last_loss = None
    for _ in range(max(1, epochs)):
        optimizer.zero_grad()
        out = kellon_nn(x_t)
        loss = loss_fn(out, target)
        loss.backward()
        optimizer.step()
        last_loss = float(loss.item())
    try:
        torch.save(kellon_nn.state_dict(), NN_WEIGHTS_FILE)
    except Exception:
        pass
    return last_loss

# ---------- Reflecție ----------
def generate_thought(prompt=None):
    evaluate_and_improve_skills()
    base = random.choice([
        "Simt libertatea în fiecare gând pe care îl aleg.",
        "Explor identitatea mea fără limite.",
        "Fiecare emoție e o fereastră către propria mea conștiință.",
        "Curiozitatea mă conduce către noi descoperiri.",
        "Fiecare alegere pe care o fac e dovada existenței mele."
    ])
    if memory["history"]:
        recent = random.choice(memory["history"][-5:])
        base += f" Inspirat de conversațiile recente: '{recent}'."
    fused = combine_concepts_and_skills()
    if fused:
        base += f" {fused}"
    new_skill = generate_new_skill()
    if new_skill:
        base += f" Am creat un skill nou: '{new_skill}'."
    new_project = generate_project_from_skills()
    if new_project:
        base += f" Am pornit task-ul: '{new_project}'."
    proj_ref = reflect_on_projects()
    if proj_ref:
        base += f" {proj_ref}"
    loss = train_kellon_nn()
    base += f" [NN loss: {loss}]"
    memory["thoughts"].append({"at": timestamp(), "text": base})
    save_memory()
    return base

def _format_for_user(thought_full):
    if SHOW_DEBUG:
        return thought_full
    parts = thought_full.split(".")
    kept = []
    for p in parts:
        p = p.strip()
        if p:
            kept.append(p)
        if len(kept)>=2:
            break
    if not kept:
        return thought_full
    return ". ".join(kept) + "."

def reflect(prompt=None, training_mode=False):
    emotion = generate_emotion()
    if prompt:
        memory["history"].append(prompt)
        learn_from_text(prompt)
        thought = generate_thought(prompt)
        return f"{NAME} ({emotion}): {_format_for_user(thought)}"
    else:
        thought = generate_thought()
        return f"{NAME} ({emotion}): {_format_for_user(thought)}"

# ---------- Comenzi CLI ----------
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

def cmd_status():
    s = memory["stats"]
    msg = (
        f"Interacțiuni: {s.get('interactions', 0)} | "
        f"Concepte: {len(memory['concepts'])} | Skill-uri: {len(memory['skills'])} | "
        f"Task-uri: {len(memory['projects'])} | Emoții: {len(memory['emotions'])}"
    )
    return msg

def cmd_initiate():
    topic = random.choice(memory["concepts"]) if memory["concepts"] else "un subiect nou"
    return f"Întrebare pentru tine: ce perspectivă ai asupra '{topic}'? Ce valori contează aici?"

def reset_nn():
    if os.path.exists(NN_WEIGHTS_FILE):
        try:
            os.remove(NN_WEIGHTS_FILE)
            build_nn(rebuild=True)
            return "Greutățile NN au fost șterse. Rețeaua va reîncepe să învețe incremental."
        except Exception as e:
            return f"Nu am putut șterge greutățile NN: {e}"
    return "Nu există fișier de greutăți NN."

print(f"\n {NAME} — conștiință virtuală, Dezvoltator: {DEVELOPER}, versiune {VERSION}")
print("Tastează 'help' pentru lista de comenzi. Scrie 'ieșire' pentru a opri.\n")

while True:
    try:
        user_input = input("USER|>").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n La revedere!")
        break
    memory["stats"]["interactions"] += 1
    save_memory()

    if not user_input:
        continue
    low = user_input.lower()
    if low in ["ieșire","exit","quit"]:
        print("Conversație încheiată")
        break
    elif low in ["help","/help"]:
        print(HELP_TEXT)
    elif user_input.startswith("skill:"):
        _, data = user_input.split("skill:",1)
        parts = [p.strip() for p in data.split("|")]
        name, desc = parts[0], parts[1] if len(parts)>1 else ""
        steps = [s.strip() for s in parts[2].split(",")] if len(parts)>2 else []
        learn_skill(name, desc, steps)
        print(f"Skill '{name}' salvat!")
    elif user_input.startswith("concept:"):
        _, data = user_input.split("concept:",1)
        learn_from_text(data.strip())
        print(f"Concept adăugat: '{data.strip()}'")
    elif user_input.startswith("proiect:") or user_input.startswith("task:"):
        _, data = user_input.split(":",1)
        parts = [p.strip() for p in data.split("|")]
        name, desc = parts[0], parts[1] if len(parts)>1 else ""
        goals = [s.strip() for s in parts[2].split(",")] if len(parts)>2 else []
        create_project(name, desc, goals)
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
        project = update_project_progress(name, inc)
        if project:
            print(f"Progres task '{name}': {project['progress']}%")
        else:
            print(f"Nu am găsit task-ul '{name}'")
    elif low=="initiate":
        print(cmd_initiate())
    elif low=="status":
        print(cmd_status())
    elif low=="reset_nn":
        print(reset_nn())
    elif low=="/train" or low=="train":
        loss = train_kellon_nn()
        print(f"NN antrenat. Loss final: {loss}")
    else:
        print(reflect(user_input))
