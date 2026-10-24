import os
import pickle
import networkx as nx
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.prompts import ChatPromptTemplate

# Load API key from .env
load_dotenv()

# Define local storage paths
STORAGE_DIR = "./storage"
FAISS_PATH = os.path.join(STORAGE_DIR, "faiss_index")
GRAPH_PATH = os.path.join(STORAGE_DIR, "kg_graph.pkl")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Initialize OpenAI Embeddings and LLM
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def build_vector_db(file_path: str):
    """Loads a PDF, splits it into chunks, and saves it to a local FAISS Vector DB."""
    print(f"1. Loading PDF from: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    print("2. Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(docs)
    print(f"   -> Created {len(chunks)} chunks from {len(docs)} pages.")

    print("3. Generating embeddings and saving to FAISS Vector DB...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_PATH)
    print(f"   -> FAISS index saved successfully at {FAISS_PATH}!")

    return chunks

def build_knowledge_graph(chunks):
    """Extracts entities and relationships from chunks and saves a NetworkX Knowledge Graph."""
    print("4. Extracting Knowledge Graph entities & relationships using LLM...")
    llm_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = llm_transformer.convert_to_graph_documents(chunks)

    G = nx.DiGraph()
    for graph_doc in graph_documents:
        for node in graph_doc.nodes:
            G.add_node(node.id, type=node.type)
        for edge in graph_doc.relationships:
            G.add_edge(edge.source.id, edge.target.id, relation=edge.type)

    with open(GRAPH_PATH, "wb") as f:
        pickle.dump(G, f)

    print(f"   -> Knowledge Graph saved at {GRAPH_PATH}!")
    print(f"   -> Extracted {G.number_of_nodes()} Nodes and {G.number_of_edges()} Relationships.")
    return G

def ingest_pdf(file_path: str):
    """Master ingestion pipeline: builds both Vector DB and Knowledge Graph."""
    chunks = build_vector_db(file_path)
    G = build_knowledge_graph(chunks)
    return {
        "chunks_processed": len(chunks),
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges()
    }

def retrieve_from_kg(query: str, G: nx.DiGraph) -> str:
    """Finds graph nodes matching query words and retrieves 1-hop relationships."""
    kg_context = []
    query_lower = query.lower()
    query_words = [w.strip("?.,!") for w in query_lower.split() if len(w.strip("?.,!")) > 2]

    for node in G.nodes():
        node_str = str(node).lower()
        # Match if node name appears in query OR any significant query word appears in node name
        if node_str in query_lower or any(word in node_str for word in query_words):
            for _, target, data in G.out_edges(node, data=True):
                kg_context.append(f"{node} --[{data.get('relation')}]--> {target}")
            for source, _, data in G.in_edges(node, data=True):
                kg_context.append(f"{source} --[{data.get('relation')}]--> {node}")

    # Deduplicate and limit to top 30 relationships so prompt stays focused
    unique_rels = list(dict.fromkeys(kg_context))[:30]
    return "\n".join(unique_rels) if unique_rels else "No direct graph relationships matched."

def answer_question(query: str):
    """Queries both FAISS Vector DB and NetworkX Knowledge Graph to answer a question."""
    if not os.path.exists(FAISS_PATH) or not os.path.exists(GRAPH_PATH):
        return {"error": "Databases not found. Please ingest a PDF first."}

    # 1. Retrieve from Vector DB
    vector_store = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    vector_docs = vector_store.similarity_search(query, k=4)
    vector_context = "\n\n".join([doc.page_content for doc in vector_docs])

    # 2. Retrieve from Knowledge Graph
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
    kg_context = retrieve_from_kg(query, G)

    # 3. Combine both contexts and generate LLM response
    prompt = ChatPromptTemplate.from_template("""
You are a helpful and accurate AI assistant answering customer questions based on the provided document.
Use BOTH the unstructured Vector DB Context and the structured Knowledge Graph Relationships to formulate your answer.
If the answer is not in the context, state that clearly.

--- VECTOR DB CONTEXT ---
{vector_context}

--- KNOWLEDGE GRAPH RELATIONSHIPS ---
{kg_context}

--- CUSTOMER QUESTION ---
{question}
""")

    chain = prompt | llm
    response = chain.invoke({
        "vector_context": vector_context,
        "kg_context": kg_context,
        "question": query
    })

    return {
        "answer": response.content,
        "vector_context": vector_context,
        "kg_context": kg_context
    }