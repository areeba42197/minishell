import tkinter as tk
from tkinter import scrolledtext
import shlex
import os
from shell_core import ShellCore

class ShellUI:
    def __init__(self, master):
        self.logic = ShellCore()
        self.window = master
        self.window.title("Mini Shell -  ❤")

        self.display = scrolledtext.ScrolledText(
    master,
    wrap=tk.WORD,
    width=100,
    height=30,
    bg="#ffe6f0",             # Light pink background
    fg="#ff1493",             # Shocking pink text
    font=("Courier New", 12, "bold"),
    insertbackground="#ff69b4",  # Cursor color (hot pink)
    undo=True
)

        self.display.pack(padx=10, pady=10)
        self.display.insert(tk.END, self.get_prompt())

        self.display.bind("<Return>", self.run)
        self.display.bind("<Up>", self.prev)
        self.display.bind("<Down>", self.next)
        self.display.bind("<Tab>", self.complete)

        self.cmd_pos = self.display.index("insert")
        self.last_suggest = {"prefix": "", "items": [], "pos": 0}

    def get_prompt(self):
        cwd = os.path.basename(self.logic.path)
        return f"IIUI-Shell:{cwd}$ "

    def run(self, event=None):
        cmd = self.display.get(self.cmd_pos, tk.END).strip()
        self.display.insert(tk.END, "\n")

        def show(res):
            self.display.insert(tk.END, res + "\n")
            self.display.insert(tk.END, self.get_prompt())
            self.display.see(tk.END)
            self.cmd_pos = self.display.index("insert")

        res = self.logic.process(cmd, cb=show)
        if res and not cmd.endswith("&"):
            show(res)
        elif res:
            self.display.insert(tk.END, res + "\n")
            self.display.insert(tk.END, self.get_prompt())
            self.cmd_pos = self.display.index("insert")
        return "break"

    def prev(self, event=None):
        if self.logic.history:
            self.logic.index = max(0, self.logic.index - 1)
            self._replace_line(self.logic.history[self.logic.index])
        return "break"

    def next(self, event=None):
        if self.logic.history:
            self.logic.index = min(len(self.logic.history) - 1, self.logic.index + 1)
            self._replace_line(self.logic.history[self.logic.index])
        return "break"

    def _replace_line(self, text):
        self.display.delete(self.cmd_pos, tk.END)
        self.display.insert(tk.END, text)

    def complete(self, event=None):
        line = self.display.get(self.cmd_pos, tk.END).strip()
        try:
            parts = shlex.split(line)
        except:
            return "break"
        if not parts:
            return "break"

        current = parts[-1]

        if self.last_suggest["prefix"] == current and self.last_suggest["items"]:
            self.last_suggest["pos"] = (self.last_suggest["pos"] + 1) % len(self.last_suggest["items"])
            choice = self.last_suggest["items"][self.last_suggest["pos"]]
        else:
            try:
                items = [x for x in os.listdir('.') if x.startswith(current)]
                if not items:
                    return "break"
                self.last_suggest = {"prefix": current, "items": items, "pos": 0}
                choice = items[0]
            except:
                return "break"

        updated = " ".join(parts[:-1] + [choice])
        self._replace_line(updated)
        return "break"
