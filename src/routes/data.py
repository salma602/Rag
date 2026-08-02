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
from models.db_schems import DataChunk, Asset
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum  import AssetTypeEnum
logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)
@data_router.post("/upload/{id}")
async def upload_data(request: Request, id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    project_model =await ProjectModel.create_instance(db_client=request.app.mongodb_client)
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
    print("file_path =", file_path)
    print("file_id =", file_id)
    print("original filename =", file.filename)

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

    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),

    )

    asset_record= await asset_model.create_asset(asset=asset_resource)
    return JSONResponse(
        content={
            "isvalid": isvalid,
            "result_signsl": ResponseSignal.FILE_SUCCESS_UPLOADED.value,
            "file_id": asset_record.asset_name,
            "project_id": str(project.id)
        }
    )

@data_router.post("/process/{id}")
async def process_endpoint(request: Request, id: str, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)   

    project=await project_model.get_project_or_create_one(project_id=id)
    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)


    project_files_ids={}
    if process_request.file_id:
        assest_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=file_id)
        if assest_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "isvalid": False,
                    "result_signsl": ResponseSignal.FILE_ID_ERROR.value
                }
            )
        project_files_ids = {assest_record.id: assest_record.asset_name}
    else:
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.id, asset_type=AssetTypeEnum.FILE.value)
        project_files_ids = {
            record.id: record.asset_name for record in project_files}

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "isvalid": False,
                "result_signsl": ResponseSignal.NO_FILES_FOUND_FOR_PROCESSING.value
            }
        )


    process_controller_obj = ProcessController(project_id=id)

    no_records=0
    no_files=0
    chunk_model = await ChunkModel.create_instance(
                db_client=request.app.mongodb_client
            )

    if do_reset ==1:
        _= await chunk_model.delete_chunks_by_project_id(project_id=project.id)
    

    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller_obj.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"Error occurred while processing file: {file_id}. File not found or could not be loaded.")
            continue  
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
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        
        
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    count = await chunk_model.collection.count_documents({})
    print("Documents in collection:", count)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files,
        }
    )
