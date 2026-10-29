import pytest

pytestmark = pytest.mark.unit

from app.scenes import (
    SCENES, make_choice, visible_choices, apply_effects,
)

def test_import_scenes():
    assert len(SCENES) > 0

def make_state(**overrides):
    return {**{ "player_name": "", "current_scene": "start", "money": 0, "relations": {}, "history": [], "inventory": {}, "trust": {}, "flags": {}, "days": 0,}, **overrides}

def test_choice_without_condition_is_visible():
    scene = {"choices": [{"text": "A", "next": "a"}]}
    result = visible_choices(scene, make_state())
    assert len(result) == 1

def test_two_choices_without_condition_both_visible():
    scene = {"choices": [{"text": "A", "next": "a"}, {"text": "B", "next": "b"}]}
    result = visible_choices(scene, make_state())
    assert len(result) == 2

def test_flag_absent_visible_when_flag_not_set():
    scene = {"choices": [
        {"text": "A", "next": "a", "condition": {"flag_absent": "done"}},
    ]}
    state = make_state()            
    assert len(visible_choices(scene, state)) == 1


def test_flag_absent_hidden_when_flag_set():
    scene = {"choices": [
        {"text": "A", "next": "a", "condition": {"flag_absent": "done"}},
    ]}
    state = make_state(flags={"done": True})
    assert visible_choices(scene, state) == []

def test_flag_present_hidden_when_flag_not_set():
    scene = {"choices": [
            {"text": "A", "next": "a", "condition": {"flag_present": "done"}},
    ]}
    state = make_state()
    assert visible_choices(scene, state) == []


def test_flag_present_visible_when_flag_set():
    scene = {"choices": [
        {"text": "A", "next": "a", "condition": {"flag_present": "done"}},
    ]}
    state = make_state(flags={"done": True})       
    assert len(visible_choices(scene, state)) == 1

def test_money_at_least_hidden_below():
    scene = {"choices": [
        {"text": "A", "next": "a", "condition": {"money_at_least": 100}},
    ]}
    state = make_state(money=99)
    assert visible_choices(scene, state) == []

def test_money_at_least_visible_at_boundary():
    scene = {"choices": [
        {"text": "A", "next": "a", "condition": {"money_at_least": 100}},
    ]}
    state = make_state(money=100)
    assert len(visible_choices(scene, state)) == 1

def test_money_delta():
    state = make_state(money=100)
    apply_effects(state, {"money": -30})
    assert state["money"] == 70

def test_money_negative_delta():
    state = make_state(money=100)
    apply_effects(state, {"money": -30})
    assert state["money"] == 70

def test_money_positive_delta():
    state = make_state(money=100)
    apply_effects(state, {"money": +50})
    assert state["money"] == 150

def test_inventory_added():
    state = make_state()
    apply_effects(state, {"inventory": {"bomb": 2}})
    assert state["inventory"]["bomb"] == 2

def test_inventory_removed_when_reaches_zero():
    state = make_state(inventory={"bomb": 1})
    apply_effects(state, {"inventory": {"bomb": -1}})
    assert "bomb" not in state["inventory"]

def test_trust_not_below_zero():
    state = make_state(trust={"Kacap": 10})
    apply_effects(state, {"trust": {"Kacap": -50}})
    assert state["trust"]["Kacap"] == 0


def test_trust_not_above_hundred():
    state = make_state(trust={"Kacap": 90})
    apply_effects(state, {"trust": {"Kacap": +50}})
    assert state["trust"]["Kacap"] == 100

def test_days_not_below_zero():
    state = make_state(days=1)
    apply_effects(state, {"days": -5})
    assert state["days"] == 0

def test_none_gives_is_noop():
    state = make_state(money=50, days=2)
    snapshot = dict(state)           
    apply_effects(state, None)
    assert state == snapshot  

def test_flags_are_set():
    state = make_state()
    apply_effects(state, {"flags": {"done": True, "count": 5}})
    assert state["flags"]["done"] is True
    assert state["flags"]["count"] == 5    

@pytest.mark.parametrize("scene_name", list(SCENES.keys()))
def test_all_next_point_to_existing_scenes(scene_name):
    scene = SCENES[scene_name]
    for i, choice in enumerate(scene["choices"]):
        assert choice["next"] in SCENES, (
            f"{scene_name}[{i}]: next={choice['next']!r} не существует"
        )

@pytest.mark.parametrize("scene_name", list(SCENES.keys()))
def test_all_conditions_are_valid(scene_name):
    scene = SCENES[scene_name]
    try:
        visible_choices(scene, make_state())
    except ValueError as e:
        pytest.fail(f"{scene_name}: {e}")

@pytest.mark.parametrize("scene_name,index,expected_next", [
    ("start", 0, "landing"),
    ("start", 1, "rejected"),
    ("base_see_bio_lvl", 0, "strick_ameba"),
    ("base_see_bio_lvl", 1, "base_my_room"),
    ("base_see_bio_lvl", 2, "see_base"),
    ("cooking_room", 0, "cooking_book"),
    ("cooking_room", 1, "eat_room"),
])
def test_make_choice_valid(scene_name, index, expected_next):
    next_scene, choice = make_choice(scene_name, index, make_state())
    assert next_scene == expected_next
    assert "text" in choice

def test_make_choice_bad_index():
    with pytest.raises(IndexError, match="Неверный индекс"):
        make_choice("start", 99, make_state())

@pytest.mark.parametrize("condition,state,should_be_visible", [
    ({"flags_not_exact": {"a": 1, "b": 1}}, make_state(flags={"a": 1, "b": 1}), False),
    ({"flags_not_exact": {"a": 1, "b": 1}}, make_state(flags={"a": 1}), True),
    ({"flags_exact": {"a": 1, "b": 1}}, make_state(flags={"a": 1, "b": 1}), True),
    ({"flags_exact": {"a": 1, "b": 1}}, make_state(flags={"a": 1}), False),
    ({"flags_all": ["a", "b"]}, make_state(flags={"a": 1, "b": 1}), True),
    ({"flags_all": ["a", "b"]}, make_state(flags={"a": 1}), False),
    ({"inventory_at_least": {"a": 1}}, make_state(inventory={"a": 1}), True),
    ({"inventory_at_least": {"a": 1}}, make_state(inventory={}), False),
    ({"inventory_absent": "b"}, make_state(inventory={"a": 1}), True),
    ({"inventory_absent": "a"}, make_state(inventory={"a": 1}), False),
    ({"inventory_has_all": ["a", "b"]}, make_state(inventory={"a": 1, "b": 1}), True),
    ({"inventory_has_all": ["a", "b"]}, make_state(inventory={"a": 1}), False),
    ({"trust_at_least": {"name": "K", "value": 80}}, make_state(trust={"K": 80}), True),
    ({"trust_at_least": {"name": "K", "value": 80}}, make_state(trust={"K": 79}), False),
    ({"inventory_not_has_all": ["a", "b"]}, make_state(inventory={}), True),
    ({"inventory_not_has_all": ["a", "b"]}, make_state(inventory={"a": 1}),  True),
    ({"inventory_not_has_all": ["a", "b"]}, make_state(inventory={"a": 1, "b": 1}), False),
    ({"trust_below": {"name": "K", "value": 30}}, make_state(trust={"K": 30}), False),
    ({"trust_below": {"name": "K", "value": 30}}, make_state(trust={"K": 29}), True),
    ({"days_at_least": 3}, make_state(days=3), True),
    ({"days_at_least": 3}, make_state(days=2), False),
    ({"days_at_least": 3}, make_state(days=4), True),
    ({"days_below": 3}, make_state(days=2), True),     
    ({"days_below": 3}, make_state(days=3), False),   
    ({"days_below": 3}, make_state(days=4), False),
])

def test_conditions_visible(condition, state, should_be_visible):
    scene = {"choices": [{"text": "A", "next": "a", "condition": condition}]}
    result = visible_choices(scene, state)
    assert (len(result) == 1) == should_be_visible
