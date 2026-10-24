import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Hybrid Graph-RAG Assistant",
    page_icon="🕸️",
    layout="wide"
)

st.title("🕸️ Hybrid RAG (Vector DB + Knowledge Graph) Q&A")
st.caption("Powered by FastAPI, FAISS Vector Store, NetworkX Knowledge Graph & OpenAI")

# Sidebar: System Status & PDF Ingestion
with st.sidebar:
    st.header("⚙️ System Status")
    try:
        health_res = requests.get(f"{FASTAPI_URL}/health", timeout=3)
        if health_res.status_code == 200:
            db_ready = health_res.json().get("databases_initialized", False)
            st.success("FastAPI Backend: Online")
            if db_ready:
                st.info("Databases: Ready (Vector + KG loaded)")
            else:
                st.warning("Databases: Empty (Please upload a PDF)")
    except Exception:
        st.error("FastAPI Backend: Offline. Start Uvicorn on port 8000.")

    st.divider()
    st.header("📄 1. Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF to build/update the databases", type=["pdf"])

    if st.button("Ingest into Vector DB & KG", type="primary") and uploaded_file:
        with st.spinner("Chunking PDF & extracting Knowledge Graph entities..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                res = requests.post(f"{FASTAPI_URL}/ingest", files=files)
                if res.status_code == 200:
                    data = res.json()
                    st.success(data["message"])
                    stats = data["stats"]
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Chunks", stats["chunks_processed"])
                    col2.metric("KG Nodes", stats["nodes"])
                    col3.metric("KG Edges", stats["edges"])
                else:
                    st.error(f"Error: {res.json().get('detail', res.text)}")
            except Exception as e:
                st.error(f"Failed to connect to FastAPI: {e}")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main Area: Customer Q&A Chat
st.subheader("💬 2. Ask Customer Questions")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "vector_context" in msg and "kg_context" in msg:
            with st.expander("🔍 Inspect Hybrid Retrieval Context (Vector DB + Knowledge Graph)"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**📚 Vector DB Chunks (FAISS)**")
                    st.info(msg["vector_context"])
                with c2:
                    st.markdown("**🕸️ Knowledge Graph Relationships (NetworkX)**")
                    st.code(msg["kg_context"], language="text")

# Chat Input
query = st.chat_input("Ask any question about your document...")

if query:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Call FastAPI /ask endpoint
    with st.chat_message("assistant"):
        with st.spinner("Querying FAISS Vector DB & Knowledge Graph..."):
            try:
                res = requests.post(f"{FASTAPI_URL}/ask", json={"question": query})
                if res.status_code == 200:
                    data = res.json()
                    answer = data["answer"]
                    v_ctx = data["vector_context"]
                    kg_ctx = data["kg_context"]

                    st.markdown(answer)

                    with st.expander("🔍 Inspect Hybrid Retrieval Context (Vector DB + Knowledge Graph)"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**📚 Vector DB Chunks (FAISS)**")
                            st.info(v_ctx)
                        with c2:
                            st.markdown("**🕸️ Knowledge Graph Relationships (NetworkX)**")
                            st.code(kg_ctx, language="text")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "vector_context": v_ctx,
                        "kg_context": kg_ctx
                    })
                else:
                    st.error(f"Backend Error: {res.json().get('detail', res.text)}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI server on port 8000: {e}")