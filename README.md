# Space Rangers Quest — «Гнездо пиратов»

Текстовый квест на веб-странице по мотивам игры «Космические рейнджеры 2».
Пользователь проходит сцены, делает выбор, прогресс сохраняется в cookie.

## 🎮 Что умеет

- Показывает сцену с текстом и вариантами действий.
- Обрабатывает выбор и переходит к следующей сцене.
- Считает уровень доверия Кацапа в зависимости от решений.
- Сохраняет прогресс между сессиями (cookie на 7 дней).
- Позволяет начать заново одной кнопкой.

## 🛠️ Стек

- **Python 3.9+**
- **FastAPI** — веб-фреймворк
- **Jinja2** — HTML-шаблоны
- **itsdangerous** — подпись cookie
- **pytest + Playwright + httpx** — тесты
- **pytest-cov** — покрытие

## 📁 Структура

space-rangers-quest/
├── app/
│   ├── main.py              # FastAPI, роуты
│   ├── scenes.py            # сцены квеста
│   ├── templates/           # HTML-шаблоны
│   └── static/css/          # стили
├── tests/
│   ├── unit/                # тесты чистой логики
│   ├── api/                 # тесты эндпоинтов
│   └── ui/                  # тесты через браузер
├── pytest.ini
├── requirements.txt
└── README.md

## 🚀 Установка

```bash
git clone https://github.com/your-username/space-rangers-quest.git
cd space-rangers-quest

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium