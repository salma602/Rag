from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helpers.config import get_settings
from stores.LLM.LLMProviderFactory import LLMProviderFactory
app = FastAPI()


async def startup_db_client():
    settings = get_settings()

    print("MONGO_URI:", settings.MONGO_URI)
    print("MONGO_DB_NAME:", settings.MONGO_DB_NAME)

    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB_NAME]

    llm_provider_factory = LLMProviderFactory(config=settings)
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_SIZE)



    
async def shutdown_db_client():
    app.mongodb_conn.close()


app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

app.include_router(base.base_router)
app.include_router(data.data_router)