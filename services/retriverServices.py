from database.pineConeRetriver import retriever
import logging
logging.basicConfig(level=logging.INFO)



def embedder(user_input):

    if user_input:
        retriever.add_texts(user_input)
        logging.info("Texts successfully added to the retriever.")
    else:
        logging.error("No text content found in the documents.")

    return f"{user_input} added to the retriever."

def search(user_query):
    results = retriever.invoke(user_query)
    return results

