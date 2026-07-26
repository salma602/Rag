from helpers.config import get_settings, Settings
import os
import random
import string
class Basecontroller:
    def __init__(self, app_settings: Settings):
        self.app_settings = app_settings    
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, "assets/files")

    def generate_random_string(self, length: int = 12):
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))