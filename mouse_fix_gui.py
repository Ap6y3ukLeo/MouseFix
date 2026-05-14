#!/usr/bin/env python3
import json, os, sys, time, ctypes, threading
from ctypes import wintypes
import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray

WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
user32 = ctypes.WinDLL('user32', use_last_error=True)

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM,
                              ctypes.POINTER(MSLLHOOKSTRUCT))

class State:
    threshold_ms = 100
    last_press = {}
    total = {}
    blocked = {}
    hook_id = None
    running = False
    proc_ref = None

state = State()

def hook_callback(nCode, wParam, lParam):
    if nCode >= 0:
        btn = {WM_LBUTTONDOWN: "left", WM_RBUTTONDOWN: "right"}.get(wParam)
        if btn:
            now = time.time()
            last = state.last_press.get(btn, 0)
            diff = now - last
            state.total[btn] = state.total.get(btn, 0) + 1
            if 0 < diff < state.threshold_ms / 1000.0:
                state.blocked[btn] = state.blocked.get(btn, 0) + 1
                return 1
            state.last_press[btn] = now
    return user32.CallNextHookEx(state.hook_id, nCode, wParam, lParam)

# Config - рядом с EXE или в APPDATA
try:
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
except:
    script_dir = os.path.expanduser("~")
CONFIG_FILE = os.path.join(script_dir, "fixer_config.json")
# Если не можем писать рядом - используем UserProfile
try:
    with open(CONFIG_FILE, "a") as f: pass
except:
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mousefix_config.json")

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            d = json.load(f)
            return d.get("threshold", 100)
    except:
        return 100

def save_config(val):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"threshold": val}, f)
    except:
        pass

def create_tray_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#5B5BFF")
    draw.ellipse([16, 16, 48, 48], fill="#7C7CFF")
    draw.polygon([24, 22, 30, 42, 38, 18, 44, 40, 50, 24, 54, 34],
                 fill="#FFFFFF33")
    draw.rectangle([26, 28, 38, 36], fill="#FFFFFFCC")
    return img

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("MouseFix")
        start_val = load_config()
        self.root.geometry("420x640")
        self.root.resizable(True, True)
        self.root.minsize(380, 560)
        self.root.configure(fg_color="#0A0A0F")
        
        self.val = start_val
        state.threshold_ms = start_val
        self.is_on = state.running
        self.tray_icon = None
        self.tray_thread = None
        
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.build()
        
        # Запускаем трей
        self.setup_tray()
        
    def setup_tray(self):
        def on_show(icon, item):
            self.show_window()
        def on_exit(icon, item):
            icon.stop()
            self.root.after(100, self.real_quit)
        
        menu = pystray.Menu(
            pystray.MenuItem("Показать", on_show, default=True),
            pystray.MenuItem("Выход", on_exit)
        )
        img = create_tray_icon()
        self.tray_icon = pystray.Icon("mousefix", img, "MouseFix", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()
    
    def hide_window(self):
        self.root.withdraw()
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def real_quit(self):
        if state.hook_id:
            user32.UnhookWindowsHookEx(state.hook_id)
        self.root.destroy()
    
    def build(self):
        main = ctk.CTkFrame(self.root, fg_color="#0D0D14", corner_radius=12,
                           border_width=1, border_color="#1E1E2A")
        main.pack(fill="both", expand=True, padx=12, pady=12)
        
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(16, 20))
        
        glass = ctk.CTkFrame(content, fg_color="#13131F", corner_radius=16,
                            border_width=1, border_color="#1E1E2E")
        glass.pack(fill="both", expand=True)
        
        # Toggle
        tf = ctk.CTkFrame(glass, fg_color="transparent")
        tf.pack(fill="x", padx=24, pady=(28, 4))
        ctk.CTkLabel(tf, text="Блокировка", font=("Segoe UI", 15, "bold"),
                    text_color="#E8E8F0").pack(side="left")
        self.switch = ctk.CTkSwitch(tf, text="", command=self.toggle,
                                   progress_color="#5B5BFF", fg_color="#2A2A3A",
                                   button_color="#E8E8F0",
                                   switch_height=26, switch_width=44)
        self.switch.pack(side="right")
        if state.running:
            self.switch.select()
        
        self.status_light = ctk.CTkLabel(glass, text="○  Выключено",
                                        font=("Segoe UI", 12), text_color="#6B6B80")
        self.status_light.pack(padx=24, pady=(4, 16), anchor="w")
        if state.running:
            self.status_light.configure(text="●  Активно", text_color="#5B5BFF")
        
        ctk.CTkFrame(glass, fg_color="#1A1A2A", height=1).pack(fill="x", padx=24)
        
        # Slider
        ctk.CTkLabel(glass, text="Порог срабатывания", font=("Segoe UI", 13, "bold"),
                    text_color="#D0D0E0").pack(padx=24, pady=(20, 2), anchor="w")
        ctk.CTkLabel(glass, text="Интервал между кликами для блокировки",
                    font=("Segoe UI", 10), text_color="#6B6B80").pack(padx=24, pady=(0, 14), anchor="w")
        
        sf = ctk.CTkFrame(glass, fg_color="transparent")
        sf.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkLabel(sf, text="10", font=("Segoe UI", 11), text_color="#6B6B80").pack(side="left", padx=(0, 4))
        self.slider = ctk.CTkSlider(sf, from_=10, to=300,
                                   fg_color="#1E1E2E", progress_color="#5B5BFF",
                                   button_color="#5B5BFF", button_hover_color="#7C7CFF",
                                   height=4, button_length=16, command=self.on_slide)
        self.slider.set(self.val)
        self.slider.pack(side="left", fill="x", expand=True, padx=4)
        ctk.CTkLabel(sf, text="300", font=("Segoe UI", 11), text_color="#6B6B80").pack(side="left", padx=(4, 0))
        
        # Value
        vf = ctk.CTkFrame(glass, fg_color="transparent")
        vf.pack(padx=24, pady=(12, 20))
        self.val_display = ctk.CTkLabel(vf, text=f"{self.val} мс",
                                       font=("Segoe UI", 32, "bold"), text_color="#F0F0FF")
        self.val_display.pack(side="left", padx=(0, 12))
        ec = ctk.CTkFrame(vf, fg_color="#1A1A28", corner_radius=10,
                         border_width=1, border_color="#2A2A3A")
        self.entry = ctk.CTkEntry(ec, placeholder_text="мс", width=80,
                                 font=("Segoe UI", 13, "bold"), justify="center",
                                 fg_color="transparent", border_width=0, text_color="#D0D0E0")
        self.entry.pack(padx=12, pady=6)
        self.entry.bind("<Return>", self.entry_apply)
        ec.pack(side="left")
        
        # Presets
        pf = ctk.CTkFrame(glass, fg_color="transparent")
        pf.pack(padx=24, pady=(0, 24))
        for label, v in [("Быстрый", 30), ("Обычный", 70), ("Средний", 100), ("Медленный", 150), ("Тест", 300)]:
            btn = ctk.CTkButton(pf, text=label, width=60, height=28,
                              font=("Segoe UI", 11), corner_radius=8,
                              fg_color="#1A1A28", hover_color="#2A2A3A",
                              text_color="#A0A0B8", border_width=1, border_color="#2A2A3A",
                              command=lambda x=v: self.set_val(x))
            btn.pack(side="left", padx=(0, 4))
        
        # Stats
        sc = ctk.CTkFrame(glass, fg_color="#0D0D18", corner_radius=12)
        sc.pack(fill="x", padx=24, pady=(0, 24))
        self.total_label = ctk.CTkLabel(sc, text="Всего кликов — 0",
                                       font=("Segoe UI", 12), text_color="#6B6B80")
        self.total_label.pack(padx=16, pady=(12, 2), anchor="w")
        self.blocked_label = ctk.CTkLabel(sc, text="Подавлено — 0",
                                         font=("Segoe UI", 12), text_color="#6B6B80")
        self.blocked_label.pack(padx=16, pady=(2, 2), anchor="w")
        self.rate_label = ctk.CTkLabel(sc, text="Эффективность — 0%",
                                      font=("Segoe UI", 12), text_color="#5B5BFF")
        self.rate_label.pack(padx=16, pady=(2, 12), anchor="w")
        
        self.upd()
    
    def on_slide(self, v):
        self.val = int(v)
        self.val_display.configure(text=f"{self.val} мс")
        if state.running:
            state.threshold_ms = self.val
        save_config(self.val)
    
    def entry_apply(self, e=None):
        try:
            v = int(self.entry.get())
            self.val = max(10, min(300, v))
            self.slider.set(self.val)
            self.val_display.configure(text=f"{self.val} мс")
            if state.running:
                state.threshold_ms = self.val
            save_config(self.val)
        except:
            pass
        self.root.focus()
    
    def set_val(self, v):
        self.val = v
        self.slider.set(v)
        self.val_display.configure(text=f"{v} мс")
        if state.running:
            state.threshold_ms = v
        save_config(v)
    
    def toggle(self):
        if not self.switch.get():
            self.is_on = False
            if state.hook_id:
                user32.UnhookWindowsHookEx(state.hook_id)
                state.hook_id = None
            state.running = False
            state.proc_ref = None
            self.status_light.configure(text="○  Выключено", text_color="#6B6B80")
            return
        state.threshold_ms = self.val
        proc = HOOKPROC(hook_callback)
        state.proc_ref = proc
        hid = user32.SetWindowsHookExW(WH_MOUSE_LL, proc, 0, 0)
        if hid:
            state.hook_id = hid
            state.running = True
            self.is_on = True
            self.status_light.configure(text="●  Активно", text_color="#5B5BFF")
        else:
            self.switch.deselect()
            self.status_light.configure(text="✕  Ошибка — нужны права администратора", text_color="#FF4757")
    
    def upd(self):
        b = sum(state.blocked.values())
        t = sum(state.total.values())
        rate = int(b * 100 / t) if t > 0 else 0
        self.total_label.configure(text=f"Всего кликов — {t}")
        self.blocked_label.configure(text=f"Подавлено — {b}")
        self.rate_label.configure(text=f"Эффективность — {rate}%")
        self.root.after(500, self.upd)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    App().run()