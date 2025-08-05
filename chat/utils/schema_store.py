import os
import asyncio
import streamlit as st
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from chat.utils.oracle_connector import init_pool
from shutil import rmtree

#from sentence_transformers import SentenceTransformer


SCHEMA_INDEX_PATH = "data/schema_store.faiss"

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbeddings(model_name=st.secrets.model.model_name,model_kwargs={'device': 'cpu'})

def fetch_schema_docs() -> List[Document]:
    pool = init_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT table_name, column_name FROM user_tab_columns where table_name not in ('VW_USERINFO','VW_USER_MENU','VW_USER_PROGRAM','USERS','ADD_EXAMPLES','NEW_VIEW_ADD') ORDER BY table_name")
            rows = cursor.fetchall()
            grouped = {}
            for table, column in rows:
                grouped.setdefault(table, []).append(column)
            return [Document(page_content=f"Table {t}: {', '.join(cols)}") for t, cols in grouped.items()]

def fetch_newly_added_schema_docs() -> List[Document]:
    pool = init_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT table_name, column_name FROM user_tab_columns where table_name in (SELECT VIEW_NAME FROM NEW_VIEW_ADD WHERE NEW_FLAG = 'Y') ORDER BY table_name")
            rows = cursor.fetchall()
            grouped = {}
            for table, column in rows:
                grouped.setdefault(table, []).append(column)
            return [Document(page_content=f"Table {t}: {', '.join(cols)}") for t, cols in grouped.items()]
        
@st.cache_resource
def build_or_load_schema_store(force_rebuild: bool = False):
    if force_rebuild or not os.path.exists(SCHEMA_INDEX_PATH):
        if os.path.exists(SCHEMA_INDEX_PATH):
            rmtree(SCHEMA_INDEX_PATH)
        schema_docs = fetch_schema_docs()
        db = FAISS.from_documents(schema_docs, load_embedding_model())
        db.save_local(SCHEMA_INDEX_PATH)
        return db
    else:
        return FAISS.load_local(SCHEMA_INDEX_PATH, load_embedding_model(), allow_dangerous_deserialization=True)
