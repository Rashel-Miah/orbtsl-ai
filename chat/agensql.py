from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
import cx_Oracle

connection_uri = "oracle+cx_oracle://aitest:aitest@localhost:1521?service_name=orcl.amernitech.com"
db = SQLDatabase.from_uri(connection_uri, view_support=True)

llm = ChatOllama(
	model='qwen2.5-coder:7b',
	temperature=0.7,
	base_url="http://localhost:11434",	
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific views,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the views in the database to see what you
can query. All the view name is prefix by vw_.
Do NOT skip this step.

Then you should query the schema of the most relevant views.
""".format(
    dialect=db.dialect,
    top_k=5,
)

agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
)

question = "How many workorders are open?"


for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    print(step["messages"][-1].content)
    