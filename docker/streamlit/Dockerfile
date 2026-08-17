FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit \
    requests

COPY streamlit_app /app/streamlit_app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]