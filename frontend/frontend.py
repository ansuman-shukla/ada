import sys
sys.path.append('C:\\Users\\Manan Agrawal\\Documents\\WORK\\Python101\\ada')


import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
import os
from services.retriverServices import *
from services.taskServices import *
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.chat_agent_executor import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
import os
import streamlit as st
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from tools.task_tools import *

class AIManager:
    """Manages AI model initialization and responses"""
    
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            api_key=os.getenv("GEMINI_API_KEY"),
            HARM_CATEGORY_HATE_SPEECH=False,
        )
        self.tools = ToolManager.get_tools()    # Call get_tools on instance
        self.prompt = self._create_prompt()
    



    def _create_prompt(self):
        """Create the chat prompt template"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are Ada, a personal assistant focused on conversation, search, and task management.
                    # IMPORTANT REMINDER
                    Always use tools for information retrieval - never respond from internal knowledge."""),         
            ("placeholder", "{messages}"),
            ("user" ,f"Current DATE and TIME is :-{datetime.now().strftime("(%A %d/%m/%Y %H:%M:%S")}")
        ])
        
    def get_response(self, user_query: str) -> str:
        """Generate AI response for user query"""
        def format_for_model(state):
            return self.prompt.invoke({"messages": state["messages"]})
            
        agent = create_react_agent(
            self.model,
            self.tools,
            state_modifier=format_for_model,
            checkpointer=st.session_state.memory_saver
        )
        
        config = {"configurable": {"thread_id": st.session_state.get("thread_id", "default")}}
        response = agent.invoke(
            {"messages": [HumanMessage(content=f"{user_query} + Current DATE and TIME is :-{datetime.now().strftime("(%A %d/%m/%Y %H:%M:%S")}")]},
            config=config
        )
        
        return response["messages"][-1].content


class ChatStateManager:
    """Manages chat state and message history"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize or reset session state with default values"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "memory_saver" not in st.session_state:
            st.session_state.memory_saver = MemorySaver()
            
    @staticmethod
    def add_message(message):
        """Add a message to the chat history"""
        st.session_state.messages.append(message)
        
    @staticmethod
    def get_messages():
        """Retrieve all messages from chat history"""
        return st.session_state.messages


class ChatInterface:
    """Manages the chat interface and message display"""
    
    def __init__(self):
        self.ai_manager = AIManager()
        ChatStateManager.initialize_session_state()

    def setup_interface(self):
        """Set up the Streamlit interface"""
        st.set_page_config(page_title="Ada - Personal Assistant", page_icon="🤖")
        st.title('Ada - Personal Assistant')

    def display_chat_history(self):
        """Display existing chat history"""
        for message in ChatStateManager.get_messages():
            if isinstance(message, (HumanMessage, AIMessage)):
                role = "human" if isinstance(message, HumanMessage) else "assistant"
                with st.chat_message(role):
                    st.markdown(message.content)

    def handle_user_input(self):
        """Process user input and generate response"""
        user_query = st.chat_input("You're talking to Ada")
        
        if user_query:
            # Add user message
            human_message = HumanMessage(user_query)
            ChatStateManager.add_message(human_message)
            with st.chat_message("human"):
                st.markdown(user_query)
            
            # Generate and display AI response
            with st.chat_message("assistant"):
                ai_response = self.ai_manager.get_response(user_query)
                st.markdown(ai_response)
                ChatStateManager.add_message(AIMessage(ai_response))

def main():
    """Main application entry point"""
    chat_interface = ChatInterface()
    chat_interface.setup_interface()
    chat_interface.display_chat_history()
    chat_interface.handle_user_input()

if __name__ == "__main__":
    main()