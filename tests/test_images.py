import pytest

from app.images import get_scene_image
from app.images import SCENE_IMAGES, STATIC_IMAGES

pytestmark = pytest.mark.unit

def test_get_scene_image_returns_existing(monkeypatch, tmp_path):
    (tmp_path / "start.png").write_bytes(b"fake")
    monkeypatch.setattr("app.images.STATIC_IMAGES", tmp_path)
    assert get_scene_image("start") == "start.png"


def test_get_scene_image_falls_back_to_default(monkeypatch, tmp_path):
    (tmp_path / "your_name.jpeg").write_bytes(b"fake")
    monkeypatch.setattr("app.images.STATIC_IMAGES", tmp_path)
    assert get_scene_image("nonexistent_scene") == "your_name.jpeg"


def test_get_scene_image_empty_when_nothing_exists(monkeypatch, tmp_path):
    monkeypatch.setattr("app.images.STATIC_IMAGES", tmp_path)
    assert get_scene_image("nonexistent") == ""

def test_all_scene_images_exist():
    missing = [
        name for name, fname in SCENE_IMAGES.items()
        if not (STATIC_IMAGES / fname).is_file()
    ]
    assert not missing, f"Нет файлов картинок: {missing}"