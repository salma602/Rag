from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATION_SUCCESS = "file validation success"
    FILE_SUCCESS_UPLOADED = "file uploaded successfully"
    FILE_UPLOAD_FAILED = "file upload failed"
    FILE_SIZE_EXCEEDS_LIMIT = "file size exceeds limit"
    FILE_TYPE_NOT_ALLOWED = "file type not allowed"
    PROCESSING_FAILED = "file processing failed"
    PROCESSING_SUCCESS = "file processing success"
    NO_FILE_ERROR = "no file found for the given project"
    FILE_ID_ERROR = "file id is required for processing"
    PROJECT_NOT_FOUND_ERROR = "project not found error"
    INSERT_INTO_VECTORDB_ERROR = "error while inserting into vector db"
    INSERT_INTO_VECTORDB_SUCCESS = "successfully inserted into vector db"
    VECTORDB_COLLECTION_RETRIEVED = "vector db collection retrieved"
    VECTORDB_SEARCH_ERROR = "error while searching in vector db"
    VECTORDB_SEARCH_SUCCESS = "successfully searched in vector db"


    