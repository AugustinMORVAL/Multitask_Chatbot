import streamlit as st
import time

st.set_page_config(initial_sidebar_state="collapsed")

def create_sidebar(config):
    st.sidebar.title("Powered by AIugustin")
    model = st.sidebar.selectbox("Select a model", options=config['models'])
    temperature = st.sidebar.slider("Temperature", **config['temperature_slider'])
    system_prompt = st.sidebar.text_area("System Prompt", **config['system_prompt'])
    reset_conversation = st.sidebar.button("Reset Conversation")
    
    parameters = {}
    if st.sidebar.toggle("Add more parameters"):
        for param, settings in config['additional_parameters'].items():
            if 'slider' in settings:
                parameters[param] = st.sidebar.slider(settings['label'], **settings['slider'])
            elif 'input' in settings:
                parameters[param] = st.sidebar.text_input(settings['label'], **settings['input'])
    
    return model, temperature, system_prompt, reset_conversation, parameters

def create_chat_interface(chatbot_manager, pdf_manager, model, temperature, system_prompt, reset_conversation, parameters):
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Reset conversation if button is clicked
    if reset_conversation:
        st.session_state.messages = []
    
    # Add system prompt to messages
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
    
    # Display chat messages
    for message in st.session_state.messages[1:]:  # Skip system message
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
            response = chatbot_manager.get_response(model, st.session_state.messages, temperature, **parameters)
        
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

def create_file_uploader():
    file_data = None
    audio_data = None

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Upload files📄"):
            uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"], label_visibility="collapsed")
            if uploaded_file is not None:
                file_contents = uploaded_file.read()
                st.success(f"'{uploaded_file.name}' uploaded!")
                file_data = {"type": "file", "content": file_contents, "name": uploaded_file.name}

    with col2:
        with st.expander("Upload audio🎵"):
            audio_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "ogg"], label_visibility="collapsed")
            if audio_file is not None:
                audio_contents = audio_file.read()
                st.success(f"'{audio_file.name}' uploaded!")
                st.audio(audio_contents, format=f"audio/{audio_file.name.split('.')[-1]}")
                audio_data = {"type": "audio", "content": audio_contents, "name": audio_file.name}

    return file_data, audio_data