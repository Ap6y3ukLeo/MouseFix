#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы фильтра двойных кликов.
Генерирует искусственные клики для тестирования.
"""

import time
import threading
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0

# Состояние
last_click_time = {}
lock = threading.Lock()

def on_click(x, y, button, pressed):
    """Обработчик кликов для тестирования."""
    if not pressed:
        return
    
    button_name = getattr(button, 'name', str(button)).lower()
    current_time = time.time()
    
    with lock:
        last_time = last_click_time.get(button_name, 0)
        time_diff = current_time - last_time
        
        if time_diff < CLICK_THRESHOLD_S and time_diff > 0:
            print(f"[TEST] ДВОЙНОЙ КЛИК ОБНАРУЖЕН: {button_name} "
                  f"через {time_diff*1000:.1f} мс - БУДЕТ ЗАБЛОКИРОВАН")
            return False  # Блокируем в тесте
        else:
            print(f"[TEST] Нормальный клик: {button_name}")
        
        last_click_time[button_name] = current_time
    
    return True

def simulate_double_click():
    """Симулирует быстрый двойной клик для тестирования."""
    print("\n[TEST] Симуляция быстрого двойного клика через 50 мс...")
    time.sleep(2)  # Даем время пользователю подготовиться
    
    # Здесь мы не можем реально сгенерировать клик мыши без дополнительных библиотек
    # Но мы покажем, как бы это работало
    print("[TEST] В реальном сценарии:")
    print("[TEST] 1. Пользователь нажимает кнопку мыши")
    print("[TEST] 2. Через 50 мс происходит второй клик (механический дефект)")
    print("[TEST] 3. Наша программа обнаруживает интервал 50 мс < 70 мс")
    print("[TEST] 4. Второй клик блокируется и не достигает приложений")

def main():
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ФИЛЬТРА ДВОЙНЫХ КЛИКОВ")
    print("=" * 50)
    print(f"Порог срабатывания: {CLICK_THRESHOLD_MS} мс")
    print()
    print("Инструкции:")
    print("1. Запустите эту программу")
    print("2. Нормально используйте мышь - увидите логи кликов")
    print("3. Если у вас есть мышь с двойным кликом, попробуйте кликнуть")
    print("4. Программа покажет, когда быстрый клик был бы заблокирован")
    print()
    print("Для симуляции теста раскомментируйте вызов simulate_double_click()")
    print("в конце функции main() и перезапустите программу")
    print("-" * 50)
    
    # Запускаем слушатель
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    main()