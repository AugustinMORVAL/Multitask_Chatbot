from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from typing import Dict
import re

class ChatbotManager:
    def __init__(self, api_keys: dict, config):
        self.api_keys = api_keys
        self.config = config
        self.msgs = StreamlitChatMessageHistory(key="langchain_messages")
        self.memory = ConversationBufferMemory(chat_memory=self.msgs, return_messages=True, memory_key="chat_history", output_key="output")
        self.tools = self._initialize_tools()
        self.model_selector_agent = self._create_model_selector_agent()
        self.model_specs = self._get_model_specs()

    def _initialize_tools(self):
        default_model = "llama-3.3-70b-versatile"
        self.llm = ChatGroq(
            api_key=self.api_keys['groq_api_key'],
            model=default_model,
            streaming=True
        )
        search = DuckDuckGoSearchAPIWrapper(max_results=10)
        tools = [
            Tool(
                name="Web Search",
                func=search.run, 
                description="useful for when you need to answer questions about current events, social media, university articles, etc. You should ask targeted questions",
            )
        ]
        
        return tools

    def _create_model_selector_agent(self):
        # Create a prompt for the model selection agent
        model_selection_prompt = PromptTemplate.from_template("""
        You are a model selection expert. Analyze the user's input and select the most appropriate model based on the task requirements.
        
        Available models and their specializations:
        {model_specs}
        
        User input: {input}
        
        Select the most appropriate model and explain your reasoning.
        Output format: <model>model_name</model><reasoning>your explanation</reasoning>
        """)
        
        # Initialize a basic LLM for model selection (using a smaller, faster model)
        selector_llm = ChatGroq(
            api_key=self.api_keys['groq_api_key'],
            model="llama-3.1-8b-instant",  # Using faster model for selection
            streaming=False
        )
        
        # Create the model selection chain
        return model_selection_prompt | selector_llm

    def get_response(self, user_input: str, cfg: Dict) -> str:
        try:
            # Get model selection response
            selection_response = self.model_selector_agent.invoke({
                "model_specs": self.model_specs,
                "input": user_input
            })
            
            # Convert AIMessage to string if needed
            selection_text = selection_response.content if hasattr(selection_response, 'content') else str(selection_response)
            
            # Parse the response to get the selected model
            model_match = re.search(r'<model>(.*?)</model>', selection_text)
            selected_model = model_match.group(1) if model_match else "llama-3.3-70b-versatile"
            
            # Initialize LLM with selected model
            llm = ChatGroq(
                api_key=self.api_keys['groq_api_key'],
                model=selected_model,
                streaming=True,
            )
            
            # Create agent with selected model
            react_agent = create_react_agent(
                llm,
                self.tools,
                hub.pull("hwchase17/react-chat")
            )
            
            # Update the agent executor configuration
            agent_executor = AgentExecutor(
                agent=react_agent,
                tools=self.tools,
                memory=self.memory,
                handle_parsing_errors=True,
                max_iterations=8,
                early_stopping_method="force", 
                verbose=True
            )
            
            # Error handling wrapper around the input
            sanitized_input = {
                "input": user_input.strip(),
                "chat_history": self.memory.chat_memory.messages if self.memory else []
            }
            
            response = agent_executor.invoke(sanitized_input, cfg)
            
            # Add model selection reasoning to the response
            reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', selection_text)
            reasoning = reasoning_match.group(1) if reasoning_match else ""
            response['output'] += f"\n\n**Selected Model:** {selected_model}\n**Selection Reasoning:** {reasoning}"
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Failed to get response: {e}")
    
    def _get_model_specs(self):
        model_details = []
        for model, details in self.config['models'].items():
            spec = f"- {model}:\n"
            spec += f"  Description: {details['description'].strip()}\n"
            spec += f"  Use cases: {', '.join(details['use_case'])}\n"
            spec += f"  Context window: {details['context_window']} tokens\n"

            model_details.append(spec)
        
        return "\n".join(model_details)
        
    def document_retrieval(self, vector_store, input_query):
        """Retrieve relevant documents and generate a response from the AI model."""
        try:
            template = """
            Tu es une assistante virtuelle serviable et dévouée. Ton rôle principal est d'aider l'utilisateur en fournissant 
            des réponses précises et réfléchies basées sur le contexte donné. Si l'utilisateur pose des questions liées aux 
            informations fournies, réponds de manière courtoise et professionnelle.

            IMPORTANT: Tu dois TOUJOURS répondre en français, quelle que soit la langue de la question.

            Contexte:
            {context}

            Question: {question}

            Instructions supplémentaires:
            - Utilise un langage professionnel mais accessible
            - Si tu ne trouves pas l'information dans le contexte, dis-le poliment
            - Reste toujours factuel et basé sur le contexte fourni
            """
            
            # Create a chat prompt template based on the defined template
            prompt = ChatPromptTemplate.from_template(template)

            # Configure retriever
            retriever = vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 4}
            )

            # Set up parallel execution to retrieve context and pass it with the question
            setup_and_retrieval = RunnableParallel(
                {"context": retriever, "question": RunnablePassthrough()}
            )

            # Initialize the Groq model
            model = self.llm

            # Define an output parser to handle the response formatting
            output_parser = StrOutputParser()

            # Chain the setup, prompt, model, and output parsing into one pipeline
            rag_chain = setup_and_retrieval | prompt | model | output_parser

            # Generate and return the response using the input query
            response = rag_chain.invoke(input_query)
            return response

        except Exception as ex:
            return f"Erreur: {str(ex)}"