import os
import glob
from sentence_transformers import SentenceTransformer
import chromadb
# from chromadb.utils import embedding_functions # Not strictly needed if we pass embeddings directly
from langchain.text_splitter import RecursiveCharacterTextSplitter # Or MarkdownTextSplitter
import uuid # For generating unique IDs if needed, though we construct them

# --- Configuration ---
KNOWLEDGE_BASE_DIR = "/Users/jacc/Downloads/TextRealmsAI/data/knowledge_base/"
CHROMA_DB_PATH = "/Users/jacc/Downloads/TextRealmsAI/data/chroma_db"
COLLECTION_NAME = "text_realms_kb"
EMBEDDING_MODEL_NAME = 'BAAI/bge-small-en-v1.5'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Helper Functions ---
def load_documents(kb_dir):
    """Loads all .md documents from the knowledge base directory."""
    documents = []
    # Ensure the path ends with a slash for glob to work as expected with **
    if not kb_dir.endswith('/'):
        kb_dir += '/'
    
    for filepath in glob.glob(os.path.join(kb_dir, "**/*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Using relative path from KNOWLEDGE_BASE_DIR as part of the source identifier
            relative_path = os.path.relpath(filepath, KNOWLEDGE_BASE_DIR)
            documents.append({"content": content, "source": relative_path})
    print(f"Loaded {len(documents)} documents.")
    return documents

def chunk_documents(docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True # Helps maintain context around splits
    )
    all_chunks = []
    for i, doc in enumerate(docs):
        chunks_text = text_splitter.split_text(doc["content"])
        for j, chunk_text_content in enumerate(chunks_text):
            # Create a more robust unique ID
            chunk_id = f"doc_{i}_{doc['source'].replace('/', '_').replace('.', '_')}_chunk_{j}"
            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text_content,
                "metadata": {"source": doc['source'], "doc_id_in_batch": i, "chunk_num_in_doc": j}
            })
    print(f"Created {len(all_chunks)} chunks.")
    return all_chunks

# --- Main Script ---
if __name__ == "__main__":
    print("Starting knowledge base build process...")

    # 1. Load documents
    docs_data = load_documents(KNOWLEDGE_BASE_DIR)
    if not docs_data:
        print(f"No documents found in {KNOWLEDGE_BASE_DIR}. Please ensure .md files are present. Exiting.")
        exit()

    # 2. Chunk documents
    chunks_with_metadata = chunk_documents(docs_data)
    if not chunks_with_metadata:
        print("No chunks created from documents. Exiting.")
        exit()

    # 3. Initialize Embedding Model
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Embedding model loaded.")

    # 4. Initialize ChromaDB
    print(f"Initializing ChromaDB client at: {CHROMA_DB_PATH}...")
    # Ensure the directory for ChromaDB exists
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    print(f"Getting or creating collection: {COLLECTION_NAME}...")
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
        # If you wanted Chroma to manage embeddings:
        # embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    )
    # Clear the collection if it already exists and we want a fresh build
    # This is useful during development. For production, you might want to update.
    if collection.count() > 0:
        print(f"Collection '{COLLECTION_NAME}' already exists with {collection.count()} items. Clearing it for a fresh build.")
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' cleared and recreated.")

    print("ChromaDB collection ready.")

    # 5. Generate Embeddings and Populate Vector Store
    print("Generating embeddings and populating ChromaDB (this may take a while)...")
    
    batch_size = 32 # Adjusted batch size, can be tuned
    num_chunks_total = len(chunks_with_metadata)

    for i in range(0, num_chunks_total, batch_size):
        batch_data = chunks_with_metadata[i:i+batch_size]
        
        current_batch_texts = [item['text'] for item in batch_data]
        current_batch_ids = [item['id'] for item in batch_data]
        current_batch_metadatas = [item['metadata'] for item in batch_data]

        print(f"Processing batch {i//batch_size + 1}/{(num_chunks_total + batch_size - 1)//batch_size} (size: {len(current_batch_texts)})...")
        
        if not current_batch_texts:
            print("Skipping empty batch.")
            continue

        embeddings = model.encode(current_batch_texts, show_progress_bar=False).tolist()

        try:
            collection.add(
                ids=current_batch_ids,
                embeddings=embeddings,
                documents=current_batch_texts,
                metadatas=current_batch_metadatas
            )
            print(f"Added {len(current_batch_ids)} items to collection.")
        except Exception as e:
            print(f"Error adding batch to ChromaDB: {e}")
            print(f"Problematic IDs: {current_batch_ids[:5]}...") # Log first few IDs for debugging
            # Potentially add more detailed logging or error handling here

    print(f"Successfully populated ChromaDB collection '{COLLECTION_NAME}' with {collection.count()} items.")
    print("Knowledge base build process complete.")
