import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from app.database_manager import DatabaseManager
from app.document_processor import DocumentProcessor
import time

class UIComponents:
    def __init__(self, config):
        self.config = config
        self.state = self._initialize_state()
        
    def _initialize_state(self):
        if "local_database" not in st.session_state:
            st.session_state.local_database = []
        if "external_database" not in st.session_state:
            st.session_state.external_database = None
        if "db_manager" not in st.session_state:
            st.session_state.db_manager = None

    def enter_api_key(self):
        if "groq_api_key" in st.secrets:
            groq_api_key = st.secrets.groq_api_key
        else:
            groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
            if not groq_api_key:
                st.info("Enter a Groq API Key to continue")
                st.stop()
            
        return {"groq_api_key": groq_api_key}
    
    def create_chat_history(self):
        if st.session_state.langchain_messages:
            for message in st.session_state.langchain_messages:
                if isinstance(message, dict):
                    # Handle dictionary-style messages
                    role = message.get("role", "user")
                    content = message.get("content", "")
                else:
                    # Handle LangChain message objects
                    role = message.type if hasattr(message, 'type') else "user"
                    content = message.content if hasattr(message, 'content') else str(message)

                with st.chat_message(role):
                    st.markdown(content)
    
    def create_chat_interface(self, chatbot_manager):
        self.create_chat_history()
        output_container = st.empty()
        
        user_input = st.chat_input("Type your message here...")

        if user_input:
            output_container = output_container.container()
            output_container.chat_message("user").write(user_input)

            answer_container = output_container.chat_message("assistant")
            st_callback = StreamlitCallbackHandler(answer_container)
            cfg = RunnableConfig()
            cfg["callbacks"] = [st_callback]

            try:
                # Get the response and simulate the callback
                answer = chatbot_manager.get_response(user_input, cfg)
                answer_container.write(answer["output"])
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()
        if st.session_state.langchain_messages:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Clear Chat History"):
                    st.session_state.clear()
                    st.rerun()
            
    def create_file_uploader(self, name="Upload files"):    
        uploaded_files = st.file_uploader(
            name,
            type=["pdf"],
            accept_multiple_files=True,
            help="Select one or more files to upload"
        )
        
        if uploaded_files:
            existing_files = {file['name'] for file in st.session_state.local_database}
            new_files = [f for f in uploaded_files if f.name not in existing_files]
            
            if new_files:
                self._process_pdf_files(new_files)
                
            return new_files
        
    def _process_pdf_files(self, new_files):
        
        doc_processor = DocumentProcessor()
        chunks = doc_processor.chunk_pdf(new_files)
        
        # Store files and their chunks in local_database
        for uploaded_file in new_files:
            file_chunks = [c for c in chunks if c.metadata["file_name"] == uploaded_file.name]
            st.session_state.local_database.append({
                "file": uploaded_file,
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "timestamp": time.time(),
                "chunks": file_chunks
            })
            st.success(f"Successfully uploaded and processed {uploaded_file.name}!")
            # st.session_state.new_files_added.append(uploaded_file.name)
            # st.rerun()
                    
    def create_database_connection(self):  
        # Database type selection
        db_type = st.sidebar.selectbox(
            "Select Database Type",
            options=["MySQL", "SQLite", "PostgreSQL", "MongoDB", "Qdrant"]
        )
        
        # Connection method
        connection_method = st.sidebar.radio(
            "Connection Method",
            options=["File", "URL", "Custom"]
        )
        
        connection_params = {}
        
        if connection_method == "File":
            uploaded_file = st.sidebar.file_uploader(
                "Upload Database File",
                type=["db", "sqlite", "sqlite3"] if db_type == "SQLite" else None
            )
            if uploaded_file:
                connection_params['file_path'] = uploaded_file
                
        elif connection_method == "URL":
            connection_params['url'] = st.sidebar.text_input("Database URL")
            if db_type == "Qdrant":
                connection_params['api_key'] = st.sidebar.text_input("API Key", type="password")
                
        else:  # Custom
            default_ports = {
                "MySQL": 3306,
                "PostgreSQL": 5432,
                "MongoDB": 27017,
                "Qdrant": 6333
            }
            if db_type != "SQLite":
                connection_params.update({
                    'host': st.sidebar.text_input("Host"),
                    'port': st.sidebar.number_input("Port", value=default_ports.get(db_type, 0)),
                    'username': st.sidebar.text_input("Username"),
                    'password': st.sidebar.text_input("Password", type="password"),
                    'database': st.sidebar.text_input("Database Name")
                })
            else:
                connection_params.update({
                    'database': st.sidebar.text_input("Database Name")
                })

        # Connection button and handling
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Connect" if not st.session_state.external_database else "Disconnect"):
                if not st.session_state.external_database:
                    try:
                        st.session_state.db_manager = DatabaseManager(db_type, connection_params)
                        st.session_state.external_database = st.session_state.db_manager.create_connection()
                        st.sidebar.success("Successfully connected to database!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Failed to connect: {str(e)}")
                else:
                    try:
                        st.session_state.db_manager.disconnect()
                        st.session_state.external_database = None
                        st.session_state.db_manager = None
                        st.sidebar.success("Successfully disconnected from database!")
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Failed to disconnect: {str(e)}")

        # Connection status display - moved here and simplified
        with st.sidebar.expander("Connection Status", expanded=True):
            if st.session_state.db_manager is None:
                st.markdown("Status: :red[●] Disconnected")
            else:
                conn_info = st.session_state.db_manager.get_connection_info()
                status_color = "green" if conn_info["status"] == "connected" else "orange"
                st.markdown(f"Status: :{status_color}[●] {conn_info['status'].title()}")
                
                if conn_info["connected_since"]:
                    st.caption(f"Connected since: {conn_info['connected_since'].strftime('%Y-%m-%d %H:%M:%S')}")
                if conn_info["last_error"]:
                    st.error(f"Last Error: {conn_info['last_error']}")

    def create_database_details(self):
        if st.session_state.local_database or st.session_state.external_database:
            st.divider()
            st.sidebar.title("📚 Database Contents")
            
            if st.session_state.local_database:
                st.sidebar.subheader(f"**Local Files:**")
                with st.sidebar.expander("Local Files Details", expanded=False):
                    st.caption(f"**Local Files:** {len(st.session_state.local_database)}")
                    for file in st.session_state.local_database:
                        file_type = file['type'].lower()
                        icon = self.config['file_icons'].get(file_type, '📄')
                        st.markdown(f"{icon} **{file['name']}**")
                        
            if st.session_state.external_database:
                st.sidebar.subheader(f"**External Database:**")
                with st.sidebar.expander("Database Details", expanded=False):
                    st.write(st.session_state.external_database)