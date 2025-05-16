import time
from gamification import LevelSystem

class PomodoroTimer:
    def __init__(self):
        self.work_duration = 25 * 60  # 25 minutes
        self.break_duration = 5 * 60   # 5 minutes
    
    def start_session(self, subject, callback):
        print(f"Starting study session for {subject}!")
        time.sleep(self.work_duration)  # In real app, use proper timer
        callback(xp_earned=50, subject=subject)