from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

#connection_uri = "oracle+cx_oracle://aitest:aitest@localhost:1521?service_name=orcl.amernitech.com"
#db = SQLDatabase.from_uri(connection_uri, view_support=True)

#print(db.dialect)
#print(db.get_usable_table_names())
#db.run("SELECT COUNT(*) FROM vw_outsource_workorder WHERE open_status = 'Y'")

# Defining llm
#llm = ChatOllama(
    #model='qwen2.5-coder:7b',
    #temperature=0.3,
    #base_url="http://localhost:11434",	
#)

def run_bot(llm, db, username, user_input):

    class State(TypedDict):
        question: str
        query: str
        result: str
        answer: str

    system_message = """
    Given an input question, create a syntactically correct {dialect} query to
    run to help find the answer. Unless the user specifies in his question a
    specific number of examples they wish to obtain, always limit your query to
    at most {top_k} results. You can order the results by a relevant column to
    return the most interesting examples in the database.

    Never query for all the columns from a specific table, only ask for a the
    few relevant columns given the question.

    Pay attention to use only the column names that you can see in the schema
    description. Be careful to not query for columns that do not exist. Also,
    pay attention to which column is in which table.
    Pay attention to use TRUNC(SYSDATE) function to get the current date, if the question involves "today".

    Do not add semicolon at the end of generated query. Remove the semicolon if already there. 

    Only use the following tables:
    {table_info}
    """

    user_prompt = "Question: {input}"

    query_prompt_template = ChatPromptTemplate(
        [("system", system_message), ("user", user_prompt)]
    )

    #for message in query_prompt_template.messages:
    #    message.pretty_print()

    class QueryOutput(TypedDict):
        """Generated SQL query."""

        query: Annotated[str, ..., "Syntactically valid SQL query."]


    def write_query(state: State):
        """Generate SQL query to fetch information."""
        prompt = query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"].rstrip(",;")} 

    def execute_query(state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def generate_answer(state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    memory = MemorySaver()

    graph_builder = StateGraph(State).add_sequence(
        [write_query, execute_query, generate_answer]
    )
    graph_builder.add_edge(START, "write_query")
    graph = graph_builder.compile(checkpointer=memory)

    # Now that we're using persistence, we need to specify a thread ID
    # so that we can continue the run after review.

    config = {"configurable": {"thread_id": username}}

    response = graph.invoke({"question": user_input},config=config)
    
    return response['answer']

    #for step in graph.stream(
        #{"question": user_input}, stream_mode="updates", config=config
    #):
        #print(step)

# run_bot(llm,db,'rashel',"How many closed outsource workorders are there?")

#print(db.run("SELECT COUNT(*) FROM vw_outsource_workorder WHERE close_status = 'Y'"))