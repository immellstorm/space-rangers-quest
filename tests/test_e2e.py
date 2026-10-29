import pytest

pytestmark = pytest.mark.e2e


def test_server_is_up(live_server, page):
    page.goto(f"{live_server}/login")
    assert page.url.endswith("/login")
    assert "PIN" in page.content()

def test_browser_opens_example(page):
    page.goto("https://example.com")
    assert "Example Domain" in page.title()


def test_full_login_flow_reaches_game(live_server, page):
    page.goto(f"{live_server}/login")
    assert page.url.endswith("/login")

    page.fill('input[name="username"]', "newplayer")
    page.fill('input[name="pin"]', "5678")
    page.get_by_role("button", name="Войти").click()

    assert page.url.endswith("/")
    page.fill('input[name="player_name"]', "Новичок")
    page.get_by_role("button", name="Начать приключение").click()

    assert "/quests" in page.url
    page.get_by_role("button").first.click()

    assert page.url.endswith("/")

    title = page.locator("#quest-title").text_content().strip()
    assert title == "Гнездо пиратов"

    text = page.locator("#quest-text").text_content()
    assert "Новичок" in text


def test_choice_refuse_shows_rejected_scene(game_page):
    game_page.get_by_role("button", name="Я отказываюсь от этого задания").click()
    assert "Ну и дурак" in game_page.locator("#quest-text").text_content()

def test_accept_quest_updates_money_and_days(game_page, page):
    game_page.get_by_role("button", name="Я берусь за это задание").click()
    page.get_by_role("button", name="Искать Русмана").click()
    page.get_by_role("button", name="У меня нет вопросов. Давай приступим к делу").click()


    money_line = game_page.locator("#money-line").text_content()
    days_line = game_page.locator("#days-line").text_content()

    assert "1000" in money_line, f"money line: {money_line!r}"
    assert "3" in days_line, f"days line: {days_line!r}"