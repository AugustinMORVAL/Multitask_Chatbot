import streamlit as st
import time

class UIComponents:
    def __init__(self, config):
        self.config = config
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = ""
        if "database" not in st.session_state:
            st.session_state.database = []
        if "external_databse" not in st.session_state: 
            st.session_state.external_database = []

    def create_sidebar(self):
        st.sidebar.title("Powered by AIugustin")
        model = st.sidebar.selectbox("Select a model", options=self.config['models'])
        cot_reflection = st.sidebar.toggle("Enable CoT reflection", value=False, help=self.config['cot_reflection']['help'])
        system_prompt = self.update_system_prompt(cot_reflection)
        show_cot_process = st.sidebar.toggle("Show CoT process", value=False, help="Show the CoT process in the response") if cot_reflection else False
        temperature = st.sidebar.slider("Temperature", **self.config['temperature_slider'])
        max_tokens = self.update_max_tokens(cot_reflection)
        reset_conversation = st.sidebar.button("Reset Conversation")
        parameters = self.set_parameters()
        
        return model, system_prompt, temperature, max_tokens, cot_reflection, show_cot_process, reset_conversation, parameters
    
    def update_system_prompt(self, cot_reflection):
        prompt_mode = "cot_reflection" if cot_reflection else "system_prompt"
        system_prompt = st.sidebar.text_area("System Prompt", value=self.config[prompt_mode]['value'], help=self.config['system_prompt']['help'])
        st.session_state.system_prompt = system_prompt
        return system_prompt
    
    def update_max_tokens(self, cot_reflection):
        max_tokens_settings = self.config['max_tokens_slider'] if not cot_reflection else self.config['max_tokens_slider_cot_reflection']
        max_tokens = st.sidebar.slider("Max Tokens", **max_tokens_settings)
        return max_tokens
    
    def set_parameters(self):
        parameters = {}
        if st.sidebar.toggle("Add more parameters"):
            for param, settings in self.config['additional_parameters'].items():
                if 'slider' in settings:
                    parameters[param] = st.sidebar.slider(settings['label'], **settings['slider'])
                elif 'input' in settings:
                    parameters[param] = st.sidebar.text_input(settings['label'], **settings['input'])
        return parameters

    def create_chat_interface(self, chatbot_manager, pdf_manager, model, system_prompt, temperature, max_tokens, cot_reflection, show_cot_process, reset_conversation, parameters):
        
        if reset_conversation:
            st.session_state.messages = []
        
        # Add system prompt to messages
        if not st.session_state.messages or st.session_state.messages[0]["role"] != "system" or st.session_state.messages[0]["content"] != system_prompt:
            if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
                st.session_state.messages[0] = {"role": "system", "content": system_prompt}
            else:
                st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Get user input
        if prompt := st.chat_input("Ask me anything"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get chatbot response
            try:
                response = pdf_manager.query_pdf(chatbot_manager, model, prompt, temperature)
            except ValueError:
                response = chatbot_manager.get_response(model, st.session_state.messages, temperature, max_tokens, cot_reflection, show_cot_process, **parameters)

            
            # Display chatbot response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.005)
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    def create_file_uploader(self, sidebar=False):
        st_component = st.sidebar if sidebar else st
        
        with st_component.expander("📄 Upload your files into the database", expanded=False):
            uploaded_files = st_component.file_uploader("Choose files", 
                                                        type=["pdf", "docx", "mp3", "wav"], 
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

    def display_database(self, sidebar=False):
        st_component = st.sidebar if sidebar else st

        if st.session_state.external_database: 
            pass
        else : 
            with st_component.expander("No external database linked."):
                pass

        if st.session_state.database:
            st.write(f"Current database size: {len(st.session_state.database)}")
            with st_component.expander("Database content", icon="📚", expanded=True):
                for file in st.session_state.database:
                    file_type = file['type'].lower()
                    icon = self.config['file_icons'].get(file_type, '📄')
                    st.write(f"{icon} {file['name']} ({file_type})")
        else:
            st.write("No files in the database.")