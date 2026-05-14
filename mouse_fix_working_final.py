#!/usr/bin/env python3
"""
Рабочая версия Mouse Double-Click Fixer
Демонстрирует принцип работы и может блокировать клики при запуске от администратора
"""

import time
import threading
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70  # Порог в миллисекундах (можно изменить)
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0  # Порог в секундах

# Состояние
last_click_time = {}
total_clicks = {}
blocked_clicks = {}
lock = threading.Lock()

def on_click(x, y, button, pressed):
    """Обработчик событий клика мыши."""
    if not pressed:  # Обрабатываем только нажатие кнопки
        return True
        
    button_name = getattr(button, 'name', str(button))
    current_time = time.time()
    
    with lock:
        # Считаем общее количество кликов
        total_clicks[button_name] = total_clicks.get(button_name, 0) + 1
        
        # Проверяем время с последнего клика этой кнопки
        last_time = last_click_time.get(button_name, 0)
        time_diff = current_time - last_time
        
        # Если это быстрый двойной клик (интервал меньше порога)
        if 0 < time_diff < CLICK_THRESHOLD_S:
            # Блокируем этот клик
            blocked_clicks[button_name] = blocked_clicks.get(button_name, 0) + 1
            
            # Выводим информацию о блокировке
            print(f"🔇 БЛОКИРОВКА: {button_name} клик "
                  f"(интервал: {time_diff*1000:.1f} мс, "
                  f"всего: {total_clicks[button_name]}, "
                  f"заблокировано: {blocked_clicks[button_name]})")
            
            # Возвращаем False чтобы заблокировать событие
            return False
        else:
            # Нормальный клик - разрешаем
            last_click_time[button_name] = current_time
            print(f"✅ НОРМАЛ: {button_name} клик "
                  f"(интервал: {time_diff*1000:.1f} мс, "
                  f"всего: {total_clicks[button_name]})")
            return True

def print_header():
    """Выводит заголовок и инструкции."""
    print("=" * 70)
    print("Mouse Double-Click Fixer - Рабочая версия")
    print("=" * 70)
    print(f"Порог срабатывания: {CLICK_THRESHOLD_MS} мс")
    print()
    print("Как это работает:")
    print("- Программа отслеживает время между нажатиями кнопок мыши")
    print("- Если интервал меньше порога, второй клик блокируется")
    print("- Для реальной блокировки необходим запуск от администратора")
    print()
    print("Как проверить работу:")
    print("1. Медленно кликайте - должны видеть ✅ НОРМАЛ сообщения")
    print("2. Быстро дважды кликните - должен появиться 🔇 БЛОКИРОВКА сообщение")
    print("3. После блокировки программа продолжит работать")
    print("4. Смотрите счетчики в скобках")
    print()
    print("ВАЖНО: Для реальной блокировки кликов:")
    print("- Запустите эту программу от имени администратора")
    print("- Без прав администратора будет только мониторинг")
    print("- На некоторых системах может потребоваться дополнительная настройка")
    print("=" * 70)

def print_final_stats():
    """Выводит финальную статистику."""
    print("\n" + "=" * 50)
    print("ФИНАЛЬНАЯ СТАТИСТИКА:")
    print("=" * 50)
    for button in set(list(total_clicks.keys()) + list(blocked_clicks.keys())):
        total = total_clicks.get(button, 0)
        blocked = blocked_clicks.get(button, 0)
        rate = (blocked / total * 100) if total > 0 else 0
        print(f"{button:>6}: {total:>4} кликов, {blocked:>4} заблокировано ({rate:>5.1f}%)")
    print("=" * 50)

def main():
    print_header()
    
    try:
        print("[ИНФО] Запуск слушателя мыши...")
        print("[ИНФО] Нажмите Ctrl+C для остановки и просмотра статистики")
        print("-" * 70)
        
        # Запускаем слушатель мыши
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
            
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("[ИНФО] Получен сигнал остановки (Ctrl+C)")
        print_final_stats()
        print("[ИНФО] Спасибо за использование Mouse Double-Click Fixer!")
        print("=" * 50)
    except Exception as e:
        print(f"\n[ОШИБКА] Критическая ошибка: {e}")
        print("[ИНФО] Убедитесь, что установлена библиотека pynput:")
        print("       pip install pynput")

if __name__ == "__main__":
    main()