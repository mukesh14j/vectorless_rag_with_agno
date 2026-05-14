import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Vectorless RAG",
    layout="wide"
)

st.title("📄 Vectorless RAG with Ollama")

# Session state
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "document_id" not in st.session_state:
    st.session_state.document_id = None

# Upload only once
if not st.session_state.document_uploaded:

    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"]
    )

    if uploaded_file is not None:

        with st.spinner("Uploading document..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue()
                )
            }

            response = requests.post(
                f"{BACKEND_URL}/upload",
                files=files
            )

        if response.status_code == 200:

            data = response.json()

            st.session_state.document_id = data[
                "document_id"
            ]

            st.session_state.document_uploaded = True

            st.success("Document uploaded and indexed")

            st.rerun()

else:

    st.success(
        f"Document already indexed\n\n"
        f"Document ID: "
        f"{st.session_state.document_id}"
    )

    if st.button("Upload New Document"):

        st.session_state.document_uploaded = False

        st.session_state.document_id = None

        st.rerun()

    question = st.text_input(
        "Ask question"
    )

    if st.button("Ask"):

        if question.strip() == "":
            st.warning("Enter question")

        else:

            with st.spinner("Generating answer..."):

                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={
                        "document_id":
                            st.session_state.document_id,
                        "question":
                            question
                    }
                )

            data = response.json()

            st.subheader("Answer")

            st.write(data["answer"])

            st.subheader("Retrieved Chunks")

            for chunk in data["chunks"]:

                with st.expander(
                    f"Score: "
                    f"{chunk['score']:.2f}"
                ):
                    st.write(chunk["chunk"])