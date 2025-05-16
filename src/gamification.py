class LevelSystem:
    XP_LEVELS = [0, 100, 250, 500, 1000, 2000]
    THEME_UNLOCKS = {
        1: "default",
        3: "forest",
        5: "space"
    }
    
    def __init__(self, user_data):
        self.user_data = user_data
    
    def add_xp(self, amount):
        self.user_data["xp"] += amount
        self.check_level_up()
        
    def check_level_up(self):
        current_level = self.user_data["level"]
        if self.user_data["xp"] >= self.XP_LEVELS[current_level]:
            self.user_data["level"] += 1
            self.unlock_theme()
            return True
        return False
    
    def unlock_theme(self):
        new_level = self.user_data["level"]
        if new_level in self.THEME_UNLOCKS:
            theme = self.THEME_UNLOCKS[new_level]
            if theme not in self.user_data["unlocked_themes"]:
                self.user_data["unlocked_themes"].append(theme)