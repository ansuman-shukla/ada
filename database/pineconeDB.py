
import os
from dotenv import load_dotenv
from pinecone import Pinecone , ServerlessSpec


load_dotenv()
index_name = "ada-knowledge-base"


# openai_api_key = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1024,  # E5-large requires 1024 dimensions
        metric="cosine",  # E5 works best with cosine similarity
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

index = pc.Index(index_name)