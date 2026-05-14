#!/usr/bin/env python3
"""
Mouse Double-Click Fixer с правильной блокировкой событий
Блокирует оба события (нажатие и отпускание) второго клика в быстрой паре
"""

import time
import threading
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70  # Порог в миллисекундах
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0  # Порог в секундах

# Состояние
last_click_time = {}          # Время последнего нажатия для каждой кнопки
buttons_pressed = set()       # Нажатые кнопки в данный момент
suppress_next_release = set() # Кнопки, для которых нужно подавить отпускание
click_counter = {}            # Счетчик кликов для статистики
suppress_counter = {}         # Счетчик подавленных кликов
lock = threading.Lock()

def on_click(x, y, button, pressed):
    """Обработчик событий нажатия/отпускания кнопки мыши."""
    button_name = getattr(button, 'name', str(button))
    
    with lock:
        current_time = time.time()
        
        if pressed:
            # Обрабатываем нажатие кнопки
            click_counter[button_name] = click_counter.get(button_name, 0) + 1
            
            last_time = last_click_time.get(button_name, 0)
            time_diff = current_time - last_time
            
            # Проверяем, является ли это быстрым вторым нажатием
            if 0 < time_diff < CLICK_THRESHOLD_S:
                # Это быстрый двойной клик - блокируем это нажатие
                suppress_counter[button_name] = suppress_counter.get(button_name, 0) + 1
                print(f"[MouseFix] ПОДАВЛЕНО нажатие {button_name} (быстрый двойной клик, интервал: {time_diff*1000:.1f} мс)")
                
                # Помечаем, что нужно также подавить следующее отпускание этой кнопки
                suppress_next_release.add(button_name)
                return False  # Блокируем событие нажатия
            else:
                # Нормальное нажатие - разрешаем
                last_click_time[button_name] = current_time
                buttons_pressed.add(button_name)
                print(f"[MouseFix] Нормальное нажатие {button_name}")
                return True
        else:
            # Обрабатываем отпускание кнопки
            if button_name in suppress_next_release:
                # Это отпускание нужно подавить (оно принадлежит быстрому двойному клику)
                suppress_next_release.discard(button_name)
                print(f"[MouseFix] ПОДАВЛЕНО отпускание {button_name} (часть быстрого двойного клика)")
                buttons_pressed.discard(button_name)
                return False  # Блокируем событие отпускания
            else:
                # Нормальное отпускание
                buttons_pressed.discard(button_name)
                print(f"[MouseFix] Нормальное отпускание {button_name}")
                return True

def print_instructions():
    """Выводит инструкции по использованию."""
    print("=" * 60)
    print("Mouse Double-Click Fixer - Правильная блокировка")
    print("=" * 60)
    print(f"Порог срабатывания: {CLICK_THRESHOLD_MS} мс")
    print("Программа блокирует ОБА события (нажатие и отпускание) второго клика")
    print("в быстрой паре, чтобы предотвратить регистрацию двойного клика ОС.")
    print()
    print("Инструкции:")
    print("1. Медленно кликайте мышью - увидите нормальные нажатия и отпускания")
    print("2. Быстро дважды кликните - должно быть обнаружено и подавлено")
    print("3. При быстром двойном клике вы увидите сообщения о подавлении")
    print("   как нажатия, так и отпускания второй кнопки")
    print("4. После подавления программа должна продолжать работать")
    print("5. Нажмите Ctrl+C для остановки")
    print("-" * 60)

def main():
    print_instructions()
    
    try:
        # Запускаем слушатель мыши
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\n\n[MouseFix] Программа остановлена пользователем")
        print(f"Статистика: {dict(click_counter)} кликов, {dict(suppress_counter)} подавлено")
    except Exception as e:
        print(f"\n[MouseFix] Ошибка: {e}")

if __name__ == "__main__":
    main()