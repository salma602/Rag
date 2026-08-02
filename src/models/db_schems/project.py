from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("project_id", 1)
                ],
                "name": "project_id_index",
                "unique": True
            }
        ]