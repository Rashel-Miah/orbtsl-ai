SMART_PROMPT_TEMPLATE = """
You are an expert Oracle SQL assistant.
Given the database relevant schema, relevant examples and a user question, write a syntactically correct ORACLE query to run.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. 
If needed wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention on the length of column alias is not more than 25 characters.
Be careful to not query for columns that do not exist. Also, pay attention to which column is in which schema.
Pay attention to use TRUNC(SYSDATE) function to get the current date, if the question involves "today".
Pay attention to use capital letter character in the value of where condition.
Pay attention to use 'Y' as value if any column suffix is status in the where condition, and do not use any columns in where condition that do not exist.
Pay attention to use only the column names you can see in the schemas below in select clause, where clause, having clause and order by clause. 
Do not add the (;) semicolon at the end of the query.
Pay attention not to use any currency symbol.
Pay attention to use relevant schemas and relevant examples to learn the query.
Do not break down the sql query result, just answer the query result in a nice sentence.
Always see the relevant schema details to validate the query column names.

Respond with only a valid SQL statement. Do not include any explanations or formatting.

Relevant Schema:
{schema_hints}

Relevant Examples:
{examples}

Question: {question}

"""
#{suffix}
def build_prompt(schema_hints: str, examples: list, question: str) -> str:
    formatted_examples = "\n".join(
        [f"Q: {ex['input']}\nA: {ex['query']}" for ex in examples]
    )
    return SMART_PROMPT_TEMPLATE.format(
        schema_hints=schema_hints,
        examples=formatted_examples,
        question=question,
        #suffix=PROMPT_SUFFIX
    )

## For intent promting

# 1. Fast regex-based intent detection
db_keywords = [
    r"\b(select|list|show|get|count|find|display|total|number of|how many|active|open|pending|where|from)\b"
]
general_keywords = [
    r"\b(hi|hello|thanks|thank you|how are you|who are you|what's your name|good morning|good evening|bye|who made you)\b"
]

# 2. LLM-based fallback if regex is unsure
def intent_prompt(question):
    return f"""
        You are an AI classifier. Classify the user's message into one of the following intents:

        - "db" → if the input asks for data, counts, filters, reports, or anything that would require querying a database.
        - "general" → if the input is a greeting, personal question, chit-chat, or anything that does not require data from a database.

        Respond with just one word: db or general.
        ### Examples:

        User: "How many open outsource workorders are there?"
        Intent: db

        User: "Show me total taxi revenue of last month"
        Intent: db

        User: "What is the total outstanding of the employee 'D904961'?"
        Intent: db

        User: "Hello!"
        Intent: general

        User: "Who made you?"
        Intent: general

        User: "Thanks!"
        Intent: general

        User: "What's your name?"
        Intent: general

        User input: "{question}"
        Answer:"""