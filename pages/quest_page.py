
from playwright.sync_api import Page, expect


class QuestPage:
    URL = "/"

    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator("#quest-title")
        self.text = page.locator("#quest-text")
        self.choices = page.locator("#choices button")
        self.final_block = page.locator("#final")
        self.money = page.locator("#money-line")
        self.days = page.locator("#days-line")


    def goto(self) -> "QuestPage":
        self.page.goto(self.URL)
        return self

    def choose(self, choice_text: str) -> "QuestPage":
        self.page.get_by_role("button", name=choice_text).click()
        return self

    def reset(self) -> "QuestPage":
        self.page.get_by_role("button", name="Начать заново").click()
        return self

    def get_title(self) -> str:
        return (self.title.text_content() or "").strip()

    def get_text(self) -> str:
        return (self.text.text_content() or "").strip()

    def get_money(self) -> str:
         return (self.money.text_content() or "").strip()

    def get_days(self) -> int:
        text = (self.days.text_content() or "").strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits or 0)

    def get_choices(self) -> list[str]:
        return [(btn.text_content() or "").strip() for btn in self.choices.all()]

    def expect_text_contains(self, text: str) -> "QuestPage":
        expect(self.text).to_contain_text(text)
        return self

    def expect_title(self, title: str) -> "QuestPage":
        expect(self.title).to_have_text(title)
        return self

    def expect_choices_count(self, count: int) -> "QuestPage":
        expect(self.choices).to_have_count(count)
        return self

    def expect_final(self) -> "QuestPage":
        expect(self.final_block).to_be_visible()
        return self

    def expect_money(self, amount: int) -> "QuestPage":
        expect(self.money).to_contain_text(str(amount))
        return self