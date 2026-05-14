#!/usr/bin/env python3
"""
Простой отладочный скрипт для проверки подавления кликов
"""

import time
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0

# Состояние
last_click_time = {}
click_counter = 0

def on_click(x, y, button, pressed):
    global click_counter
    
    click_counter += 1
    button_name = getattr(button, 'name', str(button))
    current_time = time.time()
    
    print(f"[{click_counter}] Клик {button_name} в ({x}, {y}) - {'нажата' if pressed else 'отпущена'} в {current_time:.3f}")
    
    if not pressed:
        return True  # Всегда разрешаем отпускание
    
    # Обрабатываем только нажатие
    last_time = last_click_time.get(button_name, 0)
    time_diff = current_time - last_time
    
    print(f"    Время с последнего {button_name} клика: {time_diff*1000:.1f} мс")
    
    if 0 < time_diff < CLICK_THRESHOLD_S:
        print(f"    >>> БЫСТРЫЙ ДВОЙНОЙ КЛИК ОБНАРУЖЕН! БУДЕТ ПОДАВЛЕН <<<")
        print(f"    >>> Возвращаем False для блокировки события <<<")
        return False  # Блокируем событие
    else:
        print(f"    Нормальный интервал, событие будет передано дальше")
        last_click_time[button_name] = current_time
        return True

def main():
    print("=" * 60)
    print("ОТЛАДОЧНАЯ ВЕРСИЯ ФИЛЬТРА ДВОЙНЫХ КЛИКОВ")
    print("=" * 60)
    print(f"Порог срабатывания: {CLICK_THRESHOLD_MS} мс")
    print("Инструкции:")
    print("1. Медленно кликайте мышью - увидите нормальные клики")
    print("2. Быстро дважды кликните - должен быть обнаружен быстрый двойной клик")
    print("3. При быстром двойном клике должно появиться сообщение о подавлении")
    print("4. После подавления скрипт должен продолжать работать")
    print("5. Нажмите Ctrl+C для остановки")
    print("-" * 60)
    
    try:
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()