#!/usr/bin/env python3
import chromadb
import os

# Initialize ChromaDB client
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chroma_db')
print(f"ChromaDB path: {db_path}")

client = chromadb.PersistentClient(path=db_path)

# Get or create the collection
try:
    collection = client.get_collection('text_realms_kb')
    count = collection.count()
    print(f'ChromaDB collection exists with {count} documents')
    
    # Show a few sample documents if they exist
    if count > 0:
        results = collection.get(limit=5)
        print(f'Sample documents:')
        for i, (doc_id, doc) in enumerate(zip(results['ids'], results['documents'])):
            print(f'  {i+1}. ID: {doc_id}')
            print(f'     Text: {doc[:100]}...' if len(doc) > 100 else f'     Text: {doc}')
    else:
        print('Collection is empty - no documents found')
        
except Exception as e:
    print(f'Collection does not exist or error: {e}')
    print('Available collections:', client.list_collections())
