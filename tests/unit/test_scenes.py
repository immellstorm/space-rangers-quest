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

def test_make_choice_from_accepted():
    assert make_choice("accepted", 0) == "destroy"
    assert make_choice("accepted", 1) == "negotiate"
    assert make_choice("accepted", 2) == "scout"

def test_make_choice_from_scout():
    assert make_choice("scout", 0) == "destroy"
    assert make_choice("scout", 1) == "negotiate"
    assert make_choice("scout", 2) == "cache"