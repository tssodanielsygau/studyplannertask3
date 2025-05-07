import time
from rich.console import Console
from utils import load_data

console = Console()

def accuracy(typed, target):
    correct = sum(1 for t, a in zip(typed, target) if t == a)
    return round((correct / len(target)) * 100, 2)

def typing_test(words, level):
    console.print(f'Level')