from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form, Request, HTTPException

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
    "photo": "Фотография с пеленгессами",
    "card": "Магнитная карта к кладовке",
    "boots": "Сапоги из мультипластика",
    "spirt": "99%-й спирт",
    "flowers" : "Болотные водоросли",
    "swarm_water" : "Болотная жижа",
    "water" : "Ведро воды",
    "sandy" : "Песок", 
    "ryaska" : "Стакан Ряски",
    "acid" : "Кислота",
    "dark_drink": "Пиво «Махпельское тёмное»",
    "vtekilla": "Бутылка втыкиллы",
    "guanava": "Бутылка гуанавы",
    "nucker_malok": "Банка малокского ядерного",
    "access_card_special": "Карта допуска на спецуровень",
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

    text = scene["text"].format(
        player_name=STATE["player_name"],
        days=STATE["days"],
        money=STATE["money"],
    )

    choices = [
        {**c, "text": c["text"].format(player_name=STATE["player_name"])}
        for c in visible_choices(scene, STATE)
    ]

    inventory_display = [
        {"name": ITEM_NAMES.get(item, item), "count": count}
        for item, count in STATE["inventory"].items()
    ]

    flags = STATE["flags"]
    brew_lines = []
    total_ml = 0

    if flags.get("added_sandy"):
        brew_lines.append(f"Песка в напитке: {flags.get('sandy_g', 0)} г")

    if flags.get("added_flowers"):
        brew_lines.append(f"Водорослей в напитке: {flags.get('flowers_g', 0)} г")

    if flags.get("added_acid"):
        ml = flags.get("acid_ml", 0)
        brew_lines.append(f"Кислоты в напитке: {ml} мл")
        total_ml += ml

    if flags.get("added_spirt"):
        ml = flags.get("spirt_ml", 0)
        brew_lines.append(f"Спирта в напитке: {ml} мл")
        total_ml += ml

    if flags.get("added_water"):
        ml = flags.get("water_ml", 0)
        brew_lines.append(f"Воды в напитке: {ml} мл")
        total_ml += ml

    if flags.get("added_swarm_water"):
        ml = flags.get("swarm_water_ml", 0)
        brew_lines.append(f"Болотной жижи: {ml} мл")
        total_ml += ml

    if brew_lines:
        total_ml += flags.get("sandy_g", 0) + flags.get("flowers_g", 0)
        brew_lines.append(f"Стакан заполнен на {total_ml} мл")

    return templates.TemplateResponse(
        "scene.html",
        {
            "request": request,
            "scene": scene,
            "state": STATE,
            "text": text,
            "choices": choices,
            "inventory_display": inventory_display,
            "brew_lines": brew_lines,
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