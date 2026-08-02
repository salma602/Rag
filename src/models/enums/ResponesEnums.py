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

    