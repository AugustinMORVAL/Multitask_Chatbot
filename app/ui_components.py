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
            st.session_state.local_database = None
        if "external_database" not in st.session_state:
            st.session_state.external_database = None
        if "db_manager" not in st.session_state:
            st.session_state.db_manager = None
        if "document_stats" not in st.session_state:
            st.session_state.document_stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "processed_files": set(),
                "last_update": None,
                "file_details": {}
            }
            
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
                    role = message.get("role", "user")
                    content = message.get("content", "")
                else:
                    role = message.type if hasattr(message, 'type') else "user"
                    content = message.content if hasattr(message, 'content') else str(message)

                with st.chat_message(role):
                    st.markdown(content)
    
    def create_chat_interface(self, chatbot_manager):
        self.create_chat_history()
        
        user_input = st.chat_input("Type your message here...")
        if user_input:
            self._handle_user_input(user_input, chatbot_manager)
    
    def _show_document_context(self):
        if not st.session_state.local_database:
            st.warning("📚 Please upload documents to use document context.")
            return
            
        with st.expander("📊 Document Statistics", expanded=False):
            stats = st.session_state.document_stats
            st.write(f"Total Documents: {stats.get('total_documents', 0)}")
            st.write(f"Total Chunks: {stats.get('total_chunks', 0)}")
            st.write(f"Last Updated: {stats.get('last_update', 'Never')}")
            
            if stats.get('file_details'):
                st.divider()
                st.subheader("📑 Processed Files")
                for filename, details in stats['file_details'].items():
                    with st.expander(f"📄 {filename}"):
                        st.write(f"Chunks: {details.get('chunks', 0)}")
                        st.write(f"Total Pages: {details.get('total_pages', 0)}")
                        st.write(f"Average Chunk Size: {int(details.get('average_chunk_size', 0))} chars")
                        st.write(f"Processed At: {details.get('processed_at', 'Unknown')}")
    
    def _process_pdf_files(self, new_files):
        doc_processor = DocumentProcessor()
        
        with st.spinner("Processing documents..."):
            progress_bar = st.progress(0)
            for idx, file in enumerate(new_files):
                progress = (idx + 1) / len(new_files)
                progress_bar.progress(progress)
                
                chunks, vector_store = doc_processor.chunk_pdf([file])
                if vector_store:
                    st.session_state.local_database = vector_store
                
            progress_bar.empty()
    
    def _show_chat_controls(self):
        if st.session_state.langchain_messages:
            if st.button("Clear Chat History"):
                st.session_state.clear()
                st.rerun()
    
    def _handle_user_input(self, user_input, chatbot_manager, use_documents=False):
        output_container = st.empty()
        output_container.chat_message("user").write(user_input)

        answer_container = output_container.chat_message("assistant")
        st_callback = StreamlitCallbackHandler(answer_container)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_callback]

        try:
            if use_documents:
                if not st.session_state.local_database:
                    answer_container.warning("No documents are loaded for context. Proceeding with standard response.")
                    response = chatbot_manager.get_response(user_input, cfg)
                else:
                    response = chatbot_manager.document_retrieval(st.session_state.local_database, user_input)
            else:
                response = chatbot_manager.get_response(user_input, cfg)
            
            answer_container.write(response["output"])
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

    def create_file_uploader(self, name="Upload files"):    
        uploaded_files = st.file_uploader(
            name,
            type=["pdf"],
            accept_multiple_files=True,
            help="Select one or more files to upload"
        )
        
        if uploaded_files:
            processed_files = st.session_state.document_stats["processed_files"]
            new_files = [f for f in uploaded_files if f.name not in processed_files]
            
            if new_files:
                self._process_pdf_files(new_files)
                
            return new_files
        
    def create_database_connection(self):  
        db_type = st.sidebar.selectbox(
            "Select Database Type",
            options=["MySQL", "SQLite", "PostgreSQL", "MongoDB", "Qdrant"]
        )
        
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

        # Connection status display
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