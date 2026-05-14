#!/usr/bin/env python3
"""
Mouse Double-Click Fixer
=======================

Эта программа фильтрует случайные двойные клики мыши, которые происходят 
слишком быстро (например, через ~70 мс после первого клика).

Как это работает:
- Отслеживает время между кликами одной и той же кнопки мыши
- Если интервал меньше порога (по умолчанию 70 мс), второй клик блокируется
- Для реальной блокировки кликов требуется запуск от имени администратора

Автор: Kilo Code
"""

import time
import threading
import sys
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70  # Порог в миллисекундах
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0  # Порог в секундах

# Состояние: время последнего клика для каждой кнопки
last_click_time = {}
lock = threading.Lock()

def on_click(x, y, button, pressed):
    """
    Обработчик событий клика мыши.
    
    Args:
        x, y: Координаты курсора
        button: Кнопка мыши (left, right, middle)
        pressed: True если нажата, False если отпущена
    
    Returns:
        bool: False чтобы заблокировать событие, True чтобы пропустить
    """
    # Обрабатываем только нажатие кнопки (не отпускание)
    if not pressed:
        return True
    
    # Получаем имя кнопки (left, right, etc.)
    button_name = getattr(button, 'name', str(button)).lower()
    
    current_time = time.time()
    
    with lock:
        # Получаем время последнего клика этой кнопки
        last_time = last_click_time.get(button_name, 0)
        time_diff = current_time - last_time
        
        # Если клик слишком быстрый после предыдущего - блокируем
        if 0 < time_diff < CLICK_THRESHOLD_S:
            print(f"[MouseFix] БЛОКИРОВКА {button_name} клика "
                  f"(интервал: {time_diff*1000:.1f} мс)")
            return False  # Блокируем событие
        
        # Обновляем время последнего клика
        last_click_time[button_name] = current_time
    
    # Пропускаем нормальные клики
    return True

def print_banner():
    """Выводит информационный баннер."""
    banner = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║              Mouse Double-Click Fixer v1.0                                 ║
    ║                                                                            ║
    ║  Эта программа блокирует случайные двойные клики мыши,                     ║
    ║  которые происходят быстрее чем {} мс после первого клика.               ║
    ║                                                                            ║
    ║  ⚠️  ВАЖНО: Для реальной блокировки кликов запустите от администратора!  ║
    ║                                                                            ║
    ║  Нажмите Ctrl+C для остановки программы                                    ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """.format(CLICK_THRESHOLD_MS)
    print(banner)

def main():
    """Основная функция программы."""
    try:
        print_banner()
        
        # Запускаем слушатель мыши
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
            
    except KeyboardInterrupt:
        print("\n\n[MouseFix] Программа остановлена пользователем")
    except Exception as e:
        print(f"\n[MouseFix] Ошибка: {e}")
        print("\nСоветы по устранению:")
        print("1. Убедитесь, что установлена библиотека pynput: pip install pynput")
        print("2. Для блокировки кликов запустите программу от имени администратора")
        print("3. На некоторых системах может потребоваться включить доступ к управлению компьютером")
        print("   в настройках конфиденциальности")

if __name__ == "__main__":
    main()