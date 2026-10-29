
import pytest
from app.glossary import GLOSSARY

pytestmark = pytest.mark.unit

@pytest.mark.parametrize("key,item", list(GLOSSARY.items()))
def test_glossary_entry_has_required_fields(key, item):
    for field in ("title", "category", "short", "full"):
        assert field in item, f"{key}: нет поля {field!r}"
    assert isinstance(item["full"], str) and len(item["full"]) > 0

def test_glossary_categories_are_known():
    known = {"Расы", "Персонажи", "Планеты", "Звёздные системы", "Организации"}
    for key, item in GLOSSARY.items():
        assert item["category"] in known, f"{key}: неизвестная категория {item['category']!r}"