"""Точка входа: чтение, проверка, анализ и сохранение результатов."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from analysis import (
    completion_counts,
    leader_completed_ids,
    select_tasks,
    top_users,
    validate_todos,
)

BASE = Path(__file__).resolve().parent


def load_todos(path: Path) -> list[dict]:
    """Читает JSON-файл и валидирует структуру."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    validate_todos(data)
    return data


def ask_user_id() -> int:
    """Положительный целый user_id с повторным вводом."""
    while True:
        raw = input("Введите userId (целое > 0): ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ошибка: нужно целое число.")
            continue
        if value <= 0:
            print("Ошибка: число должно быть положительным.")
            continue
        return value


def ask_parameter() -> str:
    """Непустая строка-параметр (вариант 8)."""
    while True:
        raw = input("Введите подстроку для поиска в названии: ")
        if raw.strip():
            return raw.strip()
        print("Ошибка: строка не должна быть пустой.")


def main() -> int:
    try:
        todos = load_todos(BASE / "todos.json")
    except FileNotFoundError:
        print("Файл todos.json не найден")
        return 1
    except json.JSONDecodeError as error:
        print(f"Ошибка JSON: {error}")
        return 1
    except UnicodeError as error:
        print(f"Ошибка кодировки: {error}")
        return 1
    except ValueError as error:  # сюда попадут и структурные ошибки
        print(f"Ошибка данных: {error}")
        return 1
    except OSError as error:
        print(f"Ошибка доступа к файлу: {error}")
        return 1

    counts = completion_counts(todos)
    leaders = top_users(counts)
    leader_ids = leader_completed_ids(todos, leaders)

    print("Количества выполненных задач:", counts)
    print("Лидеры:", leaders)
    print("Задачи лидеров:", leader_ids)

    # --- индивидуальный вариант ---
    user_id = ask_user_id()
    parameter = ask_parameter()
    selected = select_tasks(todos, user_id, parameter)
    print(f"Выбрано задач для userId={user_id}: {len(selected)}")

    # Сохраняем только после успешной обработки
    try:
        with open(BASE / "leaders.json", "w", encoding="utf-8") as file:
            json.dump(leader_ids, file, ensure_ascii=False, indent=2)
        with open(BASE / "selected.json", "w", encoding="utf-8") as file:
            json.dump(selected, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Ошибка записи: {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
Ключевые моменты:

json.JSONDecodeError — подкласс ValueError, поэтому его обработчик стоит раньше общего 
except ValueError
.

Запись результатов выполняется только после успешного чтения и валидации — при ошибке входных данных прежние leaders.json / selected.json не перезаписываются.
