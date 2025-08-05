from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

def add_to_memory(user_input, ai_output):
    memory.chat_memory.add_user_message(HumanMessage(content=user_input))
    memory.chat_memory.add_ai_message(AIMessage(content=ai_output))

def get_chat_history():
    return memory.load_memory_variables({})["chat_history"]