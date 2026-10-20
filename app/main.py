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

app = FastAPI(title="Космические квесты")
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
    "days": 0,   
}

QUESTS = [
    {
        "id": "pirate_lair",
        "title": "Гнездо пиратов",
        "description": "Пиратская база. Крейсер доминаторов. И ты — один против всех.",
        "start_scene": "start",
    },
]

ITEM_NAMES = {
    "droid": "Дроид",
    "drill": "Бур",
    "pickaxe": "Кирка",
    "bomb": "Бомба",
    "timer": "Таймер",
    "detonator": "Детонатор",
    "explosive": "Взрывчатка",
}

@app.post("/start")
def start(player_name: str = Form(...)):
    STATE["player_name"] = player_name.strip() or "Рейнджер"
    return RedirectResponse("/quests", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if not STATE["player_name"]:
        return templates.TemplateResponse("intro.html", {"request": request})
    
    if "quest_id" not in STATE["flags"]:
        return RedirectResponse("/quests", status_code=303)
    scene = get_scene(STATE["current_scene"])

    text = scene["text"].format(player_name=STATE["player_name"])

    choices = [
        {**c, "text": c["text"].format(player_name=STATE["player_name"])}
        for c in visible_choices(scene, STATE)
    ]

    inventory_display = [
        {"name": ITEM_NAMES.get(item, item), "count": count}
        for item, count in STATE["inventory"].items()
    ]

    return templates.TemplateResponse(
        "scene.html",
        {
            "request": request,
            "scene": scene,
            "state": STATE,
            "text": text,
            "choices": choices,
            "inventory_display": inventory_display,
        },
    )

@app.post("/choose")
def choose(choice_index: int = Form(...)):
    next_scene, choice = make_choice(STATE["current_scene"], choice_index, STATE)
    apply_effects(STATE, choice.get("gives"))  

    STATE["history"].append(STATE["current_scene"])
    STATE["current_scene"] = next_scene

    return RedirectResponse("/", status_code=303)

@app.get("/quests", response_class=HTMLResponse)
def quests_list(request: Request):
    if not STATE["player_name"]:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "quests.html",
        {"request": request, "state": STATE, "quests": QUESTS},
    )


@app.post("/quests/select")
def quests_select(quest_id: str = Form(...)):
    quest = next((q for q in QUESTS if q["id"] == quest_id), None)
    if quest is None:
        raise HTTPException(status_code=404, detail="Квест не найден")
    STATE["current_scene"] = quest["start_scene"]
    STATE["flags"]["quest_id"] = quest_id
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
    STATE["days"] = 0
    return RedirectResponse("/", status_code=303)


@app.get("/api/state")
def api_state():
    return STATE