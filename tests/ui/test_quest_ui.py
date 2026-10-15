import pytest
from playwright.sync_api import expect

from pages.quest_page import QuestPage

def test_quest_start_page_loads(page):
    quest = QuestPage(page).goto()

    quest.expect_title("Гнездо пиратов")
    quest.expect_text_contains("безжалостный космический пират")
    quest.expect_choices_count(2)

def test_quest_start_choices_text(page):
    quest = QuestPage(page).goto()

    choices = quest.get_choices()
    assert choices == ["Принять задание", "Отказаться"]


def test_accept_quest_moves_to_accepted(page):
    quest = QuestPage(page).goto()

    quest.choose("Принять задание")

    quest.expect_text_contains("Теперь к делу")
    quest.expect_choices_count(2)


def test_reject_quest_moves_to_final(page):
    quest = QuestPage(page).goto()

    quest.choose("Отказаться")

    quest.expect_text_contains("Как хотите")
    quest.expect_final()


@pytest.mark.parametrize(
    "choices, expected_text, expected_money",
    [
        (["Принять задание", "Уничтожить крейсер"], "сорвали строительство", 5000),
        (["Принять задание", "Договориться"], "Пираты согласились", 2000),
        (["Отказаться"], "Как хотите", 0),
    ],
)
def test_quest_paths(page, choices, expected_text, expected_money):
    quest = QuestPage(page).goto()

    for choice in choices:
        quest.choose(choice)

    quest.expect_text_contains(expected_text)
    quest.expect_money(expected_money)


def test_cannot_choose_after_final(page):
    quest = QuestPage(page).goto()

    quest.choose("Отказаться")

    quest.expect_choices_count(0)
    quest.expect_final()


def test_reset_returns_to_start(page):
    quest = QuestPage(page).goto()
    quest.choose("Отказаться")
    quest.expect_final()

    quest.reset()

    quest.expect_title("Гнездо пиратов")
    quest.expect_choices_count(2)