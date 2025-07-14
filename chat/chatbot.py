import streamlit as st 
from langchain_community.utilities import SQLDatabase
import ollama
import re, sys
import time, random
from langchain_ollama import ChatOllama
from chat.chatmodel_v1 import run_bot


st.set_page_config(page_title="Orbits Assistant")
st.header("Orbits :blue[Assistant]")

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

# Initialize the chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'db' not in st.session_state:
     connection_uri = f"oracle+cx_oracle://{st.secrets.db_credentials.user}:{st.secrets.db_credentials.password}@{st.secrets.db_credentials.hostport}?service_name={st.secrets.db_credentials.srvcname}"
     st.session_state.db = SQLDatabase.from_uri(connection_uri, view_support=True)
     
     st.session_state.llm_engine = ChatOllama(
          model=selected_model,
          temperature=0.3,
          base_url="http://localhost:11434",	
    )   
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
        # response = st.write_stream(llm_engine.stream(prompt))
        response = st.write(run_bot(st.session_state.llm_engine,st.session_state.db,'rashel', prompt))
        print(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role":"assistant", "content":response})


