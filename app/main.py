from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.scenes import (
    SCENES,
    get_scene,
    make_choice,
    visible_choices,
    apply_effects,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Космические Рейнджеры 2")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


STATE = {
    "player_name": "",
    "current_scene": "start",
    "money": 0,
    "relations": {},
    "history": [],
    "inventory": {},
    "trust": {},
    "flags": {},    
}

@app.post("/start")
def start(player_name: str = Form(...)):
    STATE["player_name"] = player_name.strip() or "Рейнджер"
    return RedirectResponse("/", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if not STATE["player_name"]:
        return templates.TemplateResponse("intro.html", {"request": request})
    scene = get_scene(STATE["current_scene"])
    text = scene["text"].format(player_name=STATE["player_name"])
    choices = [
        {**c, "text": c["text"].format(player_name=STATE["player_name"])}
        for c in visible_choices(scene, STATE)
    ]
    return templates.TemplateResponse(
        "scene.html",
        {
            "request": request,
            "scene": scene,
            "state": STATE,
            "text": text,
            "choices": choices,
        },
    )

@app.post("/choose")
def choose(choice_index: int = Form(...)):
    next_scene, choice = make_choice(STATE["current_scene"], choice_index, STATE)
    apply_effects(STATE, choice.get("gives"))        # ← ставим флаги, списываем деньги

    STATE["history"].append(STATE["current_scene"])
    STATE["current_scene"] = next_scene

    scene = get_scene(next_scene)
    if scene.get("reward"):
        STATE["money"] += scene["reward"].get("money", 0)
        for race, delta in scene["reward"].get("relations", {}).items():
            STATE["relations"][race] = STATE["relations"].get(race, 0) + delta

    return RedirectResponse("/", status_code=303)


@app.post("/reset")
def reset():
    STATE["player_name"] = ""
    STATE["current_scene"] = "start"
    STATE["money"] = 0
    STATE["relations"] = {}
    STATE["history"] = []
    STATE["inventory"] = {}
    STATE["trust"] = {}
    STATE["flags"] = {}
    return RedirectResponse("/", status_code=303)


@app.get("/api/state")
def api_state():
    return STATE