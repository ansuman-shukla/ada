from langgraph.prebuilt.chat_agent_executor import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from tools.task_tools import ToolManager
from tools.sub_agents import *




class AIManager:
    """Manages AI model initialization and responses"""
    
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            api_key=os.getenv("GEMINI_API_KEY"),
            HARM_CATEGORY_HATE_SPEECH=False,
        )
        agents_manager = AgentsManager()
        self.tools = agents_manager.get_tools()
        self.prompt = self._create_prompt()
        
    def _create_prompt(self):
        """Create the chat prompt template"""
        return ChatPromptTemplate.from_messages([
            ("system", "You are Ada, a personal helpful assistant! You have Search and Task tools to help you.Use the tools wisely to get the data from the Internet using or manage or get task or Manage memory"),
            ("placeholder", "{messages}"),
            ("user", "Hello Ada!"),
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
            {"messages": [HumanMessage(content=f"{user_query} + Current DATE and TIME is :- {datetime.now().strftime("(%A %d/%m/%Y %H:%M:%S")} )")]},
            config=config
        )
        
        return response["messages"][-1].content
