import os
import re

from .Basecontroller import Basecontroller
from helpers.config import get_settings
from .Projectcontroller import ProjectController
from fastapi import UploadFile
from models import ResponseSignal

class DataController(Basecontroller):

    def __init__(self):
        super().__init__(get_settings())
        self.size_scale = 1024 * 1024

    def validate_upload_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value

        if file.size > self.app_settings.FILE_MAX_SIZE_MB * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDS_LIMIT.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    
    def generate_unique_file_path(self, original_filename: str, project_id: str):
        random_key = self.generate_random_string()
        project_path=ProjectController().get_project_path(project_id=project_id)
        clean_filename = self.get_clean_file_name(original_filename=original_filename)
        new_file_path = os.path.join(project_path,random_key + '_' + clean_filename)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(project_path,random_key + '_' + clean_filename)

        return new_file_path, random_key + '_' + clean_filename
    
    def get_clean_file_name(self, original_filename: str):
        clean_filename = re.sub(r'[^\w.]', '', original_filename.strip())
        clean_filename = clean_filename.replace(' ', '_')
        return clean_filename