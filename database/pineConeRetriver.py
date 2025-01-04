from database.pineconeDB import embeddings, bm25encoder, index
from langchain_community.retrievers import PineconeHybridSearchRetriever

retriever = PineconeHybridSearchRetriever(embeddings=embeddings, sparse_encoder=bm25encoder, index=index)

# print(retriever)