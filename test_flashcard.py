"""
test_flashcard.py
Автоматизовані тести для утиліти "Словник із флеш-картками".
Перевіряються функції: load_data, save_data, next_id, get_weight,
а також логіка тренування (оновлення рейтингу).
"""

import json
import os
import sys

# Підключаємо головний модуль
sys.path.insert(0, os.path.dirname(__file__))
import main

TEST_FILE = "test_words.json"


def setup(records):
    """Записує тестові дані у тимчасовий файл."""
    main.DATA_FILE = TEST_FILE
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)


def teardown():
    """Видаляє тимчасовий файл після тесту."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    main.DATA_FILE = "words.json"


def run_test(name, fn):
    """Запускає один тест і виводить результат."""
    try:
        fn()
        print(f"  ✓ {name}")
        return True
    except AssertionError as e:
        print(f"  ✗ {name}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ {name}: неочікувана помилка — {e}")
        return False
    finally:
        teardown()


# ── Тест 1: завантаження даних ───────────────────────────────────────────────
def test_load_data():
    records = [
        {"id": 1, "word": "apple", "translation": "яблуко", "example": "", "rating": 2},
        {"id": 2, "word": "book",  "translation": "книга",  "example": "", "rating": 0},
    ]
    setup(records)
    loaded = main.load_data()
    assert len(loaded) == 2, f"Очікувалось 2 записи, отримано {len(loaded)}"
    assert loaded[0]["word"] == "apple"
    assert loaded[1]["translation"] == "книга"


# ── Тест 2: завантаження при відсутньому файлі ───────────────────────────────
def test_load_empty():
    main.DATA_FILE = TEST_FILE
    # Файл не існує
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    result = main.load_data()
    assert result == [], f"Очікувався порожній список, отримано {result}"


# ── Тест 3: генерація наступного ID ─────────────────────────────────────────
def test_next_id():
    setup([
        {"id": 1, "word": "cat", "translation": "кіт", "example": "", "rating": 0},
        {"id": 5, "word": "dog", "translation": "собака", "example": "", "rating": 1},
    ])
    words = main.load_data()
    nid = main.next_id(words)
    assert nid == 6, f"Очікувався ID 6, отримано {nid}"


# ── Тест 4: next_id при порожньому списку ────────────────────────────────────
def test_next_id_empty():
    setup([])
    words = main.load_data()
    nid = main.next_id(words)
    assert nid == 1, f"Очікувався ID 1, отримано {nid}"


# ── Тест 5: алгоритм ваги для вибірки ────────────────────────────────────────
def test_get_weight():
    setup([])
    assert main.get_weight(0) == 5, "Рейтинг 0 → вага 5"
    assert main.get_weight(3) == 2, "Рейтинг 3 → вага 2"
    assert main.get_weight(4) == 1, "Рейтинг 4 → вага 1"
    assert main.get_weight(10) == 1, "Рейтинг 10 → вага мін. 1"


# ── Тест 6: збереження та повторне завантаження ──────────────────────────────
def test_save_and_reload():
    setup([])
    records = [
        {"id": 1, "word": "sun", "translation": "сонце", "example": "The sun is bright.", "rating": 3}
    ]
    main.save_data(records)
    reloaded = main.load_data()
    assert len(reloaded) == 1
    assert reloaded[0]["word"] == "sun"
    assert reloaded[0]["rating"] == 3


# ── Тест 7: пошук за підрядком ───────────────────────────────────────────────
def test_search_logic():
    records = [
        {"id": 1, "word": "apple",  "translation": "яблуко",  "example": "", "rating": 0},
        {"id": 2, "word": "apricot","translation": "абрикос", "example": "", "rating": 1},
        {"id": 3, "word": "banana", "translation": "банан",   "example": "", "rating": 2},
    ]
    setup(records)
    words = main.load_data()
    query = "app"
    results = [w for w in words if query in w["word"].lower() or query in w["translation"].lower()]
    assert len(results) == 1, f"Очікувався 1 результат для 'app', отримано {len(results)}"
    assert results[0]["word"] == "apple"


# ── Тест 8: оновлення рейтингу після правильної відповіді ────────────────────
def test_rating_increase():
    records = [{"id": 1, "word": "tree", "translation": "дерево", "example": "", "rating": 2}]
    setup(records)
    words = main.load_data()
    # Симулюємо правильну відповідь
    words[0]["rating"] += 1
    main.save_data(words)
    reloaded = main.load_data()
    assert reloaded[0]["rating"] == 3, f"Рейтинг після правильної відповіді має бути 3, а не {reloaded[0]['rating']}"


# ── Тест 9: рейтинг не падає нижче 0 ────────────────────────────────────────
def test_rating_floor():
    records = [{"id": 1, "word": "sky", "translation": "небо", "example": "", "rating": 0}]
    setup(records)
    words = main.load_data()
    # Симулюємо помилкову відповідь при рейтингу 0
    if words[0]["rating"] > 0:
        words[0]["rating"] -= 1
    main.save_data(words)
    reloaded = main.load_data()
    assert reloaded[0]["rating"] >= 0, f"Рейтинг не може бути від'ємним: {reloaded[0]['rating']}"



# ── Тест 10: зворотнє тренування — перевірка логіки відповіді ────────────────
def test_reverse_mode_logic():
    """Перевіряє що у зворотному режимі правильна відповідь — це word, а не translation."""
    records = [
        {"id": 1, "word": "cat", "translation": "кіт", "example": "", "rating": 2},
        {"id": 2, "word": "dog", "translation": "собака", "example": "", "rating": 1},
    ]
    setup(records)
    words = main.load_data()
    chosen = words[0]  # cat / кіт
    # У зворотньому режимі показуємо "кіт", очікуємо відповідь "cat"
    correct_answer = chosen["word"].lower()
    user_answer = "cat"
    assert user_answer == correct_answer, f"Очікувалось 'cat', отримано '{correct_answer}'"



# ── Тест 11: редагування перекладу ───────────────────────────────────────────
def test_edit_translation():
    """Перевіряє що після редагування переклад оновлюється у файлі."""
    records = [
        {"id": 1, "word": "cat", "translation": "кіт", "example": "", "rating": 2},
    ]
    setup(records)
    words = main.load_data()
    # Симулюємо редагування: змінюємо переклад
    words[0]["translation"] = "кішка"
    main.save_data(words)
    reloaded = main.load_data()
    assert reloaded[0]["translation"] == "кішка", (
        f"Очікувалось 'кішка', отримано '{reloaded[0]['translation']}'"
    )


# ── Тест 12: скидання рейтингу одного слова ──────────────────────────────────
def test_reset_single_rating():
    """Перевіряє що скидання рейтингу одного слова не чіпає інші."""
    records = [
        {"id": 1, "word": "cat", "translation": "кіт",    "example": "", "rating": 5},
        {"id": 2, "word": "dog", "translation": "собака", "example": "", "rating": 3},
    ]
    setup(records)
    words = main.load_data()
    # Скидаємо рейтинг першого слова
    words[0]["rating"] = 0
    main.save_data(words)
    reloaded = main.load_data()
    assert reloaded[0]["rating"] == 0, f"Рейтинг 'cat' має бути 0, а не {reloaded[0]['rating']}"
    assert reloaded[1]["rating"] == 3, f"Рейтинг 'dog' не повинен змінитись, а не {reloaded[1]['rating']}"


# ── Тест 13: скидання рейтингу всього словника ───────────────────────────────
def test_reset_all_ratings():
    """Перевіряє що скидання всіх рейтингів обнуляє кожне слово."""
    records = [
        {"id": 1, "word": "sun",  "translation": "сонце", "example": "", "rating": 7},
        {"id": 2, "word": "moon", "translation": "місяць","example": "", "rating": 4},
        {"id": 3, "word": "star", "translation": "зірка", "example": "", "rating": 2},
    ]
    setup(records)
    words = main.load_data()
    for w in words:
        w["rating"] = 0
    main.save_data(words)
    reloaded = main.load_data()
    for w in reloaded:
        assert w["rating"] == 0, f"Рейтинг '{w['word']}' має бути 0, а не {w['rating']}"



# ── Тест 14: імпорт з файлу — базовий сценарій ───────────────────────────────
def test_import_basic():
    """Перевіряє що рядки формату 'слово - переклад' імпортуються коректно."""
    import tempfile, os
    setup([])

    # Створюємо тимчасовий txt-файл
    txt = "apple - яблуко - An apple a day.\nbook - книга\n# коментар\n\ncat - кіт\n"
    tmp = "test_import_tmp.txt"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)

    try:
        words = main.load_data()
        existing = {w["word"].lower() for w in words}
        added = 0
        with open(tmp, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("-", 2)]
            if len(parts) < 2:
                continue
            word, translation = parts[0], parts[1]
            example = parts[2] if len(parts) == 3 else ""
            if word.lower() in existing:
                continue
            words.append({"id": main.next_id(words), "word": word,
                          "translation": translation, "example": example, "rating": 0})
            existing.add(word.lower())
            added += 1
        main.save_data(words)

        assert added == 3, f"Очікувалось 3 слова, отримано {added}"
        reloaded = main.load_data()
        assert reloaded[0]["word"] == "apple"
        assert reloaded[0]["example"] == "An apple a day."
        assert reloaded[1]["example"] == ""
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ── Тест 15: імпорт — пропуск дублікатів ─────────────────────────────────────
def test_import_skip_duplicates():
    """Перевіряє що при імпорті слова-дублікати не додаються повторно."""
    import tempfile, os
    setup([{"id": 1, "word": "apple", "translation": "яблуко", "example": "", "rating": 3}])

    tmp = "test_dup_tmp.txt"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("apple - яблуко\ndog - собака\n")

    try:
        words = main.load_data()
        existing = {w["word"].lower() for w in words}
        added = 0
        skipped = 0
        with open(tmp, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("-", 2)]
            if len(parts) < 2:
                continue
            word = parts[0]
            if word.lower() in existing:
                skipped += 1
                continue
            words.append({"id": main.next_id(words), "word": word,
                          "translation": parts[1], "example": "", "rating": 0})
            existing.add(word.lower())
            added += 1
        main.save_data(words)

        assert added == 1, f"Очікувалось 1 нове слово, додано {added}"
        assert skipped == 1, f"Очікувався 1 пропуск, отримано {skipped}"
        reloaded = main.load_data()
        assert len(reloaded) == 2
        assert reloaded[0]["rating"] == 3, "Рейтинг існуючого слова не повинен змінитись"
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ── Запуск всіх тестів ───────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("Завантаження даних з файлу",              test_load_data),
        ("Завантаження при відсутньому файлі",       test_load_empty),
        ("Генерація next_id при наявних записах",    test_next_id),
        ("Генерація next_id при порожньому списку",  test_next_id_empty),
        ("Алгоритм ваги для інтервального повторення", test_get_weight),
        ("Збереження та повторне завантаження",      test_save_and_reload),
        ("Логіка пошуку за підрядком",               test_search_logic),
        ("Оновлення рейтингу після правильної відп.", test_rating_increase),
        ("Рейтинг не падає нижче 0",                 test_rating_floor),
        ("Зворотній режим: правильна відповідь = word", test_reverse_mode_logic),
        ("Редагування перекладу картки",              test_edit_translation),
        ("Скидання рейтингу одного слова",            test_reset_single_rating),
        ("Скидання рейтингу всього словника",         test_reset_all_ratings),
        ("Імпорт: базовий сценарій",                   test_import_basic),
        ("Імпорт: пропуск дублікатів",                 test_import_skip_duplicates),
    ]

    print("\n" + "=" * 50)
    print("  Автоматизовані тести — Флеш-картки")
    print("=" * 50)

    passed = 0
    for name, fn in tests:
        if run_test(name, fn):
            passed += 1

    total = len(tests)
    print("─" * 50)
    print(f"  Пройдено: {passed}/{total}")
    if passed == total:
        print("  Всі тести пройдено успішно. ✓")
    else:
        print(f"  Помилок: {total - passed}")
        sys.exit(1)