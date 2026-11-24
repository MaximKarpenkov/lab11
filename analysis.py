"""Модуль анализа учебного набора задач (без сетевых вызовов)."""
from __future__ import annotations


def validate_todos(data) -> None:
    """Проверяет структуру набора задач.

    Корень — список; каждая запись — словарь с:
      * положительными целыми id, userId (строго type is int);
      * непустой строкой title;
      * логическим completed (type is bool);
      * уникальным id.
    Дополнительные ключи допустимы.
    При нарушении бросает ValueError с пояснением.
    """
    if not isinstance(data, list):
        raise ValueError("Корень JSON должен быть списком")

    seen_ids: set[int] = set()
    for index, item in enumerate(data):
        where = f"запись #{index}"

        if not isinstance(item, dict):
            raise ValueError(f"{where}: ожидался объект (словарь)")

        # --- id ---
        if "id" not in item:
            raise ValueError(f"{where}: отсутствует поле 'id'")
        tid = item["id"]
        if type(tid) is not int:
            raise ValueError(f"{where}: 'id' должен быть целым числом (не bool)")
        if tid <= 0:
            raise ValueError(f"{where}: 'id' должен быть положительным")
        if tid in seen_ids:
            raise ValueError(f"{where}: повторяющийся id={tid}")
        seen_ids.add(tid)

        # --- userId ---
        if "userId" not in item:
            raise ValueError(f"{where}: отсутствует поле 'userId'")
        uid = item["userId"]
        if type(uid) is not int:
            raise ValueError(f"{where}: 'userId' должен быть целым числом (не bool)")
        if uid <= 0:
            raise ValueError(f"{where}: 'userId' должен быть положительным")

        # --- title ---
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{where}: 'title' должен быть непустой строкой")

        # --- completed ---
        if "completed" not in item:
            raise ValueError(f"{where}: отсутствует поле 'completed'")
        if type(item["completed"]) is not bool:
            raise ValueError(f"{where}: 'completed' должен быть bool")


def completion_counts(todos: list[dict]) -> dict[int, int]:
    """Словарь {userId: число выполненных задач}.

    Включает всех пользователей из набора, в том числе с нулём.
    """
    counts: dict[int, int] = {}
    for task in todos:
        uid = task["userId"]
        counts.setdefault(uid, 0)
        if task["completed"]:
            counts[uid] += 1
    return counts


def top_users(counts: dict[int, int]) -> list[int]:
    """Список userId с максимальным числом выполненных задач.

    Для пустого словаря или максимума 0 — [].
    """
    if not counts:
        return []
    max_value = max(counts.values())
    if max_value == 0:
        return []
    return sorted(uid for uid, value in counts.items() if value == max_value)


def leader_completed_ids(todos: list[dict], leaders: list[int]) -> list[int]:
    """id выполненных задач, принадлежащих лидерам, в исходном порядке."""
    leaders_set = set(leaders)
    return [
        t["id"]
        for t in todos
        if t["completed"] and t["userId"] in leaders_set
    ]


def select_tasks(
    todos: list[dict],
    user_id: int,
    parameter: str | int | None = None,
) -> list[dict]:
    """Фильтр задач пользователя (вариант 8: title содержит подстроку, без учёта регистра).

    Возвращает новые словари (копии), исходные записи не изменяются.
    Для неизвестного пользователя — [].
    """
    if type(user_id) is not int or user_id <= 0:
        raise ValueError("user_id должен быть положительным целым числом")

    # Вариант 8: параметр — непустая строка
    if not isinstance(parameter, str) or not parameter.strip():
        raise ValueError("Параметр должен быть непустой строкой")

    needle = parameter.strip().lower()
    result: list[dict] = []
    for task in todos:
        if task["userId"] != user_id:
            continue
        if needle in task["title"].lower():
            result.append(dict(task))
    return result
