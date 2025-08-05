import streamlit as st
import re, sys, ollama
from chat.utils.schema_store import build_or_load_schema_store
from chat.utils.example_store import build_or_load_example_selector
from chat.utils.langgraph_chain import get_sql_chain
#from chat.helper.chat_memory import add_to_memory, get_chat_history


st.set_page_config(page_title="Orbits Assistant")
#st.header("Orbits :blue[Assistant]")

def get_models():
	models = ollama.list()
	if not models:
		st.write("No models found.")
		sys.exit(1)
	model_list = []
	for model in models["models"]:		
		model_list.append(re.sub(r':latest$', '', model["model"]))
	return model_list

col1, col2 = st.columns(2)
with col1:
     st.header("Orbits :green[Chat] :blue[Assistant]")
     #st.write(f"Your unique session ID is: {st.session_state.thread_id}")

with col2:
     selected_model = st.selectbox("Choose Model",get_models(), index=2)
     st.session_state.llm_model = selected_model

# Initialize the chat history in Session state
#if "chat_history" not in st.session_state:
    #st.session_state.chat_history = []

# Initialize the chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize the llm model
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = selected_model

# Display chat messages history on app run
for message in st.session_state.messages:
 
    #with st.chat_message(message["role"], avatar="static/user_icon.png" if message["role"] == "user" else "static/ai_icon.png"):
    #with st.chat_message(message["role"], avatar=None):
        #st.markdown(message["content"])
    div = f"""
    <div class="chat-row 
        {'' if message["role"] == 'user' else 'row-reverse'}">
        <img class="chat-icon" src="app/static/{
            'user_icon.png' if message["role"] == 'user' 
                        else 'ai_icon.png'}"
            width=32 height=32>
        <div class="chat-bubble
        {'human-bubble' if message["role"] == 'user' else 'ai-bubble'}">
            &#8203;{message["content"]}
        </div>
    </div>
            """
    st.markdown(div,unsafe_allow_html=True)

config = {"configurable": {"thread_id": st.session_state.thread_id}}

#user_input = st.chat_input("Ask a question about your database...")
if user_input := st.chat_input("Ask a question about your database..."):
    user_input = re.sub(r"^```sql\\n?|```$", "", user_input.strip(), flags=re.IGNORECASE | re.MULTILINE)
    # Display user message in chat message container
    #st.chat_message("user", avatar="static/user_icon.png").markdown(user_input)
    divui = f"""
    <div class="chat-row">
        <img class="chat-icon" src="app/static/user_icon.png"
            width=32 height=32>
        <div class="chat-bubble human-bubble">
            &#8203;{user_input}
        </div>
    </div>
            """
    st.markdown(divui,unsafe_allow_html=True)

    # Add user message to chat history
    st.session_state.messages.append({"role":"user", "content":user_input})    

    # Load resources
    schema_vectorstore = build_or_load_schema_store(False)
    schema_docs = schema_vectorstore.similarity_search(user_input, k=3)
    schema_hint = "\n".join([doc.page_content for doc in schema_docs])

    example_selector = build_or_load_example_selector(k=3,force_rebuild=False)
    similar_examples = example_selector.invoke(user_input)
    few_shot = [{"input": d.page_content, "query": d.metadata["query"]} for d in similar_examples]
    
    # LangGraph SQL generator
    chain = get_sql_chain()
    result = chain.invoke({"question": user_input, "schema": schema_hint, "examples": few_shot}, config=config)

    # Execute SQL
    answer = result["answer"]

    divar = f"""
    <div class="chat-row row-reverse">
        <img class="chat-icon" src="app/static/ai_icon.png"
            width=32 height=32>
        <div class="chat-bubble ai-bubble">
            &#8203;{answer}
        </div>
    </div>
            """
    st.markdown(divar,unsafe_allow_html=True)

    st.session_state.messages.append({"role":"assistant", "content":answer})