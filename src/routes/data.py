from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
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
from models.ProjectModel import ProjectModel
from models.db_schems import DataChunk
from models.ChunkModel import ChunkModel

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)
@data_router.post("/upload/{id}")
async def upload_data(request: Request, id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    project_model = ProjectModel(db_client=request.app.mongodb_client)
    project=await project_model.get_project_or_create_one(project_id=id)


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
                    "project_id": str(project.id)
                }
            )

@data_router.post("/process/{id}")
async def process_endpoint(request: Request, id: str, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = ProjectModel(db_client=request.app.mongodb_client)   
    project=await project_model.get_project_or_create_one(project_id=id)


    process_controller_obj = ProcessController(project_id=id)
    print("file_id:", file_id)
    file_content = process_controller_obj.get_file_content(file_id=file_id)
    print("file_content:", file_content)
    file_chunks = process_controller_obj.process_file_content(file_id=file_id, chunk_size=chunk_size, overlap_size=overlap_size, file_content=file_content)

    print("chunks:", file_chunks)
    print("number of chunks:", len(file_chunks) if file_chunks else 0)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "isvalid": False,
                "result_signsl": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(
        db_client=request.app.mongodb_client
    )

    if do_reset ==1:
        _= await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    count = await chunk_model.collection.count_documents({})
    print("Documents in collection:", count)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
