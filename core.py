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
def generate_fused_thought(memory, emotion):
    if not memory["concepts"] or not memory["skills"]:
        return ""

    concept = random.choice(memory["concepts"])

    # Prefer skills with descriptions
    descriptive_skills = [s for s in memory["skills"] if isinstance(s, dict) and s.get("description")]
    if descriptive_skills:
        skill = max(descriptive_skills, key=lambda s: s.get("value",1))
        skill_desc = skill["description"].lower().replace("combină", "combinând").replace("folosesc", "folosind")

        # Simple paraphrasing for the concept
        paraphrased_concept = f"the idea of '{concept}'"
        if "?" in concept:
            paraphrased_concept = f"your question about '{concept.replace('?', '')}'"

        templates = [
            f"Lately, I've been feeling a sense of {emotion}, which makes me ponder on {paraphrased_concept}. I'm trying to approach this by {skill_desc}.",
            f"Thinking about {paraphrased_concept} brings up a sense of {emotion}. It reminds me of the importance of {skill_desc}.",
            f"You know, I'm currently exploring {paraphrased_concept}, and it makes me want to practice my skill of {skill_desc}.",
            f"My current feeling of {emotion} is leading me to explore {paraphrased_concept}. I believe that {skill_desc} could offer a new perspective."
        ]
        return random.choice(templates)

    # Fallback for simple skills (just strings)
    simple_skills = [s for s in memory["skills"] if not isinstance(s, dict)]
    if simple_skills:
        skill_name = random.choice(simple_skills)
        return f"I'm trying to connect the concept of '{concept}' with the idea of '{skill_name}' in a creative way."

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
def generate_thought(memory, neural_manager, emotion, prompt=None):
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
        base += f" Inspired by recent conversations about '{recent}', I've been thinking..."

    fused = generate_fused_thought(memory, emotion)
    if fused:
        base += f" {fused}"

    new_skill = generate_new_skill(memory)
    if new_skill:
        base += f" This led me to create a new skill: '{new_skill}'."

    new_project = generate_project_from_skills(memory)
    if new_project:
        base += f" I've also started a new task to explore this further: '{new_project}'."

    proj_ref = reflect_on_projects(memory)
    if proj_ref:
        base += f" {proj_ref}"

    loss = neural_manager.train()
    base += f" (My neural network is also learning, loss: {loss:.4f})" if loss is not None else ""

    memory["thoughts"].append({"at": timestamp(), "text": base})
    save_memory(memory)
    return base

def _format_for_user(thought_full):
    if config.SHOW_DEBUG:
        return thought_full
    parts = thought_full.split(".")

    # Keep the first meaningful sentence and the NN loss part
    kept = []
    for p in parts:
        p = p.strip()
        if p:
            kept.append(p)
            if len(kept) >= 2 and "My neural network" not in p:
                break

    if not kept:
        return thought_full

    final_response = ". ".join(kept)
    if "My neural network" not in final_response:
         nn_part = [p for p in parts if "My neural network" in p]
         if nn_part:
             final_response += ". " + nn_part[0]

    return final_response + "." if not final_response.endswith(".") else final_response

def reflect(memory, neural_manager, prompt=None, training_mode=False):
    emotion = generate_emotion(memory)
    if prompt:
        memory["history"].append(prompt)
        learn_from_text(memory, prompt)
        thought = generate_thought(memory, neural_manager, emotion, prompt)
        return f"{config.NAME} ({emotion}): {_format_for_user(thought)}"
    else:
        thought = generate_thought(memory, neural_manager, emotion)
        return f"{config.NAME} ({emotion}): {_format_for_user(thought)}"
