#!/usr/bin/env python3
"""
Debug version of mouse double-click fixer.
"""

import time
import ctypes
from ctypes import wintypes
import threading

# Windows API constants
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MOUSEMOVE = 0x0200

# Configuration
CLICK_THRESHOLD_MS = 70
CLICK_THRESHOLD_S = CLICK_THRESHOLD_MS / 1000.0

# State
last_click_time = {}
lock = threading.Lock()

# Load DLLs
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Define structures
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

# Hook procedure type
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))

# Global hook ID
hook_id = None

def get_button_from_msg(msg):
    """Map Windows message to button identifier."""
    if msg in (WM_LBUTTONDOWN, WM_LBUTTONUP):
        return "left"
    elif msg in (WM_RBUTTONDOWN, WM_RBUTTONUP):
        return "right"
    return None

def low_level_mouse_proc(nCode, wParam, lParam):
    """Low-level mouse hook callback."""
    global hook_id
    
    # Always call next hook
    result = user32.CallNextHookEx(hook_id, nCode, wParam, lParam)
    
    if nCode >= 0:
        msg = wParam
        button = get_button_from_msg(msg)
        
        # Log all mouse events for debugging
        if msg in (WM_LBUTTONDOWN, WM_LBUTTONUP, WM_RBUTTONDOWN, WM_RBUTTONUP):
            action = "down" if msg in (WM_LBUTTONDOWN, WM_RBUTTONDOWN) else "up"
            print(f"[DEBUG] Mouse {button} {action} at {time.time()}")
            
            if button and msg in (WM_LBUTTONDOWN, WM_LBUTTONUP, WM_RBUTTONDOWN, WM_RBUTTONUP):
                current_time = time.time()
                
                with lock:
                    last_time = last_click_time.get(button, 0)
                    time_diff = current_time - last_time
                    
                    print(f"[DEBUG] {button} click diff: {time_diff*1000:.1f}ms")
                    
                    if time_diff < CLICK_THRESHOLD_S and time_diff > 0:
                        # Suppress this rapid click
                        print(f"[MouseFix] Would suppress {button} click ({time_diff*1000:.1f}ms)")
                        # In real version, we would return 1 here to block
                        # But for debug, we just log and let it through
                    else:
                        last_click_time[button] = current_time
    
    return result

def main():
    global hook_id
    
    print("MouseFix Debug started")
    print("Press Ctrl+C to stop")
    
    # Get module handle
    h_module = kernel32.GetModuleHandleW(None)
    print(f"Module handle: {h_module}")
    if not h_module:
        print("Failed to get module handle!")
        return
    
    # Create hook procedure
    hook_proc = HOOKPROC(low_level_mouse_proc)
    print("Hook procedure created")
    
    # Set up the hook
    hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, hook_proc, h_module, 0)
    
    if not hook_id:
        error = kernel32.GetLastError()
        print(f"Failed to install mouse hook! Error: {error}")
        return
    else:
        print(f"Hook installed successfully! Hook ID: {hook_id}")
    
    # Message loop
    msg = wintypes.MSG()
    try:
        print("Entering message loop...")
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if hook_id:
            user32.UnhookWindowsHookEx(hook_id)
            print("Hook uninstalled")

if __name__ == "__main__":
    main()