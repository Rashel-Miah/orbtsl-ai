import streamlit as st 
import json
import os
from typing import List, Dict
#from sentence_transformers import SentenceTransformer
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

EXAMPLE_PATH = "data/examples.json"

DEFAULT_EXAMPLES = [
    {"input": "List all users.", "query": "SELECT * FROM users"},
    {
        "input": "how many open outsource work orders are there?",
        "query": "SELECT Count(*) FROM vw_outsource_workorder WHERE open_status = 'Y'",
    },
    {
        "input": "how many close outsource work orders are there?",
        "query": "SELECT Count(*) FROM vw_outsource_workorder WHERE close_status = 'Y'",
    },
    {
        "input": "how many transfer outsource work orders are there?",
        "query": "SELECT Count(*) FROM vw_outsource_workorder WHERE transfer_status = 'Y'",
    },
    {
        "input": "what is the total outstanding?",
        "query": "SELECT Sum(Total_Outstanding) FROM vw_employee_outstanding",
    },
    {
        "input": "what is the total outstanding for D05468?",
        "query": "SELECT Sum(Total_Outstanding) FROM vw_employee_outstanding Where employee_code = 'D05468'",
    },
    {
        "input": "Show the total collection amount.",
        "query": "SELECT SUM(amount) FROM vw_taxi_collection",
    },
    {
        "input": "What is the today's total collection amount.",
        "query": "SELECT SUM(amount) FROM vw_taxi_collection where paid_date = trunc(sysdate)",
    },
    {
        "input": "Show the total cc amount.",
        "query": "SELECT SUM(credit_card_amount) FROM vw_taxi_collection",
    },
]

def load_examples() -> List[Dict[str, str]]:
    if not os.path.exists(EXAMPLE_PATH):
        save_examples(DEFAULT_EXAMPLES)
    with open(EXAMPLE_PATH, "r") as f:
        return json.load(f)

def save_examples(examples: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(EXAMPLE_PATH), exist_ok=True)
    with open(EXAMPLE_PATH, "w") as f:
        json.dump(examples, f, indent=2)

def add_example(input_text: str, query_text: str):
    examples = load_examples()
    examples.append({"input": input_text, "query": query_text})
    save_examples(examples)

def get_embedding_model():
    #return SentenceTransformer(st.secrets.model.model_name)
    return HuggingFaceEmbeddings(model_name=st.secrets.model.model_name,model_kwargs={'device': 'cpu'})