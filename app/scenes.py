SCENES = {
    "start": {
        "title": "Гнездо пиратов",
        "text": (
            "Вы, Рейнджер, безжалостный космический пират. "
            "Ваш корабль дрейфует у границ сектора Пеленгов. "
            "На радаре — пиратская база, где строят крейсер Доминаторов."
        ),
        "choices": [
            {"text": "Принять задание", "next": "accepted"},
            {"text": "Отказаться", "next": "rejected"},
        ],
    },
    "accepted": {
        "title": "Гнездо пиратов",
        "text": (
            "Теперь к делу. Пираты согласны заплатить, "
            "если вы уничтожите крейсер. Но есть и другой путь — "
            "договориться с ними о союзе."
        ),
        "choices": [
            {"text": "Уничтожить крейсер", "next": "destroy"},
            {"text": "Договориться", "next": "negotiate"},
        ],
    },
    "destroy": {
        "title": "Гнездо пиратов",
        "text": (
            "Вы успешно сорвали строительство крейсера! "
            "Пираты заплатили 5000 кредитов. "
            "Пеленги недовольны."
        ),
        "choices": [],
        "reward": {"money": 5000, "relations": {"Peleng": -10}},
    },
    "negotiate": {
        "title": "Гнездо пиратов",
        "text": (
            "Пираты согласились на союз. "
            "Вы получили 2000 кредитов и поддержку в будущем. "
            "Пеленги оценили дипломатию."
        ),
        "choices": [],
        "reward": {"money": 2000, "relations": {"Peleng": 5}},
    },
    "rejected": {
        "title": "Гнездо пиратов",
        "text": "Как хотите. В другой раз.",
        "choices": [],
        "reward": {"money": 0, "relations": {}},
    },
}


def get_scene(name: str) -> dict:
    if name not in SCENES:
        raise KeyError(f"Сцена '{name}' не найдена")
    return SCENES[name]


def make_choice(current: str, choice_index: int) -> str:
    scene = get_scene(current)
    if not scene["choices"]:
        raise ValueError(f"Сцена '{current}' — финальная, выбор невозможен")
    if choice_index < 0 or choice_index >= len(scene["choices"]):
        raise IndexError(f"Неверный индекс выбора: {choice_index}")
    return scene["choices"][choice_index]["next"]