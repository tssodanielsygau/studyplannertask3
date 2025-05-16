import json
from gamification import LevelSystem
from study_timer import PomodoroTimer

class StudyQuest:
    def __init__(self):
        self.load_data()
        self.level_system = LevelSystem(self.user_data)
        self.timer = PomodoroTimer()
        
    def load_data(self):
        with open('data/subjects.json') as f:
            self.subjects = json.load(f)
        with open('data/user_progress.json') as f:
            self.user_data = json.load(f)
    
    def save_progress(self):
        with open('data/user_progress.json', 'w') as f:
            json.dump(self.user_data, f, indent=2)

if __name__ == "__main__":
    app = StudyQuest()