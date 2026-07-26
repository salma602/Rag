from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from helpers.config import get_settings, Settings
from controllers.Basecontroller import Basecontroller
from controllers.DataController import DataController
from controllers.Projectcontroller import ProjectController
from controllers.ProcessController import ProcessController

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)
@data_router.post("/upload/{id}")
async def upload_data(id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    #validate file extension
    data_controller_obj= DataController()
    isvalid, result_signsl=data_controller_obj.validate_upload_file(file=file)

    if not isvalid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "isvalid": isvalid,
                "result_signsl": result_signsl
            }
        )
    project_dir_path=ProjectController().get_project_path(project_id=id)
    file_path, file_id=data_controller_obj.generate_unique_file_path(original_filename=file.filename, project_id=id)

    try:

        async with aiofiles.open(file_path, 'wb') as f:
            while chunk:= await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "isvalid": False,
                "result_signsl": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )           
    return JSONResponse(
                content={
                    "isvalid": isvalid,
                    "result_signsl": ResponseSignal.FILE_SUCCESS_UPLOADED.value,
                    "file_id": file_id,
                }
            )

@data_router.post("/process/{id}")
async def process_endpoint(id: str, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller_obj = ProcessController(project_id=id)
    file_content = process_controller_obj.get_file_content(file_id=file_id)
    file_chunks = process_controller_obj.process_file_content(file_id=file_id, chunk_size=chunk_size, overlap_size=overlap_size, file_content=file_content)

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "isvalid": False,
                "result_signsl": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    return file_chunks
