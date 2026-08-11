from .Basecontroller import Basecontroller
from .Projectcontroller import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingStatus
from typing import List, Optional
from typing import Optional
from langchain_core.documents import Document
from helpers.config import get_settings
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: dict

     
class ProcessController(Basecontroller):
    def __init__(self, project_id: str):
        super().__init__(get_settings())
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        file_path = os.path.join(self.project_path, file_id)

        print("Project path:", self.project_path)
        print("File path:", file_path)
        print("File exists:", os.path.exists(file_path))

        file_ext = self.get_file_extension(file_id)
        print("Extension:", file_ext)
        print("TXT enum:", ProcessingStatus.TXT.value)
        print("PDF enum:", ProcessingStatus.PDF.value)

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingStatus.TXT.value:
            print("Using TextLoader")
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingStatus.PDF.value:
            print("Using PyPDFLoader")
            return PyPDFLoader(file_path)

        print("No loader found")
        return None

    def get_file_content(self, file_id: str):
        loader=self.get_file_loader(file_id=file_id)
        if loader is None:
            return None
        if loader:
            return loader.load()
        return None
    
    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        # chunks = text_splitter.create_documents(
        #     file_content_texts,
        #     metadatas=file_content_metadata
        # )

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )

        return chunks

    
    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks


    