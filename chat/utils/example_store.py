import os
import streamlit as st
from chat.utils.examples import load_examples, get_embedding_model
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.prompts.example_selector.semantic_similarity import SemanticSimilarityExampleSelector
from shutil import rmtree

EXAMPLE_INDEX_PATH = "data/example_store.faiss"

@st.cache_resource
def build_or_load_example_selector(k=3, force_rebuild: bool = False) -> SemanticSimilarityExampleSelector:
    model = get_embedding_model()
    if force_rebuild or not os.path.exists(EXAMPLE_INDEX_PATH):
        if os.path.exists(EXAMPLE_INDEX_PATH):
            rmtree(EXAMPLE_INDEX_PATH)
        examples = load_examples()
        docs = [Document(page_content=ex["input"], metadata={"query": ex["query"]}) for ex in examples]
        db = FAISS.from_documents(docs, model)
        db.save_local(EXAMPLE_INDEX_PATH)
        return db.as_retriever(search_kwargs={"k": k})            
    else:
        return FAISS.load_local(EXAMPLE_INDEX_PATH, model, allow_dangerous_deserialization=True).as_retriever(search_kwargs={"k": k})
