from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_groq import ChatGroq
from sqlalchemy import create_engine
import sqlite3
from .search_engine import SerpAPISearchEngine

class ChatbotManager:
    def __init__(self, api_keys : dict, config, model="mixtral-8x7b-32768", db_path=None):
        self.api_keys = api_keys
        self.db_path = db_path
        self.config = config
        self.model = model
        self.llm = ChatGroq(api_key=api_keys['groq_api_key'], model=model, streaming=True)
        self.tools = self._initialize_tools()
        self.msgs = StreamlitChatMessageHistory(key="langchain_messages")
        self.memory = ConversationBufferMemory(chat_memory=self.msgs, return_messages=True, memory_key="chat_history", output_key="output")
        self.agent = self._initialize_agent()

    def _initialize_tools(self):
        if 'sarpapi_api_key' in self.api_keys and self.api_keys['sarpapi_api_key']:
            search = SerpAPISearchEngine(api_key=self.api_keys['sarpapi_api_key'])
        else:
            search = DuckDuckGoSearchAPIWrapper(max_results=5)
        
        llm_math_chain = LLMMathChain.from_llm(self.llm)
        tools = [
            Tool(
                name="Web Search",
                func=search.run, 
                description="useful for when you need to answer questions about current events, social media, university articles, etc. You should ask targeted questions",
            ),
            Tool(
                name="Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math",
            ),
            Tool(
                name="Ask for information",
                func=self._ask_user,
                description="Use this tool frequently to gather more information from the user. It's essential for clarification, obtaining specific details, or when you need additional context to provide a more accurate or comprehensive answer. Always use this tool when you don't know something or are unsure about any aspect of the user's query. Consider using it before making assumptions or providing incomplete answers.",
            )
        ]
        
        if self.db_path:
            creator = lambda: sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            db = SQLDatabase(create_engine("sqlite:///", creator=creator))
            db_chain = SQLDatabaseChain.from_llm(self.llm, db)
            tools.append(
                Tool(
                    name="Database Query",
                    func=db_chain.run,
                    description="useful for when you need to answer questions about the database. Input should be in the form of a question containing full context",
                )
            )
        return tools

    def _initialize_agent(self):
        react_agent = create_react_agent(
            self.llm,
            self.tools,
            hub.pull("hwchase17/react-chat")
        )
        return AgentExecutor(
            agent=react_agent,
            tools=self.tools,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=8,
            early_stopping_method="generate"
        )
        
    def _ask_user(self, question):
        return input("User: ")

    def get_response(self, user_input, cfg):
        try:
            response = self.agent.invoke({"input": user_input}, cfg)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to get response: {e}")