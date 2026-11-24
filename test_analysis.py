"""Тесты анализа (без сетевых вызовов)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis import (
    completion_counts,
    leader_completed_ids,
    select_tasks,
    top_users,
    validate_todos,
)

BASE = Path(__file__).resolve().parent


def load_sample() -> list[dict]:
    with open(BASE / "todos.json", "r", encoding="utf-8") as file:
        return json.load(file)


# ---------- обязательные проверки ----------

def test_sample_counts_leaders_and_ids():
    todos = load_sample()
    validate_todos(todos)
    counts = completion_counts(todos)
    assert counts == {5: 2, 10: 2}
    leaders = top_users(counts)
    assert leaders == [5, 10]
    assert leader_completed_ids(todos, leaders) == [1, 3, 4, 5]


def test_empty_and_all_incomplete():
    assert top_users({}) == []
    empty_todos: list[dict] = []
    assert completion_counts(empty_todos) == {}
    assert top_users(completion_counts(empty_todos)) == []

    incomplete = [
        {"id": 1, "userId": 1, "title": "a", "completed": False},
        {"id": 2, "userId": 2, "title": "b", "completed": False},
    ]
    counts = completion_counts(incomplete)
    assert top_users(counts) == []
    assert leader_completed_ids(incomplete, top_users(counts)) == []


def test_single_and_multiple_leaders():
    single = [
        {"id": 1, "userId": 1, "title": "a", "completed": True},
        {"id": 2, "userId": 2, "title": "b", "completed": False},
    ]
    assert top_users(completion_counts(single)) == [1]

    multi = [
        {"id": 1, "userId": 1, "title": "a", "completed": True},
        {"id": 2, "userId": 2, "title": "b", "completed": True},
    ]
    assert top_users(completion_counts(multi)) == [1, 2]


# ---------- индивидуальный вариант (8) ----------

def test_variant_sample():
    todos = load_sample()
    result = select_tasks(todos, 5, "и")
    assert [t["id"] for t in result] == [2, 5]


def test_variant_unknown_user():
    assert select_tasks(load_sample(), 999, "и") == []


def test_variant_no_matches():
    assert select_tasks(load_sample(), 5, "zzz") == []


def test_variant_mixed_case():
    todos = load_sample()
    upper = select_tasks(todos, 5, "И")
    lower = select_tasks(todos, 5, "и")
    assert [t["id"] for t in upper] == [t["id"] for t in lower] == [2, 5]


# ---------- ошибки структуры ----------

@pytest.mark.parametrize("bad", [
    {"not": "a list"},
    [{"id": 1, "userId": 1, "title": "a", "completed": True},
     {"id": 1, "userId": 1, "title": "b", "completed": True}],          # повторный id
    [{"id": 1, "title": "a", "completed": True}],                       # нет userId
    [{"id": 1, "userId": 1, "title": "a", "completed": "false"}],       # completed не bool
    [{"id": True, "userId": 1, "title": "a", "completed": True}],       # id=bool
    [{"id": 0, "userId": 1, "title": "a", "completed": True}],          # не положительный
    [{"id": 1, "userId": 1, "title": "", "completed": True}],           # пустой title
])
def test_validation_errors(bad):
    with pytest.raises(ValueError):
        validate_todos(bad)


# ---------- round-trip JSON ----------

def test_round_trip(tmp_path: Path):
    todos = load_sample()
    selected = select_tasks(todos, 5, "и")
    path = tmp_path / "selected.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(selected, file, ensure_ascii=False, indent=2)
    with open(path, "r", encoding="utf-8") as file:
        restored = json.load(file)
    assert restored == selected


# ---------- исходные записи не изменяются ----------

def test_select_tasks_does_not_mutate():
    todos = load_sample()
    snapshot = json.loads(json.dumps(todos))
    select_tasks(todos, 5, "и")
    assert todos == snapshot
Запуск тестов:

bash
python -m pytest test_analysis.py -v
