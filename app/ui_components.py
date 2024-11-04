import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from app.database_manager import DatabaseManager
import time

class UIComponents:
    def __init__(self, config):
        self.config = config
        self.state = self._initialize_state()
        
    def _initialize_state(self):
        if "database" not in st.session_state:
            st.session_state.database = []
        if "external_database" not in st.session_state:
            st.session_state.external_database = None

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
            
    def create_file_uploader(self):
        uploaded_files = st.sidebar.file_uploader("Upload files", 
                                                    type=["pdf"], 
                                                        accept_multiple_files=True
                                                        )
        
        current_files = [file['file'] for file in st.session_state.database]
        for uploaded_file in uploaded_files:
                if uploaded_file not in current_files:
                    file_contents = uploaded_file.read()
                    st.session_state.database.append({
                        "file": uploaded_file,
                        "content": file_contents,
                        "name": uploaded_file.name,
                        "type": uploaded_file.type
                    })
            
        st.session_state.database = [
            file for file in st.session_state.database
            if file['file'] in uploaded_files
        ]
        return uploaded_files

    def display_database(self):
        if st.session_state.database or st.session_state.external_database:
            st.sidebar.markdown("## 📚 Database Contents")
            
            if st.session_state.database:
                st.sidebar.markdown(f"**Local Files:** {len(st.session_state.database)}")
                with st.sidebar.expander("View Local Files", expanded=False):
                    for file in st.session_state.database:
                        file_type = file['type'].lower()
                        icon = self.config['file_icons'].get(file_type, '📄')
                        st.markdown(f"{icon} **{file['name']}**")
                        st.caption(f"Type: {file_type}")
                        st.caption(f"Size: {len(file['content'])} bytes")
                        st.divider()
            
            if st.session_state.external_database:
                st.sidebar.markdown(f"**External Database:** Connected")
                with st.sidebar.expander("External Database Info", expanded=False):
                    st.write(st.session_state.external_database)

        # Main content area display

        with st.expander("Database Overview", icon="📊", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Local Files", len(st.session_state.database))
            
            with col2:
                st.metric("External Database", "Connected" if st.session_state.external_database else "Not Connected")
                
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
        
        # Initialize db_manager in session state
        if "db_manager" not in st.session_state:
            st.session_state.db_manager = None

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

        # Database details
        if st.session_state.external_database and st.session_state.db_manager:            
            with st.sidebar.expander("Database Details", expanded=False):
                st.write(st.session_state.external_database)