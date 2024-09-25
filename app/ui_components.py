import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig

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

    def clear_chat_history(self):
        if st.sidebar.button("Clear Chat History"):
            st.session_state.clear()
            st.sidebar.success("Chat history cleared!")
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
                
    def connect_external_database(self):
        st.session_state.external_database = st.sidebar.text_input("External Database URL", disabled=True) or st.sidebar.button("Connect to External Database", disabled=True)
