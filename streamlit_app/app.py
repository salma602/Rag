import streamlit as st
import requests


# ============================================================
# Configuration
# ============================================================

FASTAPI_URL = "http://127.0.0.1:5000"


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Mini RAG",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# Helper Functions
# ============================================================

def upload_file(project_id, uploaded_file):

    url = f"{FASTAPI_URL}/api/v1/data/upload/{project_id}"

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        url,
        files=files
    )

    return response


def process_file(
    project_id,
    file_id=None,
    chunk_size=1000,
    overlap_size=100,
    do_reset=0
):

    url = f"{FASTAPI_URL}/api/v1/data/process/{project_id}"

    payload = {
        "file_id": file_id,
        "chunk_size": chunk_size,
        "overlap_size": overlap_size,
        "do_reset": do_reset
    }

    response = requests.post(
        url,
        json=payload
    )

    return response


def index_project(project_id, do_reset=0):

    url = f"{FASTAPI_URL}/api/v1/nlp/index/push/{project_id}"

    payload = {
        "do_reset": do_reset
    }

    response = requests.post(
        url,
        json=payload
    )

    return response


def get_index_info(project_id):

    url = f"{FASTAPI_URL}/api/v1/nlp/index/info/{project_id}"

    response = requests.get(url)

    return response


def search_documents(project_id, text, limit=5):

    url = f"{FASTAPI_URL}/api/v1/nlp/index/search/{project_id}"

    payload = {
        "text": text,
        "limit": limit
    }

    response = requests.post(
        url,
        json=payload
    )

    return response


def ask_rag(project_id, question, limit=5):

    url = f"{FASTAPI_URL}/api/v1/nlp/index/answer/{project_id}"

    payload = {
        "text": question,
        "limit": limit
    }

    response = requests.post(
        url,
        json=payload
    )

    return response


# ============================================================
# Session State
# ============================================================

if "file_id" not in st.session_state:
    st.session_state.file_id = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("Mini RAG")

project_id = st.sidebar.number_input(
    "Project ID",
    min_value=1,
    value=1,
    step=1
)

st.sidebar.markdown("---")

st.sidebar.write("FastAPI Server")

st.sidebar.code(FASTAPI_URL)


# ============================================================
# Main Header
# ============================================================

st.title("Mini RAG System")

st.write(
    "Upload documents, process them, create the vector index, "
    "search semantically, and ask questions using RAG."
)


# ============================================================
# Tabs
# ============================================================

tab_upload, tab_process, tab_index, tab_search, tab_chat = st.tabs(
    [
        "Upload",
        "Process",
        "Vector Index",
        "Search",
        "Ask RAG"
    ]
)


# ============================================================
# Upload Tab
# ============================================================

with tab_upload:

    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "pdf"]
    )

    if uploaded_file is not None:

        st.info(
            f"Selected file: {uploaded_file.name}"
        )

        if st.button(
            "Upload File",
            key="upload_button"
        ):

            with st.spinner("Uploading..."):

                try:

                    response = upload_file(
                        project_id,
                        uploaded_file
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success(
                            data.get(
                                "result_signsl",
                                "File uploaded successfully"
                            )
                        )

                        file_id = data.get("file_id")

                        st.session_state.file_id = file_id
                        st.session_state.uploaded_file_name = (
                            uploaded_file.name
                        )

                        st.write(
                            f"File ID: `{file_id}`"
                        )

                    else:

                        st.error(
                            f"Upload failed: "
                            f"{response.status_code}"
                        )

                        st.json(response.json())

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI. "
                        "Make sure uvicorn is running."
                    )


# ============================================================
# Process Tab
# ============================================================

with tab_process:

    st.header("Process Document")

    if st.session_state.file_id:

        st.info(
            f"Current file: "
            f"{st.session_state.uploaded_file_name}"
        )

        st.write(
            f"File ID: `{st.session_state.file_id}`"
        )

    else:

        st.warning(
            "Upload a file first."
        )

    chunk_size = st.number_input(
        "Chunk Size",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )

    overlap_size = st.number_input(
        "Overlap Size",
        min_value=0,
        max_value=5000,
        value=100,
        step=50
    )

    reset_processing = st.checkbox(
        "Reset existing chunks",
        value=False
    )

    if st.button(
        "Process File",
        key="process_button"
    ):

        if not st.session_state.file_id:

            st.error("Please upload a file first.")

        else:

            with st.spinner(
                "Processing document and creating chunks..."
            ):

                try:

                    response = process_file(
                        project_id=project_id,
                        file_id=st.session_state.file_id,
                        chunk_size=chunk_size,
                        overlap_size=overlap_size,
                        do_reset=1 if reset_processing else 0
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success(
                            data.get(
                                "signal",
                                "Processing completed"
                            )
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Inserted Chunks",
                                data.get(
                                    "inserted_chunks",
                                    0
                                )
                            )

                        with col2:
                            st.metric(
                                "Processed Files",
                                data.get(
                                    "processed_files",
                                    0
                                )
                            )

                    else:

                        st.error(
                            f"Processing failed: "
                            f"{response.status_code}"
                        )

                        st.json(response.json())

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI."
                    )


# ============================================================
# Vector Index Tab
# ============================================================

with tab_index:

    st.header("Vector Database")

    st.write(
        "Create embeddings and insert document chunks "
        "into PGVector."
    )

    reset_index = st.checkbox(
        "Reset vector collection",
        value=False
    )

    if st.button(
        "Build Vector Index",
        key="index_button"
    ):

        with st.spinner(
            "Generating embeddings and building vector index..."
        ):

            try:

                response = index_project(
                    project_id=project_id,
                    do_reset=1 if reset_index else 0
                )

                if response.status_code == 200:

                    data = response.json()

                    st.success(
                        data.get(
                            "signal",
                            "Index created successfully"
                        )
                    )

                    st.metric(
                        "Inserted Items",
                        data.get(
                            "inserted_items_count",
                            0
                        )
                    )

                else:

                    st.error(
                        f"Indexing failed: "
                        f"{response.status_code}"
                    )

                    st.json(response.json())

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI."
                )


    st.markdown("---")

    st.subheader("Collection Information")

    if st.button(
        "Get Collection Info",
        key="collection_info_button"
    ):

        with st.spinner("Loading collection information..."):

            try:

                response = get_index_info(
                    project_id
                )

                if response.status_code == 200:

                    data = response.json()

                    st.json(
                        data.get(
                            "collection_info",
                            data
                        )
                    )

                else:

                    st.error(
                        f"Failed: {response.status_code}"
                    )

                    st.json(response.json())

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI."
                )


# ============================================================
# Search Tab
# ============================================================

with tab_search:

    st.header("Semantic Search")

    query = st.text_input(
        "Search Query",
        placeholder="Enter your search..."
    )

    limit = st.slider(
        "Number of results",
        min_value=1,
        max_value=20,
        value=5
    )

    if st.button(
        "Search",
        key="search_button"
    ):

        if not query.strip():

            st.warning(
                "Please enter a search query."
            )

        else:

            with st.spinner(
                "Searching vector database..."
            ):

                try:

                    response = search_documents(
                        project_id=project_id,
                        text=query,
                        limit=limit
                    )

                    if response.status_code == 200:

                        data = response.json()

                        results = data.get(
                            "results",
                            []
                        )

                        st.success(
                            f"Found {len(results)} results."
                        )

                        for i, result in enumerate(results):

                            with st.expander(
                                f"Result {i + 1}"
                            ):

                                if isinstance(
                                    result,
                                    dict
                                ):

                                    st.write(
                                        result.get(
                                            "text",
                                            ""
                                        )
                                    )

                                    if "score" in result:

                                        st.write(
                                            f"Score: "
                                            f"{result['score']}"
                                        )

                                    if "metadata" in result:

                                        st.json(
                                            result["metadata"]
                                        )

                                else:

                                    st.write(result)

                    else:

                        st.error(
                            f"Search failed: "
                            f"{response.status_code}"
                        )

                        st.json(response.json())

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI."
                    )


# ============================================================
# Ask RAG Tab
# ============================================================

with tab_chat:

    st.header("Ask Your Documents")

    question = st.text_area(
        "Question",
        placeholder="Ask a question about your documents...",
        height=120
    )

    limit = st.slider(
        "Retrieved Documents",
        min_value=1,
        max_value=20,
        value=5,
        key="rag_limit"
    )

    if st.button(
        "Ask",
        key="ask_button"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Retrieving documents and generating answer..."
            ):

                try:

                    response = ask_rag(
                        project_id=project_id,
                        question=question,
                        limit=limit
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success("Answer")

                        st.write(
                            data.get(
                                "answer",
                                "No answer returned."
                            )
                        )

                        with st.expander(
                            "Full Prompt"
                        ):

                            st.text(
                                data.get(
                                    "full_prompt",
                                    ""
                                )
                            )

                        with st.expander(
                            "Chat History"
                        ):

                            st.json(
                                data.get(
                                    "chat_history",
                                    []
                                )
                            )

                    else:

                        st.error(
                            f"RAG request failed: "
                            f"{response.status_code}"
                        )

                        st.json(response.json())

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI."
                    )