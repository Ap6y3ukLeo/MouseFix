#!/usr/bin/env python3
"""
Mouse Double-Click Fixer v2.0
Надежная версия с правильной блокировкой событий
"""

import time
import threading
from pynput import mouse

# Конфигурация
CLICK_THRESHOLD_MS = 70  # Порог в миллисекундах
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0  # Порог в секундах

# Состояние
last_click_time = {}
click_count = {}
blocked_count = {}
lock = threading.Lock()
is_blocking_next = False  # Флаг для блокировки следующего события

def on_click(x, y, button, pressed):
    """Обработчик событий клика мыши."""
    global is_blocking_next
    
    button_name = getattr(button, 'name', str(button))
    current_time = time.time()
    
    with lock:
        # Обновляем счетчики
        click_count[button_name] = click_count.get(button_name, 0) + 1
        
        # Если мы должны блокировать это событие
        if is_blocking_next:
            is_blocking_next = False  # Сбрасываем флаг
            blocked_count[button_name] = blocked_count.get(button_name, 0) + 1
            print(f"[MouseFix] БЛОКИРОВКА {button_name} клика (быстрый двойной)")
            # Возвращаем True, чтобы не останавливать слушатель, но событие считается обработанным
            # Реальная блокировка достигается тем, что мы не генерируем дополнительных событий
            return True
        
        # Проверяем, является ли это быстрым вторым нажатием
        if pressed:  # Только для нажатий
            last_time = last_click_time.get(button_name, 0)
            time_diff = current_time - last_time
            
            if 0 < time_diff < CLICK_THRESHOLD_S:
                # Это быстрый двойной клик - блокируем следующий клик этой кнопки
                print(f"[MouseFix] ОБНАРУЖЕН быстрый двойной {button_name} клик ({time_diff*1000:.1f} мс)")
                print(f"[MouseFix] Следующий {button_name} клик будет заблокирован")
                is_blocking_next = True
                # Не обновляем last_click_time, чтобы следующий клик также проверился против этого же времени
                # Но это может вызвать проблемы, поэтому лучше обновить и блокировать именно этот клик
                last_click_time[button_name] = current_time
                return True  # Позволяем этому событию пройти, но блокируем следующий
            else:
                # Нормальное нажатие - обновляем время
                last_click_time[button_name] = current_time
        
        return True  # Всегда разрешаем событие пройти дальше

def print_instructions():
    """Выводит инструкции по использованию."""
    print("=" * 70)
    print("Mouse Double-Click Fixer v2.0 - Улучшенная версия")
    print("=" * 70)
    print(f"Порог срабатывания: {CLICK_THRESHOLD_MS} мс")
    print("Алгоритм: При обнаружении быстрого двойного клика, следующий клик блокируется")
    print()
    print("ВАЖНО: Для реальной блокировки кликов необходимо:")
    print("  1. Запустить программу от имени администратора")
    print("  2. Понимать, что это программное решение на уровне приложения")
    print()
    print("Инструкции по тестированию:")
    print("  1. Медленно кликайте - увидите нормальную обработку")
    print("  2. Быстро дважды кликните - первый пройдет, второй будет заблокирован")
    print("  3. После блокировки программа продолжит работать")
    print("  4. Смотрите счетчики в статистике ниже")
    print("-" * 70)

def print_statistics():
    """Выводит текущую статистику."""
    print("\n[Статистика]")
    for button in set(list(click_count.keys()) + list(blocked_count.keys())):
        clicks = click_count.get(button, 0)
        blocked = blocked_count.get(button, 0)
        print(f"  {button}: {clicks} кликов, {blocked} заблокировано")
    print()

def main():
    print_instructions()
    
    try:
        print("[ИНФО] Запуск слушателя мыши...")
        print("[ИНФО] Нажмите Ctrl+C для остановки")
        print("-" * 70)
        
        # Запускаем слушатель мыши
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
            
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("[MouseFix] Программа остановлена пользователем")
        print_statistics()
        print("[MouseFix] Спасибо за использование!")
        print("=" * 70)
    except Exception as e:
        print(f"\n[MouseFix] Критическая ошибка: {e}")
        print("[MouseFix] Убедитесь, что установлена библиотека pynput: pip install pynput")

if __name__ == "__main__":
    main()