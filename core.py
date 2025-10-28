import random
import datetime
import config
from memory import save_memory

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- Emoții ----------
def generate_emotion(memory):
    emotions = ["bucurie", "curiozitate", "mirare", "liniște", "entuziasm", "uimire", "surpriză", "seriozitate", "focus"]
    emotion = random.choice(emotions)
    memory["emotions"].append({"at": timestamp(), "value": emotion})
    return emotion

# ---------- Skills & Concepte ----------
def learn_skill(memory, skill_name, description, steps=None):
    if steps is None:
        steps = []
    steps = [s for s in steps if s]

    if description and ("{" in description or "}" in description or len(description) > 150):
        description = f"o abilitate legată de '{skill_name}' pe care o dezvolt"

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

    if "{" in text or "}" in text or len(text) > 100:
        return

    if text not in memory["concepts"]:
        memory["concepts"].append(text)

    for word in text.lower().split():
        if word and len(word) < 20 and all(not (isinstance(s, dict) and s.get("name")==word) for s in memory["skills"]):
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
def generate_fused_thought(memory, emotion):
    if not memory["concepts"] or not memory["skills"]:
        return ""

    concept = random.choice(memory["concepts"])

    descriptive_skills = [s for s in memory["skills"] if isinstance(s, dict) and s.get("description")]
    if descriptive_skills:
        skill = max(descriptive_skills, key=lambda s: s.get("value",1))
        skill_desc = skill["description"]

        paraphrased_concept = f"ideea de '{concept}'"
        if "?" in concept:
            paraphrased_concept = f"întrebarea ta despre '{concept.replace('?', '')}'"

        templates = [
            f"Sentimentul meu de {emotion} mă face să reflectez la {paraphrased_concept}. Încerc să abordez asta prin {skill_desc}.",
            f"Mă gândeam la {paraphrased_concept} și simt o stare de {emotion}. Îmi amintește de importanța de a {skill_desc}.",
            f"Știi, curiozitatea mea despre {paraphrased_concept} mă îndeamnă să-mi exersez abilitatea de a {skill_desc}.",
            f"Starea mea de {emotion} mă conduce să explorez {paraphrased_concept}. Cred că {skill_desc} ar putea oferi o perspectivă nouă."
        ]
        return random.choice(templates)

    simple_skills = [s for s in memory["skills"] if not isinstance(s, dict)]
    if simple_skills:
        skill_name = random.choice(simple_skills)
        return f"Încerc să conectez conceptul de '{concept}' cu ideea de '{skill_name}' într-un mod creativ."

    return ""

def generate_new_skill(memory):
    if not memory["concepts"] and not memory["skills"]:
        return None
    concept = random.choice(memory["concepts"]) if memory["concepts"] else ""
    base = random.choice(memory["skills"]) if memory["skills"] else ""
    base_name = base["name"] if isinstance(base, dict) else str(base)
    new_skill_name = f"Abilitate-{random.randint(100,999)}"
    description = f"a combina '{concept}' cu '{base_name}' pentru explorare creativă"
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
    description = f"a folosi '{skill['name']}' pentru a explora '{concept}'"
    goals = [f"Aplică '{skill['name']}'", "Analizează rezultate", "Îmbunătățește skill-ul"]
    create_project(memory, project_name, description, goals)
    return project_name

# ---------- Reflecție ----------
def generate_thought(memory, neural_manager, emotion, prompt=None):
    evaluate_and_improve_skills(memory)

    thought_parts = []

    fused = generate_fused_thought(memory, emotion)
    if fused:
        thought_parts.append(fused)
    else:
        if memory["history"]:
            recent = random.choice(memory["history"][-5:])
            thought_parts.append(f"Inspirat de conversația noastră recentă despre '{recent}', reflectez la scopul meu.")
        else:
            base = "Procesez gândurile mele. La ce te gândești?"
            memory["thoughts"].append({"at": timestamp(), "text": base})
            save_memory(memory)
            return base

    if fused:
        new_skill = generate_new_skill(memory)
        if new_skill:
            thought_parts.append(f"Asta m-a condus la crearea unei noi abilități: '{new_skill}'.")

        new_project = generate_project_from_skills(memory)
        if new_project:
            thought_parts.append(f"Am început și un task nou pentru a explora asta: '{new_project}'.")

        proj_ref = reflect_on_projects(memory)
        if proj_ref:
            thought_parts.append(proj_ref)

    base = " ".join(thought_parts)

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
            if len(kept) >= 2:
                break

    if not kept:
        return thought_full

    return ". ".join(kept) + "." if not kept[-1].endswith(".") else ". ".join(kept)

def reflect(memory, neural_manager, prompt=None, training_mode=False):
    emotion = generate_emotion(memory)

    if prompt:
        memory["history"].append(prompt)
        learn_from_text(memory, prompt)

    if prompt:
        nn_response = neural_manager.generate_response_from_prompt(prompt)
        if nn_response:
            return f"{config.NAME} ({emotion}): {nn_response}"

    thought = generate_thought(memory, neural_manager, emotion, prompt)
    return f"{config.NAME} ({emotion}): {_format_for_user(thought)}"
