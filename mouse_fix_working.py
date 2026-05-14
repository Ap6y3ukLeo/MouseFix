#!/usr/bin/env python3
"""
Working mouse double-click fixer.
Uses pynput to monitor and suppress rapid clicks.
Note: For actual suppression, this needs to run with administrator privileges.
"""

import time
import threading
from pynput import mouse

# Configuration
CLICK_THRESHOLD_MS = 70  # Ignore second click if within this time
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0

# State
last_click_time = {}
click_count = {}
lock = threading.Lock()

def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    if not pressed:
        return
    
    button_name = str(button).name  # Get 'left' or 'right'
    current_time = time.time()
    
    with lock:
        last_time = last_click_time.get(button_name, 0)
        time_diff = current_time - last_time
        
        # Update click count
        click_count[button_name] = click_count.get(button_name, 0) + 1
        
        if time_diff < CLICK_THRESHOLD_S and time_diff > 0:
            # This is a rapid double-click - suppress it by consuming the event
            print(f"[MouseFix] Suppressed {button_name} click #{click_count[button_name]} ({time_diff*1000:.1f}ms)")
            # Return False to block the event
            return False
        
        last_click_time[button_name] = current_time
    
    return True

def main():
    print(f"MouseFix started - filtering clicks within {CLICK_THRESHOLD_MS}ms")
    print("Note: For actual click suppression, run as administrator")
    print("Press Ctrl+C to stop")
    
    # Create mouse listener
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    main()