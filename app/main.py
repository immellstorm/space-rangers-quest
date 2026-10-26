import os
from pathlib import Path
import sys

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.images import get_scene_image
from app.scenes import (
    SCENES, get_scene, make_choice, visible_choices, apply_effects,
)
from app.sessions import load_state, save_state, reset_state
from app.glossary import GLOSSARY
from app.auth import init_db, login_or_create, connect

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "kosmicheskie-rendzhery-secret-2024-x7k9"
IS_PROD = True

app = FastAPI(title="Космические квесты")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 30,
    https_only=IS_PROD,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

init_db()

QUESTS = [
    {
        "id": "pirate_lair",
        "title": "Гнездо пиратов",
        "description": "Три дня, чтобы стать своим среди чужих — втереться в доверие, выведать тайну и уйти живым",
        "start_scene": "start",
    },
]

ITEM_NAMES = {
    "droid": "Дроид", "drill": "Бур", "pickaxe": "Кирка", "bomb": "Бомба",
    "timer": "Таймер", "detonator": "Детонатор", "explosive": "Взрывчатка",
    "photo": "Фотография с пеленгессами", "card": "Магнитная карта к кладовке",
    "boots": "Сапоги из мультипластика", "spirt": "99%-й спирт",
    "flowers": "Болотные водоросли", "swarm_water": "Болотная жижа",
    "water": "Ведро воды", "sandy": "Песок", "ryaska": "Стакан Ряски",
    "acid": "Кислота", "dark_drink": "Пиво «Махпельское тёмное»",
    "vtekilla": "Бутылка втыкиллы", "guanava": "Бутылка гуанавы",
    "nucker_malok": "Банка малокского ядерного",
    "access_card_special": "Карта допуска на спецуровень",
}

FINAL_SCENES = {
    "rusman_and_cancel", "kill_katsap", "kill_katsap_nucker_malok",
    "teleport_666h", "get_10000", "base_angar_fight_kill",
    "katsap_drive", "plan_a", "plan_c",
    "mission_end_secret", "mission_end_ok", "mission_end_fail",
    "mission_end_timeout",
}

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("auth.html", {
        "request": request, "error": None,
    })


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    pin: str = Form(...),
):
    user_id = login_or_create(username, pin)
    if user_id is None:
        return templates.TemplateResponse("auth.html", {
            "request": request,
            "error": "Неверное имя или PIN",
        }, status_code=400)
    request.session["user_id"] = user_id
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)

    state = load_state(user_id)

    if not state["player_name"]:
        return templates.TemplateResponse("intro.html", {
            "request": request,
            "username": _get_username(user_id),
        })

    if "quest_id" not in state["flags"]:
        return RedirectResponse("/quests", status_code=303)

    if (
        state["flags"].get("timer_started")
        and state["days"] <= 0
        and state["current_scene"] not in FINAL_SCENES
        and state["current_scene"] != "go_sleep"
    ):
        state["current_scene"] = "mission_end_timeout"
        save_state(user_id, state)

    scene = get_scene(state["current_scene"])
    text = scene["text"].format(
        player_name=state["player_name"],
        days=state["days"],
        money=state["money"],
    )
    choices = [
        {**c, "text": c["text"].format(player_name=state["player_name"])}
        for c in visible_choices(scene, state)
    ]
    inventory_display = [
        {"name": ITEM_NAMES.get(item, item), "count": count}
        for item, count in state["inventory"].items()
    ]

    flags = state["flags"]
    brew_lines, total_ml = [], 0
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

    return templates.TemplateResponse("scene.html", {
        "request": request, "scene": scene, "state": state,
        "text": text, "choices": choices,
        "inventory_display": inventory_display,
        "brew_lines": brew_lines,
        "scene_image": get_scene_image(state["current_scene"]),
        "username": _get_username(user_id),
    })


@app.post("/start")
def start(request: Request, player_name: str = Form(...)):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)
    state = load_state(user_id)
    state["player_name"] = player_name.strip() or "Рейнджер"
    save_state(user_id, state)
    return RedirectResponse("/quests", status_code=303)


@app.post("/choose")
def choose(request: Request, choice_index: int = Form(...)):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)

    state = load_state(user_id)

    if (
        state["flags"].get("timer_started")
        and state["days"] <= 0
        and state["current_scene"] not in FINAL_SCENES
        and state["current_scene"] != "go_sleep"
    ):
        state["current_scene"] = "mission_end_timeout"
        save_state(user_id, state)
        return RedirectResponse("/", status_code=303)

    next_scene, choice = make_choice(
        state["current_scene"], choice_index, state
    )
    apply_effects(state, choice.get("gives"))
    state["history"].append(state["current_scene"])
    state["current_scene"] = next_scene
    save_state(user_id, state)
    return RedirectResponse("/", status_code=303)


@app.get("/quests", response_class=HTMLResponse)
def quests_list(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)
    state = load_state(user_id)
    if not state["player_name"]:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("quests.html", {
        "request": request, "state": state, "quests": QUESTS,
    })


@app.post("/quests/select")
def quests_select(request: Request, quest_id: str = Form(...)):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)
    quest = next((q for q in QUESTS if q["id"] == quest_id), None)
    if quest is None:
        raise HTTPException(status_code=404, detail="Квест не найден")
    state = load_state(user_id)
    state["current_scene"] = quest["start_scene"]
    state["flags"]["quest_id"] = quest_id
    save_state(user_id, state)
    return RedirectResponse("/", status_code=303)


@app.post("/reset")
def reset(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse("/login", status_code=303)
    reset_state(user_id)
    return RedirectResponse("/", status_code=303)


@app.get("/api/state")
def api_state(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return load_state(user_id)


def _get_username(user_id: int) -> str:
    with connect() as conn:
        row = conn.execute(
            "SELECT username FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return row["username"] if row else "Рейнджер"

@app.get("/glossary", response_class=HTMLResponse)
def glossary_page(request: Request):
    by_category = {}
    for key, item in GLOSSARY.items():
        by_category.setdefault(item["category"], []).append((key, item))
    for cat in by_category:
        by_category[cat].sort(key=lambda kv: kv[1]["title"])

    return templates.TemplateResponse("glossary.html", {
        "request": request,
        "by_category": by_category,
        "categories_order": ["Расы", "Персонажи", "Планеты", "Звёздные системы",
                             "Организации"],
    })