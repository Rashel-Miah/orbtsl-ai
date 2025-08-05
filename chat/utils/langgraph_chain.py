from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph
from langchain_ollama import ChatOllama
from chat.utils.prompt_utils import build_prompt,db_keywords,general_keywords,intent_prompt
from chat.utils.check_query_prompt import check_query_prompt
from typing_extensions import TypedDict
import re, streamlit as st 
from chat.utils.oracle_connector import execute_query
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.tools import DuckDuckGoSearchRun

llm = ChatOllama(model=st.session_state.llm_model, temperature=0.1,base_url="http://localhost:11434")

class State(TypedDict):
    question: str
    schema: str
    examples: str
    sql: str
    result:str
    answer:str
    db_success:bool

def clean_sql_response(response):
    if hasattr(response, "content"):
        content = response.content
    else:
        content = str(response)

    # Remove markdown code fences and whitespace
    content = re.sub(r"^```sql\\n?|```$", "", content.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return content.strip()

memory = InMemorySaver()

general_search_patterns = [
    r"\b(who (is|was)|what (is|are)|when (is|did)|where (is|was)|latest|news|current|define|meaning of|top \d+)\b",
    r"\b(how to|how does|how do)\b",
]

search_tool = DuckDuckGoSearchRun()

general_search_patterns = [
    r"\b(who (is|was)|what (is|are)|when (is|did)|where (is|was)|latest|news|current|define|meaning of|top \d+)\b",
    r"\b(how to|how does|how do)\b",
]

def get_sql_chain():
    def classify_intent(state):
        question = state["question"]
        # 1. Fast regex-based intent detection
        if any(re.search(p, question) for p in db_keywords):
            return {"intent": "db"}
        if any(re.search(p, question) for p in general_keywords):
            return {"intent": "general"}

        # 2. LLM-based fallback if regex is unsure
        try:
            response = llm.invoke(intent_prompt(question))
            label = response.content.strip().lower()
            if label not in ["db", "general"]:
                raise ValueError("Invalid label from LLM")
            return {"intent": label}
        except Exception as e:
            # 3. Fallback if everything fails
            print(f"[Intent Classification Fallback] {e}")
            return {"intent": "general"}
    
        #response = llm.invoke(intent_prompt)
        #label = response.content.strip().lower()
        #return {"intent": "general" if "general" in label else "db"}

    def answer_general(state):
        question = state["question"]

        # Check if it matches "web-worthy" patterns
        if any(re.search(p, question, re.IGNORECASE) for p in general_search_patterns):
            try:
                search_result = search_tool.run(question)
                if search_result and "no good" not in search_result.lower():
                    # Optionally refine the search result with the LLM
                    prompt = f"""User asked: "{question}"

                    DuckDuckGo search returned:
                    {search_result}

                    Please give a concise, helpful answer to the user based on this search result."""
                    response = llm.invoke(prompt)
                    return {"answer": response.content}
            except Exception as e:
                print(f"[DuckDuckGo Error] {e}")

        # Fallback to LLM (chit-chat, etc.)
        response = llm.invoke(question)
        return {"answer": response.content}

    #def answer_general(state):
        #question = state["question"]
        #response = llm.invoke(question)
        #return {"answer": response.content}
    
    def generate_sql(state):
        """Generate the query using retrieved information as context."""
        question = state["question"]
        schema_hints = state["schema"]
        examples = state["examples"]
        prompt = build_prompt(schema_hints, examples, question)
        sql = llm.invoke(prompt)
        sql = clean_sql_response(sql)
        print(sql)
        return {"question": question, "sql": sql}

    def recheck_sql(state):
        """Re-check the query using retrieved information as context."""
        question = state["question"]
        query = state["sql"]
        schema_hints = state["schema"]
        prompt = check_query_prompt(schema_hints, query)        
        sql = llm.invoke(prompt)
        sql = clean_sql_response(sql)        
        return {"question": question, "sql": sql}
        
    def run_the_query(state):
        """Run the query using retrieved information as context."""
        try:
            result = execute_query(state["sql"])
            if not result:
                return {"result": "NO_RESULT", "db_success": False}
            return {"result": result, "db_success": True}
        except Exception as e:
            print(f"[SQL Execution Error] {e}")
            return {"result": "SQL_ERROR", "db_success": False}

    def answer_from_sql(state):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["sql"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    def answer_from_fallback(state):
        fallback_prompt = (
            f"""The SQL query could not return a valid result.\n\n"""
            f"""Question: {state["question"]}\n"""
            f"""Generated SQL: {state["sql"]}\n"""
            f"""Result: {state["result"]}\n\n"""
            f"""Please try to answer the user's question based on the question and query context, or politely explain that the data is unavailable."""
        )
        response = llm.invoke(fallback_prompt)
        return {"answer": response.content}
            
    def generate_answer(state):
        
        """Answer question using retrieved information as context."""

        if state["result"] in ["NO_RESULT", "SQL_ERROR"]:
            fallback_prompt = (
                f"""The SQL query could not return a valid result.\n\n"""
                f"""Question: {state["question"]}\n"""
                f"""SQL Query: {state["sql"]}\n"""
                f"""SQL Result: {state["result"]}\n\n"""
                f"""Please try to answer the user's question based on the question and query context, or politely explain that the data is unavailable."""
            )
            response = llm.invoke(fallback_prompt)
            return {"answer": response.content}
        
        # Normal flow if SQL result is valid

        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["sql"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}
    
    builder = StateGraph(State)

    # Step 1: classify question type
    builder.add_node("ClassifyIntent", RunnableLambda(classify_intent))

    # Step 2a: general chat response
    builder.add_node("AnswerGeneral", RunnableLambda(answer_general))
    
    # Step 2b onward: DB-related question flow    
    builder.add_node("GenerateSQL", RunnableLambda(generate_sql))
    builder.add_node("RunSQL", RunnableLambda(run_the_query))
    #builder.add_node("GenerateAnswer", RunnableLambda(generate_answer))
    builder.add_node("AnswerFromSQL", RunnableLambda(answer_from_sql))
    builder.add_node("AnswerFromFallback", RunnableLambda(answer_from_fallback))    

    # Flow routing
    builder.set_entry_point("ClassifyIntent")
    builder.add_conditional_edges(
        "ClassifyIntent",
        lambda state: state["intent"],
        {
            "general": "AnswerGeneral",
            "db": "GenerateSQL",
        },
    )
    builder.add_edge("GenerateSQL", "RunSQL")

    builder.add_conditional_edges(
        "RunSQL",
        lambda state: "AnswerFromSQL" if state.get("db_success") else "AnswerFromFallback",
        {
            "AnswerFromSQL": "AnswerFromSQL",
            "AnswerFromFallback": "AnswerFromFallback",
        }
    )

    #builder.add_edge("RunSQL", "GenerateAnswer")
    builder.add_edge("AnswerGeneral", END)    
    builder.add_edge("AnswerFromSQL", END)
    builder.add_edge("AnswerFromFallback", END)    
    #builder.add_edge("GenerateAnswer", END)
    return builder.compile(checkpointer=memory)