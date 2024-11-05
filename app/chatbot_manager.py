from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

class ChatbotManager:
    def __init__(self, api_keys : dict, config, model="llama3-70b-8192"):
        self.api_keys = api_keys
        self.config = config
        self.model = model
        self.llm = ChatGroq(
            api_key=api_keys['groq_api_key'], 
            model=model, 
            streaming=True,
            system_prompt=config['system_prompt']['value']
        )
        self.msgs = StreamlitChatMessageHistory(key="langchain_messages")
        self.memory = ConversationBufferMemory(chat_memory=self.msgs, return_messages=True, memory_key="chat_history", output_key="output")
        self.tools = self._initialize_tools()
        self.agent = self._initialize_agent()

    def _initialize_tools(self):
        search = DuckDuckGoSearchAPIWrapper(max_results=10)
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
                description="""Use this tool to gather more information from the user when:
                1. The query is ambiguous or lacks context
                2. You need specific details to provide an accurate answer
                3. You're unsure about any aspect of the user's request
                4. Multiple interpretations of the query are possible
                5. The user's intent is not clear
                6. You need to confirm an assumption before proceeding
                7. The query touches on personal preferences or subjective information
                Only use this tool when absolutely necessary to avoid excessive back-and-forth. Frame your questions clearly and concisely.""",
            )
        ]
        
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
            early_stopping_method="generate",
            verbose=True
        )
        
    def _ask_user(self, question):
        return input("User: ")

    def get_response(self, user_input, cfg):
        try:
            response = self.agent.invoke({"input": user_input}, cfg)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to get response: {e}")
        
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