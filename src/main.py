from fastapi import FastAPI
from helpers.config import get_settings
from stores.LLM.LLMProviderFactory import LLMProviderFactory
from stores.vectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from stores.LLM.Templates.template_parser import TemplateParser

from routes import base, data, nlp

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


app = FastAPI()


async def startup_span():

    settings = get_settings()

    # Save settings inside FastAPI app
    app.app_settings = settings

    postgres_conn = (
        f"postgresql+asyncpg://"
        f"{settings.POSTGRES_USERNAME}:"
        f"{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_MAIN_DATABASE}"
    )

    app.db_engine = create_async_engine(postgres_conn)

    app.db_client = sessionmaker(
        app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # LLM
    llm_provider_factory = LLMProviderFactory(settings)

    vectordb_provider_factory = VectorDBProviderFactory(
        config=settings,
        db_client=app.db_client
    )

    # Generation client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )

    app.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID
    )

    # Embedding client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )

    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # Vector DB client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )

    await app.vectordb_client.connect()

    # Template parser
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )


async def shutdown_span():

    await app.db_engine.dispose()

    await app.vectordb_client.disconnect()


# Startup / Shutdown
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)


# Routers
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)