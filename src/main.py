from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helpers.config import get_settings
from stores.LLM.LLMProviderFactory import LLMProviderFactory
from routes.nlp import nlp_router
from stores.vectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from stores.LLM.Templates.template_parser import TemplateParser

app = FastAPI()


async def startup_spam():
    settings = get_settings()

    print("MONGO_URI:", settings.MONGO_URI)
    print("MONGO_DB_NAME:", settings.MONGO_DB_NAME)

    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB_NAME]

    llm_provider_factory = LLMProviderFactory(config=settings)
    vector_db_provider_factory = VectorDBProviderFactory(config=settings)

    #generation client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    #embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #vector db client
    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()

    app.template_parser=TemplateParser(

        language = settings.PRIMARY_LANG,
        default_language = settings.DEFAULT_LANG,
    ) 




    
async def shutdown_spam():
    app.mongodb_conn.close()
    app.vector_db_client.disconnect()



app.on_event("startup")(startup_spam)
app.on_event("shutdown")(shutdown_spam)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp_router)
