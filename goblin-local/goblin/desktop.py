import json
import threading
import time
import webbrowser
from urllib.parse import quote
import requests
import tkinter as tk
from tkinter import ttk

from .config import DEFAULT_HOTKEY, DESKTOP_CONFIG_PATH, HOST, PORT
from .ui_styles import PRIMARY_RED, DARK_RED, LIGHT_GREY, WHITE, CHARCOAL, STATUS_COLOURS

BASE_URL = f"http://{HOST}:{PORT}"

def _load_hotkey() -> str:
    try:
        with DESKTOP_CONFIG_PATH.open(encoding="utf-8") as handle:
            return (json.load(handle).get("hotkey") or DEFAULT_HOTKEY).strip().lower()
    except Exception:
        return DEFAULT_HOTKEY

def _save_hotkey(hotkey: str) -> None:
    DESKTOP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DESKTOP_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump({"hotkey": hotkey}, handle, indent=2)

def _try_import_capture_tools():
    try:
        import keyboard, pyautogui, pyperclip
        return keyboard, pyautogui, pyperclip
    except Exception:
        return None, None, None

class GoblinDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Goblin is running")
        self.root.geometry("360x150")
        self.root.configure(bg=WHITE)
        ttk.Label(self.root, text="Goblin is running", font=("Segoe UI", 14, "bold")).pack(pady=(14, 4))
        self.hotkey = _load_hotkey()
        self.hotkey_handle = None
        self.hotkey_label = ttk.Label(self.root)
        self.hotkey_label.pack()
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)
        ttk.Button(self.button_frame, text="Search manually", command=self.show_search_box).pack(side="left", padx=4)
        ttk.Button(self.button_frame, text="Set shortcut", command=self.show_hotkey_box).pack(side="left", padx=4)
        self.keyboard, self.pyautogui, self.pyperclip = _try_import_capture_tools()
        self.register_hotkey()

    def register_hotkey(self):
        self.hotkey_label.configure(text=f"Highlight text and press {self.hotkey}.")
        if not self.keyboard:
            return
        if self.hotkey_handle is not None:
            try:
                self.keyboard.remove_hotkey(self.hotkey_handle)
            except Exception:
                pass
        def callback():
            self.root.after(0, self.handle_shortcut)
        try:
            self.hotkey_handle = self.keyboard.add_hotkey(self.hotkey, callback)
        except Exception:
            self.hotkey_handle = None

    def capture_selection(self):
        if not (self.pyautogui and self.pyperclip):
            return ""
        old = self.pyperclip.paste()
        try:
            self.pyautogui.hotkey("ctrl", "c")
            time.sleep(0.15)
            return (self.pyperclip.paste() or "").strip()
        finally:
            try:
                self.pyperclip.copy(old)
            except Exception:
                pass

    def handle_shortcut(self):
        text = self.capture_selection()
        if text:
            self.show_popup(text)
        else:
            self.show_search_box()

    def lookup(self, term):
        try:
            return requests.get(f"{BASE_URL}/api/lookup", params={"q": term}, timeout=3).json()
        except Exception as exc:
            return {"query": term, "york_results": [], "general_dictionary": {"definitions": [{"part_of_speech": "error", "definition": str(exc), "examples": []}], "synonyms": []}}

    def show_hotkey_box(self):
        win = tk.Toplevel(self.root)
        win.title("Goblin shortcut")
        win.geometry("390x140")
        ttk.Label(win, text="Choose a custom shortcut, e.g. ctrl+shift+y").pack(pady=(12, 4))
        entry = ttk.Entry(win)
        entry.insert(0, self.hotkey)
        entry.pack(fill="x", padx=14)
        entry.focus_set()
        def save():
            hotkey = entry.get().strip().lower()
            if hotkey:
                self.hotkey = hotkey
                _save_hotkey(hotkey)
                self.register_hotkey()
            win.destroy()
        ttk.Button(win, text="Save shortcut", command=save).pack(pady=8)
        win.bind("<Return>", lambda _event: save())

    def show_search_box(self):
        win = tk.Toplevel(self.root)
        win.title("Goblin search")
        win.geometry("360x120")
        ttk.Label(win, text="Search Goblin").pack(pady=(12, 4))
        entry = ttk.Entry(win)
        entry.pack(fill="x", padx=14)
        entry.focus_set()
        def go():
            term = entry.get().strip()
            win.destroy()
            if term:
                self.show_popup(term)
        ttk.Button(win, text="Look up", command=go).pack(pady=8)
        win.bind("<Return>", lambda _event: go())

    def show_popup(self, term):
        data = self.lookup(term)
        win = tk.Toplevel(self.root)
        win.title("Goblin")
        win.geometry("520x560")
        win.configure(bg=WHITE)
        win.attributes("-topmost", True)
        frame = tk.Frame(win, bg=WHITE, padx=14, pady=12)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Goblin", fg=PRIMARY_RED, bg=WHITE, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(frame, text=data.get("query", term), fg=CHARCOAL, bg=WHITE, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        text = tk.Text(frame, wrap="word", height=23, bg=LIGHT_GREY, relief="flat", padx=8, pady=8)
        text.pack(fill="both", expand=True)
        text.insert("end", "York definitions\n", "heading")
        if data.get("york_results"):
            for item in data["york_results"]:
                text.insert("end", f"\n{item['term']} {item.get('full_form','')} [{item.get('status','')}]\n", "bold")
                text.insert("end", f"{item.get('plain_definition','')}\n")
                text.insert("end", f"Context: {item.get('context','')}\n")
                if item.get("source_label") or item.get("primary_action_label"):
                    text.insert("end", f"Source/action: {item.get('source_label','')} {item.get('primary_action_label','')}\n")
        else:
            text.insert("end", "No York-specific entry yet.\n")
        text.insert("end", "\nGeneral dictionary\n", "heading")
        gd = data.get("general_dictionary", {})
        for definition in gd.get("definitions", []):
            text.insert("end", f"\n{definition.get('part_of_speech')}: {definition.get('definition')}\n")
        if gd.get("synonyms"):
            text.insert("end", "\nSynonyms: " + ", ".join(gd["synonyms"]) + "\n")
        if data.get("word_definitions"):
            text.insert("end", "\nDefinitions for selected words\n", "heading")
            for word_data in data["word_definitions"]:
                text.insert("end", f"\n{word_data.get('term', '')}\n", "bold")
                defs = word_data.get("definitions", [])
                if defs:
                    for definition in defs[:2]:
                        text.insert("end", f"{definition.get('part_of_speech')}: {definition.get('definition')}\n")
                else:
                    text.insert("end", "No general dictionary definition found.\n")
        text.tag_config("heading", foreground=DARK_RED, font=("Segoe UI", 11, "bold"))
        text.tag_config("bold", font=("Segoe UI", 10, "bold"))
        text.configure(state="disabled")
        buttons = tk.Frame(frame, bg=WHITE)
        buttons.pack(fill="x", pady=(10, 0))
        safe = quote(data.get("query") or term)
        for label, url in (("Open full entry", f"{BASE_URL}/entry/{safe}"), ("Submit York definition", f"{BASE_URL}/submit?term={safe}"), ("Request definition", f"{BASE_URL}/request-definition?term={safe}")):
            ttk.Button(buttons, text=label, command=lambda u=url: webbrowser.open(u)).pack(side="left", padx=(0, 5))
        ttk.Button(buttons, text="Close", command=win.destroy).pack(side="right")

    def run(self):
        self.root.mainloop()

def run_desktop() -> None:
    GoblinDesktop().run()
