from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, Any, List
import re
import os

class ChatbotManager:
    def __init__(self, api_keys: dict, config: Dict[str, Any]):
        """Initialize the ChatbotManager with API keys and configuration."""
        self.api_keys = api_keys
        self.config = config
        self.tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self._setup_memory()
        self.model = "llama-3.3-70b-versatile"
        self.llm = self._initialize_llm(self.model)
        self.tools = self._initialize_tools()
        self.model_selector_agent = self._create_model_selector_agent()
        self.chat_history = []

    def _setup_memory(self) -> None:
        """Setup conversation memory with proper configuration."""
        self.msgs = StreamlitChatMessageHistory(key="langchain_messages")
        self.memory = ConversationBufferMemory(
            chat_memory=self.msgs,
            return_messages=True,
            memory_key="chat_history",
            output_key="output",
            input_key="input"
        )

    def _initialize_llm(self, model: str = "llama-3.3-70b-versatile") -> ChatGroq:
        """Initialize LLM with specified model and configuration."""
        self.model = model
        return ChatGroq(
            api_key=self.api_keys['groq_api_key'],
            model=model,
            streaming=True,
            stop=None,
            callbacks=self._get_callbacks() if self.tracing_enabled else None
        )

    def _get_callbacks(self) -> List[Any]:
        """Get callbacks for LangChain tracing if enabled."""
        if self.tracing_enabled:
            try:
                from langchain.callbacks import LangChainTracer
                return [LangChainTracer()]
            except ImportError:
                return []
        return []

    def _initialize_tools(self) -> List[Tool]:
        """Initialize and configure available tools."""
        search = DuckDuckGoSearchAPIWrapper(
            max_results=5,
            time='d',
            safesearch='moderate'
        )
        
        def search_with_fallback(*args, **kwargs) -> str:
            """Wrapper function to handle rate limiting."""
            try:
                return search.run(*args, **kwargs)
            except Exception as e:
                if "Ratelimit" in str(e):
                    return (
                        "I apologize, but I'm currently rate-limited from performing web searches. "
                        "I'll try to answer based on my existing knowledge. If you need specific "
                        "current information, please try again in a few minutes."
                    )
                raise e

        return [
            Tool(
                name="Web Search",
                func=search_with_fallback,
                description="Useful for finding current information from the web. Use for specific queries about current events, facts, or general knowledge.",
                return_direct=False
            )
        ]

    def _create_model_selector_agent(self) -> Any:
        """Create the model selection agent."""
        selector_llm = ChatGroq(
            api_key=self.api_keys['groq_api_key'],
            model="llama-3.1-8b-instant",
            streaming=False,
            temperature=0.3,
            max_tokens=512
        )
        
        model_selection_prompt = PromptTemplate.from_template("""
        You are a model selection expert. Analyze the user's input and select the most appropriate model based on the task requirements.
        
        Available models and their specializations:
        {model_specs}
        
        User input: {input}
        Task type: {task_type}
        
        Select the most appropriate model and explain your reasoning.
        Output format: <model>model_name</model><reasoning>your explanation</reasoning>
        """)
        
        return model_selection_prompt | selector_llm

    def get_response(self, user_input: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
        """Get a response from the chatbot using the appropriate model."""
        try:
            task_type = self._determine_task_type(user_input)
            
            # Add rate limit handling for model selection
            try:
                selection_response = self.model_selector_agent.invoke({
                    "model_specs": self.model_specs,
                    "input": user_input,
                    "task_type": task_type
                })
            except Exception as e:
                if "Ratelimit" in str(e):
                    # Use default model if rate limited
                    selection_response = AIMessage(content=f"<model>{self.model}</model><reasoning>Using default model due to rate limiting</reasoning>")
                else:
                    raise e
            
            selection_text = selection_response.content if hasattr(selection_response, 'content') else str(selection_response)
            
            model_match = re.search(r'<model>(.*?)</model>', selection_text)
            reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', selection_text)
            
            selected_model = model_match.group(1) if model_match else "llama-3.3-70b-versatile"
            reasoning = reasoning_match.group(1) if reasoning_match else ""
            
            if selected_model != self.model:
                self.llm = self._initialize_llm(selected_model)
            
            react_agent = create_react_agent(
                self.llm,
                self.tools,
                hub.pull("hwchase17/react-chat")
            )
            
            agent_executor = AgentExecutor(
                agent=react_agent,
                tools=self.tools,
                memory=self.memory,
                handle_parsing_errors=True,
                max_iterations=8,
                early_stopping_method="force",
                verbose=True,
                return_intermediate_steps=True
            )
            
            response = agent_executor.invoke(
                {
                    "input": user_input.strip(),
                    "chat_history": self.memory.chat_memory.messages if self.memory else []
                },
                cfg
            )
            
            response['output'] = self._format_response(response['output'], selected_model, reasoning)
            
            self._update_chat_history(user_input, response['output'])
            
            return response
            
        except Exception as e:
            return self._handle_error("response", str(e))

    def document_retrieval(self, vector_store: Any, input_query: str) -> Dict[str, str]:
        """Enhanced RAG implementation for document retrieval and response generation."""
        try:
            template = """
            You are a helpful AI assistant. Answer the question based on the provided context.
            
            Guidelines:
            1. Use ONLY information from the provided context
            2. If the answer isn't in the context, say "I cannot find this information in the provided documents"
            3. If you need more context, say "I would need additional context to fully answer this question"
            4. When citing information, specify the source document and page number
            5. If the context contains code, format it properly using markdown
            6. Keep responses clear and well-structured
            7. If multiple documents provide conflicting information, acknowledge this and explain the differences
            8. If the question requires information from multiple documents, synthesize the information clearly
            
            Context:
            {context}
            
            Question: {question}
            
            Previous Discussion:
            {chat_history}
            
            Response Format:
            
            ANSWER:
            [Your detailed answer here]
            
            SOURCES:
            [List the source documents and page numbers used]
            
            CONFIDENCE:
            [High/Medium/Low - Based on the completeness and relevance of the context]
            
            ADDITIONAL CONTEXT NEEDED:
            [Yes/No - Specify what additional context would be helpful if needed]
            """
            
            prompt = ChatPromptTemplate.from_template(template)

            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 4,
                    "fetch_k": 8,
                    "lambda_mult": 0.7
                }
            )

            rag_chain = (
                {
                    "context": retriever,
                    "question": RunnablePassthrough(),
                    "chat_history": lambda x: self._format_chat_history()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(input_query)
            self._update_chat_history(input_query, response)
            
            return {"output": response}

        except Exception as e:
            return self._handle_error("document_retrieval", str(e))

    def _determine_task_type(self, input_text: str) -> str:
        """Determine the type of task from user input."""
        input_lower = input_text.lower()
        if any(word in input_lower for word in ['code', 'program', 'function', 'bug', 'error']):
            return "coding"
        elif any(word in input_lower for word in ['image', 'picture', 'photo', 'diagram']):
            return "visual"
        elif len(input_lower.split()) > 50:
            return "analysis"
        else:
            return "quick_lookup"

    def _format_response(self, response: str, model: str, reasoning: str) -> str:
        """Format the response with model information and proper formatting."""
        formatted_response = response.strip()
        model_info = f"\n\n---\n**Model:** {model}"
        if reasoning:
            model_info += f"\n**Reasoning:** {reasoning}"
        return formatted_response + model_info

    def _format_chat_history(self) -> List[Dict[str, str]]:
        """Format chat history for the prompt."""
        if not self.memory or not self.memory.chat_memory.messages:
            return []
        
        formatted_history = []
        for msg in self.memory.chat_memory.messages[-5:]:  
            if isinstance(msg, (HumanMessage, AIMessage)):
                formatted_history.append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                })
        return formatted_history

    def _update_chat_history(self, user_input: str, response: str) -> None:
        """Update chat history with new interaction."""
        if self.memory:
            self.memory.save_context(
                {"input": user_input},
                {"output": response}
            )

    def _handle_error(self, context: str, error_msg: str) -> Dict[str, str]:
        """Handle errors with context-specific messages."""
        if "connection" in error_msg.lower():
            return {"output": f"⚠️ Connection error in {context}: Please check your internet connection and try again."}
        elif "permission" in error_msg.lower():
            return {"output": f"⚠️ Permission error in {context}: Please check your access permissions."}
        elif "timeout" in error_msg.lower():
            return {"output": f"⚠️ Timeout error in {context}: The operation took too long. Please try again."}
        else:
            return {"output": f"⚠️ Error in {context}: {error_msg}"}

    @property
    def model_specs(self) -> str:
        """Get formatted model specifications from config."""
        model_details = []
        for model, details in self.config['models'].items():
            spec = f"- {model}:\n"
            spec += f"  Description: {details['description'].strip()}\n"
            spec += f"  Use cases: {', '.join(details['use_case'])}\n"
            spec += f"  Context window: {details['context_window']} tokens\n"
            model_details.append(spec)
        
        return "\n".join(model_details)