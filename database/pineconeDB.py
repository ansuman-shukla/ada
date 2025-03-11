from langchain_community.retrievers import PineconeHybridSearchRetriever
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone , ServerlessSpec
from pinecone_text.sparse import BM25Encoder

load_dotenv()
index_name = "ada-knowledge-base"


# openai_api_key = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric='dotproduct',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
else:
    print(f"Index {index_name} already exists.")

index = pc.Index(index_name)

# Instantiate the embeddings model
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
# print(f"Creating embeddings...{embeddings}")

bm25encoder = BM25Encoder()
# print(f"Creating BM25 encoder...{bm25encoder}")

sentences = [
    "Apple's first product was the Apple I, a computer designed by Steve Wozniak.",
]

bm25encoder.default()
