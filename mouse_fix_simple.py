#!/usr/bin/env python3
"""
Simple mouse double-click detector and logger.
Shows the concept of filtering rapid clicks.
For actual suppression, this would need to run with higher privileges
or use a driver-level solution.
"""

import time
import threading
from pynput import mouse

# Configuration
CLICK_THRESHOLD_MS = 70  # Ignore second click if within this time
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0

# State
last_click_time = {}
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
        
        if time_diff < CLICK_THRESHOLD_S and time_diff > 0:
            # This is a rapid double-click
            print(f"[MouseFix] DETECTED rapid {button_name} click ({time_diff*1000:.1f}ms)")
            print(f"[MouseFix] In a real suppressor, this click would be BLOCKED")
            # In a real suppressor, we would return False here to block the event
            # But for demonstration, we just log it
        else:
            print(f"[MouseFix] Normal {button_name} click")
        
        last_click_time[button_name] = current_time
    
    # For demonstration, we allow all clicks through
    # In a real suppressor, rapid clicks would return False to block
    return True

def main():
    print("=" * 50)
    print("Mouse Double-Click Fixer - DEMONSTRATION VERSION")
    print("=" * 50)
    print(f"Filter threshold: {CLICK_THRESHOLD_MS}ms")
    print("This version LOGGES rapid clicks but does NOT block them.")
    print("For actual blocking, you would need:")
    print("  1. To run this as administrator, OR")
    print("  2. A driver-level solution, OR")
    print("  3. Windows accessibility hooks with proper privileges")
    print("-" * 50)
    print("Move your mouse and click to see the output.")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Create mouse listener
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    main()