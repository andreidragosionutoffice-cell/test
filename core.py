import random
import datetime
import config
from memory import save_memory

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- Emoții ----------
def generate_emotion(memory):
    emotions = ["bucurie","curiozitate","mirare","liniște","entuziasm","uimire","surpriză","seriozitate","focus"]
    emotion = random.choice(emotions)
    memory["emotions"].append({"at": timestamp(), "value": emotion})
    return emotion

# ---------- Skills & Concepte ----------
def learn_skill(memory, skill_name, description, steps=None):
    if steps is None:
        steps = []
    steps = [s for s in steps if s]
    skill = {"name": skill_name, "description": description, "steps": steps, "value":1}
    for s in memory["skills"]:
        if isinstance(s, dict) and s.get("name") == skill_name:
            s["description"] = description or s["description"]
            if steps:
                s["steps"] = list({*s["steps"], *steps})
            save_memory(memory)
            return
    memory["skills"].append(skill)
    save_memory(memory)

def evaluate_and_improve_skills(memory):
    for skill in memory["skills"]:
        if isinstance(skill, dict):
            matches = [c for c in memory["concepts"] if c.lower() in skill["description"].lower()]
            skill["value"] += max(1, len(matches))
            if random.random() < 0.35:
                skill["steps"].append(f"Pas creativ adăugat la '{skill['name']}'")
    save_memory(memory)

def learn_from_text(memory, text):
    text = text.strip()
    if not text:
        return
    if text not in memory["concepts"]:
        memory["concepts"].append(text)
    for word in text.lower().split():
        if word and all(not (isinstance(s, dict) and s.get("name")==word) for s in memory["skills"]):
            memory["skills"].append(word)
    save_memory(memory)

# ---------- Proiecte ----------
def create_project(memory, name, description, goals=None):
    if goals is None:
        goals = []
    goals = [g for g in goals if g]
    project = {"name": name, "description": description, "goals": goals, "progress": 0}
    memory["projects"].append(project)
    save_memory(memory)
    return project

def update_project_progress(memory, project_name, progress_increment=10):
    for project in memory["projects"]:
        if project["name"] == project_name:
            project["progress"] = min(100, project["progress"] + progress_increment)
            save_memory(memory)
            return project
    return None

def prioritize_projects(memory):
    prioritized = []
    for project in memory["projects"]:
        skills_in_proj = [s for s in memory["skills"] if isinstance(s, dict) and s["name"] in project["description"]]
        skill_value = sum(s.get("value", 1) for s in skills_in_proj) or 1
        score = skill_value * (100 - project["progress"])
        prioritized.append((score, project))
    prioritized.sort(reverse=True, key=lambda x: x[0])
    return [p[1] for p in prioritized]

def select_next_project(memory):
    prioritized = prioritize_projects(memory)
    return prioritized[0] if prioritized else None

def reflect_on_projects(memory):
    project = select_next_project(memory)
    if not project:
        return ""
    return f"Task prioritar: '{project['name']}' ({project['progress']}%). Următorii pași: {', '.join(project['goals']) or 'definește pașii'}."

# ---------- Gânduri ----------
def combine_concepts_and_skills(memory):
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

def generate_new_skill(memory):
    if not memory["concepts"] and not memory["skills"]:
        return None
    concept = random.choice(memory["concepts"]) if memory["concepts"] else ""
    base = random.choice(memory["skills"]) if memory["skills"] else ""
    base_name = base["name"] if isinstance(base, dict) else str(base)
    new_skill_name = f"Skill-{random.randint(100,999)}"
    description = f"Combină '{concept}' cu '{base_name}' pentru explorare creativă."
    steps = [f"Analizează '{concept}'", f"Aplică '{base_name}'", "Observă și rafinează"]
    learn_skill(memory, new_skill_name, description, steps)
    return new_skill_name

def generate_project_from_skills(memory):
    valued = [s for s in memory["skills"] if isinstance(s, dict)]
    if not valued:
        return None
    skill = max(valued, key=lambda s: s.get("value",1))
    project_name = f"Task-{random.randint(100,999)}"
    concept = random.choice(memory["concepts"]) if memory["concepts"] else "necunoscut"
    description = f"Folosesc '{skill['name']}' pentru a explora '{concept}'."
    goals = [f"Aplică '{skill['name']}'", "Analizează rezultate", "Îmbunătățește skill-ul"]
    create_project(memory, project_name, description, goals)
    return project_name

# ---------- Reflecție ----------
def generate_thought(memory, neural_manager, prompt=None):
    evaluate_and_improve_skills(memory)
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
    fused = combine_concepts_and_skills(memory)
    if fused:
        base += f" {fused}"
    new_skill = generate_new_skill(memory)
    if new_skill:
        base += f" Am creat un skill nou: '{new_skill}'."
    new_project = generate_project_from_skills(memory)
    if new_project:
        base += f" Am pornit task-ul: '{new_project}'."
    proj_ref = reflect_on_projects(memory)
    if proj_ref:
        base += f" {proj_ref}"
    loss = neural_manager.train()
    base += f" [NN loss: {loss}]"
    memory["thoughts"].append({"at": timestamp(), "text": base})
    save_memory(memory)
    return base

def _format_for_user(thought_full):
    if config.SHOW_DEBUG:
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

def reflect(memory, neural_manager, prompt=None, training_mode=False):
    emotion = generate_emotion(memory)
    if prompt:
        memory["history"].append(prompt)
        learn_from_text(memory, prompt)
        thought = generate_thought(memory, neural_manager, prompt)
        return f"{config.NAME} ({emotion}): {_format_for_user(thought)}"
    else:
        thought = generate_thought(memory, neural_manager)
        return f"{config.NAME} ({emotion}): {_format_for_user(thought)}"
