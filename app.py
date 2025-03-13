import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool, Tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient
from pinecone import Pinecone, ServerlessSpec
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi

# Load the environment variables
load_dotenv()

uri = os.getenv("uri")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Create a new database
db = client['tasks']
task_collection = db['tasks']

# Pinecone Connection
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "ada-knowledge-base"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
index = pc.Index(index_name)

# --- Task Formatting and Repository Functions ---

def format_task(task):
    """Format a MongoDB task document into a dictionary."""
    return {
        '_id': str(task.get('_id')),
        'name': str(task.get('name')),
        'description': str(task.get('description')),
        'status': str(task.get('status')),
        'time': str(task.get('time')),
        'date': str(task.get('date')),
        'priority': str(task.get('priority'))
    }

def get_all_tasks():
    """Retrieve all tasks from MongoDB."""
    try:
        return [format_task(task) for task in task_collection.find()]
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def get_task_by_date(date: str):
    """Retrieve tasks by date from MongoDB."""
    return [format_task(task) for task in task_collection.find({"date": date})]

def get_task_by_time(time: str):
    """Retrieve tasks by time from MongoDB."""
    return [format_task(task) for task in task_collection.find({"time": time})]

def get_task_by_date_time(date: str, time: str):
    """Retrieve a task by date and time from MongoDB."""
    task = task_collection.find_one({"date": date, "time": time})
    return format_task(task) if task else None

def create_task(task: dict):
    """Create a new task in MongoDB."""
    result = task_collection.insert_one(task)
    task['_id'] = str(result.inserted_id)
    return format_task(task)

def update_task(date: str, time: str, task: dict):
    """Update an existing task in MongoDB."""
    result = task_collection.update_one(
        {"date": date, "time": time},
        {"$set": task}
    )
    if result.matched_count:
        updated_task = task_collection.find_one({"date": task['date'], "time": task['time']})
        return format_task(updated_task)
    return None

def delete_task(date: str, time: str):
    """Delete a task from MongoDB."""
    result = task_collection.delete_one({"date": date, "time": time})
    return result.deleted_count > 0

# --- Retriever Functions for Pinecone ---

def embedder(user_input: str):
    """Embed user input into Pinecone vector database."""
    timestamp = datetime.now().strftime("%Y-%d-%m#%H-%M-%S")
    doc_id = f"{timestamp}"
    if user_input:
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[user_input],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        metadata = {"chunk_text": user_input}
        vector = {
            "id": doc_id,
            "values": embedding[0]['values'],
            "metadata": metadata
        }
        index.upsert(vectors=[vector])
        return f"{user_input} added to the retriever."
    return "No text content provided."

def search(user_query: str):
    """Search Pinecone vector database for matching memories."""
    try:
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[user_query],
            parameters={"input_type": "query", "truncate": "END"}
        )
        results = index.query(
            vector=embedding[0]['values'],
            top_k=5,
            include_metadata=True,
        )
        chunk_texts = [match['metadata']['chunk_text'] for match in results['matches'] if 'metadata' in match and 'chunk_text' in match['metadata']]
        return chunk_texts if chunk_texts else ["No documents found matching query"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# --- Tool Definitions ---
@tool
def get_all_tasks_():
    """
    Get all tasks from the database without any filtering.
    
    Args:
        None
        
    Returns:
        str: String representation of all tasks from the database
    """
    try:
        return str(get_all_tasks())
    except Exception as e:
        return f"Error retrieving tasks: {str(e)}"

@tool
def get_task_by_date_tool(date: str):
    """
    Get tasks by date on a particular date. Ideal for fetching all tasks scheduled for a specific date.
    
    Args:
        date (str): Date to filter tasks by, expected in format 'dd:mm:yyyy'
        
    Returns:
        str: String representation of all tasks matching the specified date
    """
    return str(get_task_by_date(date))

@tool
def get_task_by_time_tool(time: str):
    """
    Get tasks by time on a particular time. Ideal for fetching all tasks scheduled at a specific time.
    
    Args:
        time (str): Time to filter tasks by, expected in format 'hh:mm:ss' (24-hour format)
        
    Returns:
        str: String representation of all tasks matching the specified time
    """
    return str(get_task_by_time(time))

@tool
def get_task_by_date_time_tool(date: str, time: str):
    """
    Get task by date and time on a particular date and time. Returns a specific unique task.
    
    Args:
        date (str): Date of the task in format 'dd:mm:yyyy'
        time (str): Time of the task in format 'hh:mm:ss' (24-hour format)
        
    Returns:
        str: String representation of task with the given date and time, or None if no match found
    """
    return str(get_task_by_date_time(date, time))

@tool
def create_task_tool(name: str, description: str, status: str, time: str, date: str, priority: str):
    """
    Create a task in the database with the provided details.
    
    Args:
        name (str): Name/title of the task
        description (str): Detailed description of the task
        status (str): Current status of the task ['completed', 'pending', 'in progress']
        time (str): Time in 'hh:mm:ss' format (24-hour format)
        date (str): Date in 'dd:mm:yyyy' format
        priority (str): Priority level of the task ['high', 'medium', 'low']
        
    Returns:
        str: String representation of the created task including its generated ID
    """
    task = {"name": name, "description": description, "status": status, "time": time, "date": date, "priority": priority}
    return str(create_task(task))

@tool
def update_task_tool(date: str, time: str, name: str, description: str, status: str, new_time: str, new_date: str, priority: str):
    """
    Update an existing task identified by original date and time with new values.
    
    Args:
        date (str): Original date of the task to update in format 'dd:mm:yyyy'
        time (str): Original time of the task to update in format 'hh:mm:ss'
        name (str): New or updated name/title of the task
        description (str): New or updated description of the task
        status (str): New or updated status ['completed', 'pending', 'in progress']
        new_time (str): New time for the task in 'hh:mm:ss' format (24-hour)
        new_date (str): New date for the task in 'dd:mm:yyyy' format
        priority (str): New or updated priority level ['high', 'medium', 'low']
        
    Returns:
        str: String representation of the updated task, or None if no task matched
              the original date and time
    """
    task = {"name": name, "description": description, "status": status, "time": new_time, "date": new_date, "priority": priority}
    return str(update_task(date, time, task))

@tool
def delete_task_tool(date: str, time: str):
    """
    Delete a task from the database identified by its date and time.
    
    Args:
        date (str): Date of the task to delete in format 'dd:mm:yyyy'
        time (str): Time of the task to delete in format 'hh:mm:ss' (24-hour format)
        
    Returns:
        str: Success message if task was deleted, or failure message if no matching task found
    """
    result = delete_task(date, time)
    return "Task deleted" if result else "Task not found"

@tool
def create_memory(user_input: str):
    """
    Create a memory in the vector database with the user input.
    
    This tool embeds user input into a vector representation and stores it in Pinecone for
    later retrieval. Please don't use this tool unless explicitly instructed to do so.
    
    Args:
        user_input (str): Text content to be vectorized and stored as a memory
        
    Returns:
        str: Confirmation message with the stored content or error message
    """
    return embedder(user_input)

@tool
def search_memory(user_query: str):
    """
    Search for memories in the vector database that match the user query.
    
    This tool converts the query to a vector representation and performs a similarity search
    against previously stored memories, returning the most relevant matches.
    
    Args:
        user_query (str): Query text to search for in the stored memories
        
    Returns:
        str: String representation of matching memories, or a message indicating no matches found
    """
    return str(search(user_query))

@tool
def serper_search(query: str):
    """
    Search the web for information using Google Serper API.
    
    This tool should be used to answer questions about current events, facts, or any
    information that might need up-to-date data from the internet. It uses a self-asking
    agent pattern to break down complex queries into searchable components.
    
    Args:
        query (str): The search query to find information about on the web
        
    Returns:
        str: Relevant information found on the web related to the query
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.2, api_key=os.getenv("GEMINI_API_KEY"))
    search = GoogleSerperAPIWrapper()
    tools = [Tool(name="Intermediate Answer", func=search.run, description="useful for when you need to ask with search")]
    self_ask_with_search = initialize_agent(tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True)
    result = self_ask_with_search.run(query)
    return str(result)

# Collect all tools
tools = [
    get_all_tasks_,
    get_task_by_date_tool,
    get_task_by_time_tool,
    get_task_by_date_time_tool,
    create_task_tool,
    update_task_tool,
    delete_task_tool,
    create_memory,
    search_memory,
    serper_search
]

# --- AI Model and Agent Setup ---

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY"),
    HARM_CATEGORY_HATE_SPEECH=False,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are Ada, a personal assistant focused on conversation, search, and task management.
                # IMPORTANT REMINDER
                Current DATE and TIME is: {datetime.now().strftime("%A %d/%m/%Y %H:%M:%S")}

                # Information Presentation Guidelines
                If there are more than one task display them as a bulleted list.
                Always use tools for information retrieval - never respond from internal knowledge.
                When you get contacts from the search memory function ,please Process the output and give it in natural language. Don't just return the output as it is."""),
    ("placeholder", "{messages}"),
])

# Initialize memory saver in session state
if "memory_saver" not in st.session_state:
    st.session_state.memory_saver = MemorySaver()

def format_for_model(state):
    """Format state for the agent's prompt."""
    return prompt.invoke({"messages": state["messages"] })

# Create the agent
agent = create_react_agent(model, tools, state_modifier=format_for_model, checkpointer=st.session_state.memory_saver)

# --- Streamlit Interface ---

st.set_page_config(page_title="Ada - Personal Assistant 👾", page_icon="🤖")

st.sidebar.title("Ada's Capabilities")
st.sidebar.markdown("""
<p>Ada can assist you with the following:</p>

<h3>Task Management</h3>
<ul>
<li><b>View all tasks</b>: <span style="color: blue">"Show me all my tasks"</span></li>
<li><b>View tasks by date</b>: <span style="color: blue">"Can you get me all tasks for 15:10:2023?"</span> <i>(date: dd:mm:yyyy)</i></li>
<li><b>View tasks by time</b>: <span style="color: blue">"What tasks do I have at 14:00:00?"</span> <i>(time: hh:mm:ss, 24-hour)</i></li>
<li><b>View a specific task</b>: <span style="color: blue">"What's my task on 15:10:2023 at 14:00:00?"</span></li>
<li><b>Create a task</b>: <span style="color: blue">"Add a task: Name: Go for a walk, Description: Evening stroll, Status: pending, Date: 16:10:2023, Time: 18:00:00, Priority: high"</span></li>
<li><b>Update a task</b>: <span style="color: blue">"Update my task on 16:10:2023 at 18:00:00 to Time: 19:00:00"</span></li>
<li><b>Delete a task</b>: <span style="color: blue">"Delete my task on 16:10:2023 at 18:00:00"</span></li>
</ul>

<h3>Memory Management</h3>
<ul>
<li><b>Store information</b>: <span style="color: blue">"Remember that my friend's birthday is on 20:10:2023"</span></li>
<li><b>Retrieve information</b>: <span style="color: blue">"When is my friend's birthday?"</span></li>
</ul>

<h3>Web Search</h3>
<ul>
<li><b>Get information</b>: <span style="color: blue">"What's the weather like today?"</span> or <span style="color: blue">"Who won the last World Cup?"</span></li>
</ul>

<h3>Important Notes</h3>
<ul>
<li>To make Ada remember something forever, explicitly say <span style="color: blue">"Remember that..."</span> or <span style="color: blue">"Store this information..."</span>. She can retrieve it later when you ask!</li>
<li>For tasks, include all details (name, description, status, date, time, priority) when creating or updating.</li>
<li>Use date format <code>dd:mm:yyyy</code> (e.g., 15:10:2023) and time format <code>hh:mm:ss</code> (e.g., 14:00:00).</li>
</ul>
""", unsafe_allow_html=True)

st.title('Ada - Personal Assistant')

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = "human" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Handle user input
user_query = st.chat_input("You're talking to Ada")
if user_query:
    human_message = HumanMessage(f"{user_query}")
    st.session_state.messages.append(human_message)
    with st.chat_message("human"):
        st.markdown(user_query)
    
    config = {"configurable": {"thread_id": st.session_state.get("thread_id", "default")}}
    with st.spinner("Ada is thinking..."):
        response = agent.invoke({"messages": [human_message]}, config=config)
        ai_response = response["messages"][-1].content
    st.session_state.messages.append(AIMessage(ai_response))
    with st.chat_message("assistant"):
        st.markdown(ai_response)