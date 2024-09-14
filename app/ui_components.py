import streamlit as st
import time

def create_sidebar(config):
    st.sidebar.title("Powered by AIugustin")
    model = st.sidebar.selectbox("Select a model", options=config['models'])
    temperature = st.sidebar.slider("Temperature", **config['temperature_slider'])
    system_prompt = st.sidebar.text_area("System Prompt", **config['system_prompt'])
    reset_conversation = st.sidebar.button("Reset Conversation")
    
    parameters = {}
    if st.sidebar.toggle("Add more parameters"):
        for param, settings in config['additional_parameters'].items():
            parameters[param] = st.sidebar.slider(settings['label'], **settings['slider'])
    
    return model, temperature, system_prompt, reset_conversation, parameters

def create_chat_interface(chatbot_manager, model, temperature, system_prompt, reset_conversation, parameters):
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