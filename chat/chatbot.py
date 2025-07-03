import streamlit as st 
import ollama
import re, sys
import time, random
from langchain_ollama import ChatOllama


st.set_page_config(page_title="Chat Assistant")
st.header("Chat :blue[Assistant]")

def get_models():
	models = ollama.list()
	if not models:
		st.write("No models found.")
		sys.exit(1)
	model_list = []
	for model in models["models"]:		
		model_list.append(re.sub(r':latest$', '', model["model"]))
	return model_list

selected_model = st.selectbox("Choose Model",get_models(), index=2)

llm_engine = ChatOllama(
	model=selected_model,
	temperature=0.3,
	base_url="http://localhost:11434",	
)

def response_generator():
    response = random.choice([
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",    
    ])

    for word in response.split():
        yield word + " "
        time.sleep(0.5)

# Initialize the chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages history on app run
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="static/user_icon.png" if message["role"] == "user" else "static/ai_icon.png"):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input("whats up?", key="chatinput"):
    # Add user message to chat history
    st.session_state.messages.append({"role":"user", "content":prompt})

    # Display user message in chat message container
    st.chat_message("user", avatar="static/user_icon.png").markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="static/ai_icon.png"):
        response = st.write_stream(llm_engine.stream(prompt))
        # Add assistant response to chat history
        st.session_state.messages.append({"role":"assistant", "content":response})

