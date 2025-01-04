from services.taskServices import get_all_tasks_from_db ,get_task_by_date_from_db , get_task_by_time_from_db , get_task_by_date_time_from_db , create_task_in_db , update_task_in_db , delete_task_in_db
from langchain.tools import tool
import os
from services.retriverServices import *
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from repos.taskRepository import get_all_tasks , get_task_by_date , get_task_by_time , get_task_by_date_time, delete_task , update_task
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import HumanMessage, ToolMessage , SystemMessage , AIMessage
from datetime import datetime
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@tool
def get_all_tasks():
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
    Create a memory in the Vector Databse with the user input
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



tools = [get_all_tasks, get_task_by_date, get_task_by_time, get_task_by_date_time, create_task, update_task, delete_task , create_memory , search_memory]

tool_mapping = {
    "get_all_tasks": get_all_tasks,
    "get_task_by_date": get_task_by_date,
    "get_task_by_time": get_task_by_time,
    "get_task_by_date_time": get_task_by_date_time,
    "create_task": create_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "create_memory": create_memory,
    "search_memory": search_memory
}

output_parser = StrOutputParser()


async def interact_with_llm_and_tools(user_input: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        api_key=GEMINI_API_KEY,
    )

    Instructions = f"""
    I'm am Ansuman and you are Ada a personal helpful assistant! You have access to Users tasks and can help them with their tasks.
    You have all the tools to help the user with their tasks. You can get all tasks, get task by date, get task by time, get task by date and time, create task, update task, delete task, create memory and search memory.

    Please figure out tomorrow , today , yesterday etc. from the user given date and time and then perform the task accordingly.
    While searching memory please add everything in the same query and separate them with comma.Don't do multiple tool calls in a single message.
    Always respond in your own [natural],[user-friendly] language.
    """


    llm_with_tools = llm.bind_tools(tools=tools)
    system_message = SystemMessage(content=Instructions)
    human_message = HumanMessage(content=f"{user_input}+Current DATE and TIME is :- {datetime.now().strftime("(%A %d/%m/%Y %H:%M:%S")} ")
    messages =[]
    messages.append(system_message)
    messages.append(human_message)
    llm_output = llm_with_tools.invoke(messages)
    messages.append(llm_output)
    print("==============================================")
    print(llm_output)
    print("==============================================")
    
    if hasattr(llm_output, 'tool_calls'):
        for tool_call in llm_output.tool_calls:
            print(f"Executing tool: {tool_call['name']}")
            print("==============================================")
            try:
                tool_name = tool_call.get('name')
                if not tool_name:
                    raise ValueError("Function call has an empty name, skipping this call.")

                # Get the tool function directly from the tools list
                tool_func = next((t for t in tools if t.name.lower() == tool_call['name'].lower()), None)
                
                if tool_func:
                    tool_args = tool_call['args']
                    # Convert empty dict to empty string for no-arg tools
                    tool_input = "" if not tool_args else tool_args
                    tool_output = tool_func.invoke(tool_input)
                    print(tool_output)
                    print("==============================================")
                    messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call['id']))
                    print("Tool message added")
                    print("==============================================")
                else:
                    print(f"Tool {tool_call['name']} not found")
                    print("==============================================")
            except Exception as e:
                print(f"Error executing tool {tool_call['name']}: {str(e)}")
                print("==============================================")

    if llm_output.content not in ["", None]:
        parsed_response = output_parser.parse(llm_output.content)
        print(parsed_response)
        return llm_output.content

    print(f"Messages:{messages}")
    print("==============================================")
    # ...existing code...
    valid_calls = []
    for m in messages:
        if isinstance(m, AIMessage) and m.additional_kwargs.get("function_call"):
            fc = m.additional_kwargs["function_call"]
            if fc.get("name"):
                valid_calls.append(m)
        else:
            valid_calls.append(m)

    final_response = llm_with_tools.invoke(valid_calls)
# ...existing code...
    final_response = llm_with_tools.invoke(messages)
    print(final_response)
    parsed_response = output_parser.parse(final_response.content)
    return parsed_response