import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import time

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

client = Groq(api_key=GROQ_API_KEY)

def chatbot_response(model, messages, temperature, max_tokens=None, top_p=None, frequency_penalty=None, presence_penalty=None, stop=None):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
    )
    return response.choices[0].message.content

st.logo("img/logo-Cyy6uKYt.png")

# Sidebar section
st.sidebar.title("Powered by AIugustin")
model = st.sidebar.selectbox("Select a model", options=['gemma2-9b-it', 'gemma-7b-it', 'llama3-70b-8192', 'llama3-8b-8192', 'llama3-groq-70b-8192-tool-use-preview', 'llama3-groq-8b-8192-tool-use-preview', 'mixtral-8x7b-32768'])
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1, help="Controls the randomness of the model's responses. A value of 0 means that the model will always choose the most likely response, while a value of 1 means that the model will choose a response randomly from the distribution of possible responses.")
system_prompt = st.sidebar.text_area("System Prompt", value="You are a helpful assistant.", height=100, help="Sets the context and behavior for the conversation. Helps the chatbot understand how to respond to your messages. Customize this prompt to suit your needs.")
reset_conversation = st.sidebar.button("Reset Conversation")
parameters = {}
if st.sidebar.toggle("Add more parameters"):
    parameters["max_tokens"] = st.sidebar.slider("Max Tokens", min_value=1, max_value=4096, value=512, step=1, help="This parameter allows you to set the maximum number of tokens that the model can generate in a single response. This can help prevent the model from generating overly long responses and can also help to save on API costs.")
    parameters["top_p"] = st.sidebar.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.1, help="This parameter allows you to set the probability threshold for generating a response. A value of 0.5 means that the model will consider the top 50% of the most likely tokens when generating a response. This can help to balance between diversity and coherence in the model's responses.")
    parameters["frequency_penalty"] = st.sidebar.slider("Frequency Penalty", min_value=0.0, max_value=2.0, value=0.0, step=0.1, help="This parameter allows you to penalize the model for repeating the same words or phrases in a response. A value of 0.5 means that the model will be less likely to repeat the same words or phrases, while a value of 0 means that the model will not be penalized for repetition.")
    parameters["presence_penalty"] = st.sidebar.slider("Presence Penalty", min_value=0.0, max_value=2.0, value=0.0, step=0.1, help="This parameter allows you to penalize the model for using words or phrases that have already been used in the conversation. A value of 0.5 means that the model will be less likely to use the same words or phrases, while a value of 0 means that the model will not be penalized for reusing words or phrases.")
    parameters["stop"] = st.sidebar.text_input("Stop Sequences", value="", help="This parameter allows you to specify a list of sequences that the model should stop generating a response when it encounters. This can be useful for preventing the model from generating responses that are too long or that are not relevant to the user's query.")
    
# Reset conversation history when the button is clicked
if reset_conversation:
    st.session_state.messages = []

st.title("ChatBot")
st.markdown("Nice to see you again!")

# Initialize a history for the chat
if "messages" not in st.session_state:
    st.session_state.messages = []
st.session_state.messages.append({"role": "system", "content": system_prompt})

# Display chat messages from history when the application is restarted
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user prompt
if prompt := st.chat_input("Tell me more about Vincent's muscles"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    if not parameters : 
        answer = chatbot_response(model, st.session_state.messages, temperature)
    else : 
        answer = chatbot_response(model, st.session_state.messages, temperature, **parameters)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Simulate stream of response with milliseconds delay
        for chunk in answer:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.005)
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
            