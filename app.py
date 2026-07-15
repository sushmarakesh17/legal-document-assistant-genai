import streamlit as st
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="Legal Document Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Legal Document Assistant")

st.markdown("""
Upload a legal PDF and leverage **Generative AI (RAG)** to:

- 📄 Generate AI Summary
- 💬 Ask Questions
- 👥 Extract Parties
- 📅 Extract Important Dates
- 📜 Extract Clauses

Built using **Streamlit + LangChain + FAISS + HuggingFace + Ollama**
""")
# -------------------------------
# LOAD MODELS
# -------------------------------

@st.cache_resource
def load_models():

    llm = ChatOllama(
        model="llama3.2",
        temperature=0
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return llm, embeddings


llm, embeddings = load_models()

# -------------------------------
# FILE UPLOADER
# -------------------------------

uploaded_file = st.file_uploader(
    "Upload Legal PDF",
    type=["pdf"]
)

if uploaded_file:

    pdf_reader = PdfReader(uploaded_file)

    document_text = ""

    for page in pdf_reader.pages:

        page_text = page.extract_text()

        if page_text:
            document_text += page_text + "\n"

    st.success("✅ PDF Uploaded Successfully")

    with st.expander("📄 View Extracted Text"):

        st.text_area(
            "Document Content",
            document_text,
            height=300
        )

    # -------------------------------
    # SPLIT DOCUMENT
    # -------------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=200
    )

    chunks = splitter.split_text(document_text)

    st.info(f"Chunks Created : {len(chunks)}")
        # -------------------------------
    # CREATE VECTOR DATABASE
    # -------------------------------

    with st.spinner("Creating Vector Database..."):

        vector_store = FAISS.from_texts(
            texts=chunks,
            embedding=embeddings
        )

    st.success("✅ Vector Database Created")

    # -------------------------------
    # DOCUMENT SUMMARY
    # -------------------------------

    st.divider()

    st.subheader("📄 AI Document Summary")

    if st.button("Generate Summary"):

        with st.spinner("Generating Summary..."):

            prompt = f"""
You are an expert Legal Assistant.

Summarize the following legal document.

Mention:

1. Parties involved
2. Purpose
3. Important clauses
4. Dates
5. Termination
6. Overall Summary

Document:

{document_text}
"""

            summary = llm.invoke(prompt)

        st.success("Summary Generated")

        st.write(summary.content)
            # -------------------------------
    # ASK QUESTIONS (RAG)
    # -------------------------------

    st.divider()

    st.subheader("💬 Ask Questions About the Document")

    question = st.text_input(
        "Ask anything about this legal document"
    )

    if st.button("Get Answer"):

        if question.strip() == "":
            st.warning("Please enter a question.")

        else:

            docs = vector_store.similarity_search(
                question,
                k=3
            )

            context = "\n\n".join(
                [doc.page_content for doc in docs]
            )

            prompt = f"""
You are an expert Legal AI Assistant.

Answer ONLY from the context provided.

If the answer is not found in the document, reply:

'I couldn't find this information in the uploaded document.'

Context:
{context}

Question:
{question}
"""

            with st.spinner("Generating Answer..."):

                response = llm.invoke(prompt)

            st.subheader("Answer")

            st.success(response.content)

    # -------------------------------
    # LEGAL INFORMATION EXTRACTION
    # -------------------------------

    st.divider()

    st.subheader("⚖️ Legal Information Extraction")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Extract Parties"):

            prompt = f"""
Extract all parties involved in this legal document.

Document:

{document_text}
"""

            result = llm.invoke(prompt)

            st.write(result.content)

    with col2:

        if st.button("Extract Dates"):

            prompt = f"""
Extract all important dates from this legal document.

Document:

{document_text}
"""

            result = llm.invoke(prompt)

            st.write(result.content)

    with col3:

        if st.button("Extract Clauses"):

            prompt = f"""
List the important legal clauses from this document.

Document:

{document_text}
"""

            result = llm.invoke(prompt)

            st.write(result.content)