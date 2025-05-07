import json

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)