import pytest

from app.scenes import SCENES, get_scene, make_choice


def test_scenes_dict_not_empty():
    assert len(SCENES) > 0


def test_get_scene_returns_dict():
    scene = get_scene("start")
    assert isinstance(scene, dict)
    assert "title" in scene
    assert "text" in scene
    assert "choices" in scene


def test_get_scene_unknown_raises():
    with pytest.raises(KeyError):
        get_scene("unknown_scene")


def test_make_choice_returns_next_scene():
    assert make_choice("start", 0) == "accepted"
    assert make_choice("start", 1) == "rejected"


def test_make_choice_final_scene_raises():
    with pytest.raises(ValueError):
        make_choice("destroy", 0)


def test_make_choice_invalid_index_raises():
    with pytest.raises(IndexError):
        make_choice("start", 99)


def test_final_scenes_have_reward():
    for name, scene in SCENES.items():
        if not scene["choices"]:
            assert "reward" in scene, f"Сцена '{name}' без награды"