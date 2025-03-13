from database.pineconeDB import *
import logging
logging.basicConfig(level=logging.INFO)
from datetime import datetime
from langchain_core.documents import Document

def embedder(user_input):

    timestamp = datetime.now().strftime("%Y-%d-%m#%H-%M-%S")
    doc_id = f"{timestamp}"
    if user_input:
        # Generate E5 embeddings
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[user_input],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        metadata = {
            "chunk_text": user_input
        }
        # Prepare and upsert vector
        vector = {
            "id": doc_id,
            "values": embedding[0]['values'],
            "metadata": metadata
        }

        index.upsert(
            vectors=[vector],
        )

    else:
        logging.error("No text content found in the documents.")

    return f"{user_input} added to the retriever."

def search(user_query):
        
    try:
        # Generate E5 embeddings
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[user_query],
            parameters={"input_type": "query", "truncate": "END"}
        )

        # Perform vector search
        results = index.query(
            vector=embedding[0]['values'],
            top_k=5,
            include_metadata=True,
        )

        # Extract only the chunk_text from each result
        chunk_texts = []
        if results and 'matches' in results:
            for match in results['matches']:
                if 'metadata' in match and 'chunk_text' in match['metadata']:
                    chunk_texts.append(match['metadata']['chunk_text'])
        elif results and 'result' in results and 'hits' in results['result']:
            # Handle the specific result structure you shared
            for hit in results['result']['hits']:
                if 'fields' in hit and 'chunk_text' in hit['fields']:
                    chunk_texts.append(hit['fields']['chunk_text'])

        if not chunk_texts:
            raise Exception("No documents found matching query")

        return chunk_texts

    except Exception as e:
        logging.error(f"Error: {e}")
        raise e

