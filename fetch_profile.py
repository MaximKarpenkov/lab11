"""Получение профиля GitHub по логину (HTTP) или локальный пример."""
from __future__ import annotations

import json
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent


def fetch_profile(login: str) -> dict:
    """Запрашивает профиль GitHub по логину через GET."""
    if not login.strip():
        raise ValueError("Логин не должен быть пустым")

    url = "https://api.github.com/users/" + quote(login.strip(), safe="")
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "python-course-lab11",
    })
    with urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, dict) or not isinstance(data.get("login"), str):
        raise ValueError("Ответ не похож на профиль пользователя")
    return data


def load_local_sample() -> dict:
    """Читает локальный profile_sample.json (учебные данные)."""
    path = BASE / "profile_sample.json"
    if not path.exists():
        # создаём учебный пример, если его нет
        sample = {"login": "demo", "id": 1, "name": None}
        with open(path, "w", encoding="utf-8") as file:
            json.dump(sample, file, ensure_ascii=False, indent=2)
        return sample
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def print_profile(data: dict, source: str) -> None:
    """Общая функция вывода профиля для обоих источников."""
    print(f"Источник: {source}")
    print(f"login: {data.get('login')}")
    print(f"id:    {data.get('id')}")
    print(f"name:  {data.get('name')}")


def save_profile(data: dict) -> Path:
    output = BASE / "profile.json"
    with open(output, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return output


def main() -> int:
    print("Источник профиля:")
    print("  1 — сеть (api.github.com)")
    print("  2 — локальный пример (profile_sample.json)")
    choice = input("Выбор [1/2]: ").strip()

    try:
        if choice == "1":
            login = input("Логин GitHub: ")
            data = fetch_profile(login)
            print_profile(data, "сеть (api.github.com)")
        elif choice == "2":
            data = load_local_sample()
            print_profile(data, "локальный пример (учебные данные)")
        else:
            print("Неизвестный пункт меню")
            return 1

        path = save_profile(data)
        print(f"Профиль сохранён: {path.name}")
        return 0

    except HTTPError as error:
        print(f"Сервер вернул HTTP {error.code}")
    except (URLError, TimeoutError, socket.timeout):
        print("Не удалось получить ответ по сети")
    except (ValueError, UnicodeError) as error:
        print(f"Ошибка данных: {error}")
    except OSError as error:
        print(f"Ошибка доступа: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
