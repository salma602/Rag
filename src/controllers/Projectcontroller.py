from .Basecontroller import Basecontroller
from models import ResponseSignal
from fastapi import UploadFile
from helpers.config import get_settings
import os
class ProjectController(Basecontroller):

    def __init__(self):
        super().__init__(get_settings())

    def get_project_path(self, project_id: str):
        project_dir=os.path.join(self.files_dir, project_id)        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir