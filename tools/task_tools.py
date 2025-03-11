
from services.taskServices import *
from langchain_core.tools import tool, Tool
from services.retriverServices import *
from langchain.agents import AgentType, initialize_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from  langchain_google_genai import ChatGoogleGenerativeAI
import os
class ToolManager:
    """Manages available tools and their implementations"""
    
    @staticmethod
    def get_tools():
        """Initialize and return available tools"""
        
        @tool
        def get_all_tasks_():
            """
            Get all tasks from the database
            Args: No arguments
            Returns: List of all tasks
            """
            return str(get_all_tasks_from_db())


        @tool
        def get_task_by_date(date: str):
            """
            Get task by date on perticular date. Ideal for fetching all tasks on a particular date
            Args: date: Date of the task
            Returns: Task with the given date
            """
            return str(get_task_by_date_from_db(date))

        @tool
        def get_task_by_time(time: str):
            """
            Get task by time on perticular time. Ideal for fetching all tasks at a particular time
            Args: time: Time of the task
            Returns: Task with the given time
            """
            return str(get_task_by_time_from_db(time))

        @tool
        def get_task_by_date_time(date: str , time: str):
            """
            Get task by date and time on perticular date and time
            Args: date: Date of the task
                time: Time of the task
            Returns: Task with the given date and time
            """
            return str(get_task_by_date_time_from_db(date , time))

        @tool
        def create_task(name: str, description: str, status: str, time: str, date: str, priority: str):
            """
            Create a task in the database follow this format
            {
            "name": "Name of the task",
            "description": "Description of the task",
            "status": "status of the task", ["completed", "pending", "in progress"]
            "time": "hh:mm:ss",  24 hour format
            "date": "dd:mm:yyyy", 
            "priority": "Priority of the task", ["high", "medium", "low"]
            }
            Args: task: Task to be created in the database
            Returns: Created task
            """
            task = {
                "name": name,
                "description": description,
                "status": status,
                "time": time,
                "date": date,
                "priority": priority
            }
            return str(create_task_in_db(task))

        @tool
        def update_task(name: str, description: str, status: str, time: str, date: str, priority: str):
            """
            Update a task
            Args: date: Date of the task to be updated
                time: Time of the task to be updated
                task: Task to be updated
            Returns: Updated task
            """
            task = {
                "name": name,
                "description": description,
                "status": status,
                "time": time,
                "date": date,
                "priority": priority
            }
            return str(update_task_in_db(date , time ,task))


        @tool
        def delete_task(date: str , time: str):
            """
            Delete a task
            Args: date: Date of the task
                time: Time of the task
            Returns: Deleted task
            """
            return str(delete_task_in_db(date , time))


        @tool
        def create_memory(user_input: list[str]):
            """
            Create a memory in the Vector Databse with the user input. Please don't use this tool unless told explicitly.
            Memory creation structure:
            Bucket is the catagory , body is the information and  context is the context of the memory.
            ["(Bucket) , (Body) , (Context) ,(date)"]

            Args: user_input: User input to be stored in the memory in form of list[str]
            Returns: Memory created | None
            """
            # return "Memory created"
            return embedder(user_input)

        @tool
        def search_memory(user_query: str):
            """
            Search a memory in the Vector Database with the user query
            Bucket is the catagory in which you want to search the memory.body is the information you want to search and context is the context of the memory.
            search memories user_query structure:- "(Bucket) , (Query) , (Context)"
            

            Args: user_query: User query string to search the memory 
            Returns: Memory searched
            """
            # return "No memory found"
            return search(user_query)
        
        @tool
        def serper_search( query: str):
            """This is a tool which you should use to search the web about anything that the users ask for"""


            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                api_key=os.getenv("GEMINI_API_KEY")
                )
            search = GoogleSerperAPIWrapper()
            tools = [
                Tool(
                    name="Intermediate Answer",
                    func=search.run,
                    description="useful for when you need to ask with search",
                )
            ]

            self_ask_with_search = initialize_agent(
                tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True
            )
            result = self_ask_with_search.run(query)
            
            return str(result)


            
        return [ get_all_tasks_, get_task_by_date, get_task_by_time, get_task_by_date_time, create_task, update_task, delete_task , create_memory , search_memory , serper_search]


