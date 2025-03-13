# from langchain_core.tools import tool
# from services.retriverServices import * 

# @tool
# def search_memory(user_query: str):
#     """
#     Search a memory in the Vector Database with the user query

#     Args: user_query: User query string to search the memory 
#     Returns: Memory searched
#     """
#     # return "No memory found"
#     return str(search(user_query))

# @tool

# def create_memory(user_input: str):
#     """
#     Create a memory in the Vector Databse with the user input. Please don't use this tool unless told explicitly.

#     Args:User input to be stored in the memory in form of str
#     Returns: Memory created | None
#     """
#     return str(embedder(user_input))



# print(search_memory.invoke("I have to build my own MCP server"))