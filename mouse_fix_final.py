#!/usr/bin/env python3
"""
Mouse double-click fixer.
Filters out accidental double-clicks that occur within 70ms.
To actually block clicks, this script needs to be run as administrator.
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
            # This is a rapid double-click - suppress it
            print(f"[MouseFix] SUPPRESSED {button_name} click ({time_diff*1000:.1f}ms)")
            # Return False to block the event from reaching applications
            return False
        
        last_click_time[button_name] = current_time
    
    # Allow normal clicks through
    return True

def main():
    print("=" * 60)
    print("Mouse Double-Click Fixer")
    print("=" * 60)
    print(f"Filter threshold: {CLICK_THRESHOLD_MS}ms")
    print("This script will BLOCK rapid double-clicks.")
    print("")
    print("IMPORTANT: For actual click blocking, you MUST:")
    print("  1. Run this script as Administrator, OR")
    print("  2. Grant it accessibility/input monitoring permissions")
    print("")
    print("To run as Administrator:")
    print("  - Right-click Command Prompt -> 'Run as administrator'")
    print("  - Then navigate to this folder and run: python mouse_fix_final.py")
    print("")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        # Create mouse listener
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    except Exception as e:
        print(f"Error: {e}")
        print("")
        print("If you see a permission error, you need to run as Administrator.")
        print("On Windows, you may also need to enable:")
        print("  Settings -> Privacy & security -> Accessibility")
        print("  Then allow your terminal/IDE to control the computer.")

if __name__ == "__main__":
    main()