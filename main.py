import json
import os
import random
from datetime import datetime

DATA_FILE = "words.json"


# ── Збереження даних ────────────────────────────────────────────────────────

def load_data():
    """Завантажує картки з JSON-файлу.
    Якщо файл не існує — повертає порожній список."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(words):
    """Записує список карток у JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


# ── Допоміжні функції ────────────────────────────────────────────────────────

def next_id(words):
    """Генерує наступний унікальний ідентифікатор."""
    if not words:
        return 1
    return max(w["id"] for w in words) + 1


def print_words(words):
    """Виводить список карток у вигляді таблиці."""
    if not words:
        print("  Словник порожній.")
        return
    print(f"\n  {'ID':<4} {'Слово':<20} {'Переклад':<20} {'Рейтинг':<8} Приклад")
    print("  " + "-" * 75)
    for w in words:
        example_short = w["example"][:30] + "..." if len(w["example"]) > 30 else w["example"]
        print(f"  {w['id']:<4} {w['word']:<20} {w['translation']:<20} {w['rating']:<8} {example_short}")


def get_weight(rating):
    """Обраховує вагу слова для зваженої вибірки.
    Слова з низьким рейтингом з'являються частіше."""
    return max(1, 5 - rating)


def find_word(query, words):
    """Шукає картку за ID або точною назвою. Повертає картку або None."""
    try:
        rec_id = int(query)
        for w in words:
            if w["id"] == rec_id:
                return w
    except ValueError:
        for w in words:
            if w["word"].lower() == query.lower():
                return w
    return None


# ── Основна логіка ───────────────────────────────────────────────────────────

def add_word():
    """Запитує дані у користувача і додає нову флеш-картку."""
    print()
    word = input("  Слово (оригінал): ").strip()
    if not word:
        print("  Помилка: слово не може бути порожнім.")
        return

    translation = input("  Переклад: ").strip()
    if not translation:
        print("  Помилка: переклад не може бути порожнім.")
        return

    example = input("  Приклад вживання (необов'язково): ").strip()

    words = load_data()

    for w in words:
        if w["word"].lower() == word.lower():
            print(f"  Увага: слово '{word}' вже є у словнику (ID {w['id']}).")
            confirm = input("  Додати все одно? (т/н): ").strip().lower()
            if confirm not in ("т", "y", "yes", "так"):
                print("  Додавання скасовано.")
                return
            break

    words.append({
        "id": next_id(words),
        "word": word,
        "translation": translation,
        "example": example,
        "rating": 0
    })
    save_data(words)
    print(f"  ✓ Слово '{word}' додано до словника.")


def show_all():
    """Виводить всі картки словника."""
    words = load_data()
    print(f"\n  Всього слів у словнику: {len(words)}")
    print_words(words)


def edit_word():
    """Редагує переклад або приклад існуючої картки."""
    print()
    query = input("  Введіть ID або слово для редагування: ").strip()
    if not query:
        print("  Помилка: введіть ID або слово.")
        return

    words = load_data()
    target = find_word(query, words)

    if target is None:
        print(f"  Слово '{query}' не знайдено.")
        return

    print(f"\n  Картка: {target['word']} → {target['translation']}")
    print(f"  Приклад: {target['example'] or '(немає)'}")
    print(f"  Рейтинг: {target['rating']}")
    print()
    print("  Що змінити?")
    print("  1. Переклад")
    print("  2. Приклад вживання")
    print("  3. Обидва")
    print("  0. Скасувати")

    choice = input("\n  Ваш вибір: ").strip()

    if choice == "0":
        print("  Редагування скасовано.")
        return

    idx = words.index(target)

    if choice in ("1", "3"):
        new_translation = input(f"  Новий переклад (зараз: '{target['translation']}'): ").strip()
        if not new_translation:
            print("  Помилка: переклад не може бути порожнім.")
            return
        words[idx]["translation"] = new_translation

    if choice in ("2", "3"):
        new_example = input(f"  Новий приклад (Enter = залишити): ").strip()
        if new_example:
            words[idx]["example"] = new_example

    if choice not in ("1", "2", "3"):
        print("  Невідомий вибір.")
        return

    save_data(words)
    print(f"  ✓ Картку '{words[idx]['word']}' оновлено.")


def reset_rating():
    """Скидає рейтинг слова або всього словника до 0."""
    print()
    print("  Що скинути?")
    print("  1. Одне слово (за ID або назвою)")
    print("  2. Весь словник")
    print("  0. Скасувати")

    choice = input("\n  Ваш вибір: ").strip()

    if choice == "0":
        print("  Скасовано.")
        return

    words = load_data()

    if choice == "1":
        query = input("  Введіть ID або слово: ").strip()
        if not query:
            print("  Помилка: введіть ID або слово.")
            return

        target = find_word(query, words)
        if target is None:
            print(f"  Слово '{query}' не знайдено.")
            return

        print(f"  Знайдено: '{target['word']}' → '{target['translation']}' (рейтинг: {target['rating']})")
        confirm = input("  Скинути рейтинг до 0? (т/н): ").strip().lower()
        if confirm not in ("т", "y", "yes", "так"):
            print("  Скасовано.")
            return

        idx = words.index(target)
        words[idx]["rating"] = 0
        save_data(words)
        print(f"  ✓ Рейтинг '{target['word']}' скинуто до 0.")

    elif choice == "2":
        if not words:
            print("  Словник порожній.")
            return
        confirm = input(f"  Скинути рейтинг ВСІХ {len(words)} слів до 0? (т/н): ").strip().lower()
        if confirm not in ("т", "y", "yes", "так"):
            print("  Скасовано.")
            return

        for w in words:
            w["rating"] = 0
        save_data(words)
        print(f"  ✓ Рейтинг всіх {len(words)} слів скинуто до 0.")

    else:
        print("  Невідомий вибір.")


def _run_training(words, rounds, reverse=False):
    """Внутрішня логіка тренування. reverse=True — переклад → слово."""
    correct = 0
    weights = [get_weight(w["rating"]) for w in words]

    mode_label = "переклад → слово" if reverse else "слово → переклад"
    print(f"\n  Режим: {mode_label}. {rounds} раундів.")
    print("  Регістр не має значення.\n")

    for i in range(1, rounds + 1):
        chosen = random.choices(words, weights=weights, k=1)[0]
        idx = words.index(chosen)

        if reverse:
            print(f"  [{i}/{rounds}] {chosen['translation']}")
            answer = input("         Оригінал: ").strip().lower()
            correct_answer = chosen["word"].lower()
        else:
            print(f"  [{i}/{rounds}] {chosen['word']}")
            if chosen["example"]:
                print(f"         Приклад: {chosen['example']}")
            answer = input("         Переклад: ").strip().lower()
            correct_answer = chosen["translation"].lower()

        if answer == correct_answer:
            print("         ✓ Правильно!")
            words[idx]["rating"] += 1
            weights[idx] = get_weight(words[idx]["rating"])
            correct += 1
        else:
            if reverse:
                print(f"         ✗ Правильна відповідь: {chosen['word']}")
            else:
                print(f"         ✗ Правильна відповідь: {chosen['translation']}")
            if words[idx]["rating"] > 0:
                words[idx]["rating"] -= 1
                weights[idx] = get_weight(words[idx]["rating"])
        print()

    save_data(words)
    pct = round(correct / rounds * 100)
    print(f"  ─────────────────────────────────────")
    print(f"  Результат сесії: {correct}/{rounds} правильних ({pct}%)")
    if pct >= 80:
        print("  Відмінно! Продовжуйте в тому ж дусі!")
    elif pct >= 50:
        print("  Непогано! Є куди рости.")
    else:
        print("  Потрібно більше практики. Не здавайтеся!")


def train():
    """Режим тренування: слово → переклад."""
    words = load_data()
    if len(words) < 2:
        print("  Для тренування потрібно мінімум 2 слова.")
        return
    print()
    try:
        rounds_input = input(f"  Кількість раундів (Enter = 10): ").strip()
        rounds = int(rounds_input) if rounds_input else 10
        if rounds < 1:
            raise ValueError
    except ValueError:
        print("  Помилка: введіть ціле додатне число.")
        return
    _run_training(words, rounds, reverse=False)


def train_reverse():
    """Режим зворотного тренування: переклад → слово."""
    words = load_data()
    if len(words) < 2:
        print("  Для тренування потрібно мінімум 2 слова.")
        return
    print()
    try:
        rounds_input = input(f"  Кількість раундів (Enter = 10): ").strip()
        rounds = int(rounds_input) if rounds_input else 10
        if rounds < 1:
            raise ValueError
    except ValueError:
        print("  Помилка: введіть ціле додатне число.")
        return
    _run_training(words, rounds, reverse=True)


def show_stats():
    """Виводить статистику по словнику."""
    words = load_data()
    if not words:
        print("  Словник порожній. Немає даних для статистики.")
        return

    total = len(words)
    avg_rating = round(sum(w["rating"] for w in words) / total, 2)
    sorted_words = sorted(words, key=lambda w: w["rating"])

    print(f"\n  ─── Статистика словника ───────────────────────")
    print(f"  Всього слів:      {total}")
    print(f"  Середній рейтинг: {avg_rating}")

    worst = sorted_words[:5]
    print(f"\n  Потребують повторення (найнижчий рейтинг):")
    for w in worst:
        print(f"    [{w['rating']}]  {w['word']}  →  {w['translation']}")

    best = sorted_words[-5:][::-1]
    print(f"\n  Найкраще засвоєні (найвищий рейтинг):")
    for w in best:
        print(f"    [{w['rating']}]  {w['word']}  →  {w['translation']}")


def search_word():
    """Шукає слово за підрядком у слові або перекладі."""
    print()
    query = input("  Пошуковий запит: ").strip().lower()
    if not query:
        print("  Помилка: введіть запит для пошуку.")
        return

    words = load_data()
    results = [
        w for w in words
        if query in w["word"].lower() or query in w["translation"].lower()
    ]

    print(f"\n  Знайдено: {len(results)} результат(ів) за запитом '{query}'")
    print_words(results)


def delete_word():
    """Видаляє слово за ID або точним збігом слова."""
    print()
    query = input("  Введіть ID або точне слово для видалення: ").strip()
    if not query:
        print("  Помилка: введіть ID або слово.")
        return

    words = load_data()
    target = find_word(query, words)

    if target is None:
        print(f"  Слово '{query}' не знайдено у словнику.")
        return

    print(f"  Знайдено: '{target['word']}' → '{target['translation']}'")
    confirm = input("  Видалити? (т/н): ").strip().lower()
    if confirm not in ("т", "y", "yes", "так"):
        print("  Видалення скасовано.")
        return

    new_words = [w for w in words if w["id"] != target["id"]]
    save_data(new_words)
    print(f"  ✓ Слово '{target['word']}' видалено.")


# ── Меню ────────────────────────────────────────────────────────────────────

def menu():
    """Головний цикл програми з текстовим меню."""
    actions = {
        "1": add_word,
        "2": show_all,
        "3": train,
        "4": train_reverse,
        "5": show_stats,
        "6": search_word,
        "7": edit_word,
        "8": reset_rating,
        "9": delete_word,
    }

    while True:
        print("\n" + "=" * 45)
        print("  Словник із флеш-картками")
        print("=" * 45)
        words = load_data()
        print(f"  Слів у словнику: {len(words)}")
        print()
        print("  1. Додати слово")
        print("  2. Переглянути словник")
        print("  3. Тренування: слово → переклад")
        print("  4. Тренування: переклад → слово")
        print("  5. Статистика")
        print("  6. Пошук слова")
        print("  7. Редагувати картку")
        print("  8. Скинути рейтинг")
        print("  9. Видалити слово")
        print("  0. Вийти")

        choice = input("\n  Ваш вибір: ").strip()

        if choice == "0":
            print("  До побачення! Вчіться регулярно!")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("  Невідома команда. Введіть число від 0 до 9.")


if __name__ == "__main__":
    menu()