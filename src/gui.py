import tkinter as tk
from tkinter import ttk

class StudyQuestGUI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("StudyQuest")
        ttk.Label(self.root, text="Select Subject:").pack()
        for subject in self.app.subjects["subjects"]:
            ttk.Button(
                self.root,
                text=subject["name"],
                command=lambda s=subject: self.start_session(s)
            ).pack()
    
    def start_session(self, subject):
        print(f"Starting {subject['name']} session!")