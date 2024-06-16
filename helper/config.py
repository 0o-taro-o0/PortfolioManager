import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, config_file)
        with open(config_path) as f:
            self.config = json.load(f)