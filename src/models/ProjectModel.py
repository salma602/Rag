from .BaseDataModel import BaseDataModel
from .db_schems import Project, DataChunk
from .enums.DataBaseEnums import DataBaseEnums

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_PROJECTS_NAME.value]


    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        indexes = Project.get_indexes()

        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        project = await self.collection.find_one({"project_id": project_id})

        if project is None:
            new_project = Project(project_id=project_id)
            result = await self.collection.insert_one(
                new_project.model_dump(by_alias=True, exclude_unset=True)
            )
            new_project.id = result.inserted_id
            return new_project

        return Project(**project)
    
    async def get_all_projects(self,page: int = 1, page_size: int = 10):
        total_doc=await self.collection.count_documents({})
        tatal_pages=total_doc // page_size
        if total_doc % page_size > 0:
            tatal_pages += 1
        skip = (page - 1) * page_size
        cursor = await self.collection.find().skip(skip).limit(page_size)
        projects=[]
        async for doc in cursor:
            projects.append(Project(**doc))
        return projects,tatal_pages

